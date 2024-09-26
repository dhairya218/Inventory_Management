from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from .models import CustomUser, ProductList, ProductStock, ProductHistory, Unit
from .forms import ProductForm, UserForm, UnitForm
from django.views.generic import CreateView
from django.http import JsonResponse
from django.contrib import messages
from .forms import UserEditForm
from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.db.models import Sum
from datetime import timedelta
from django.views.generic import TemplateView
from django.urls import reverse
from django.http import HttpResponse
from django.utils import timezone
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from reportlab.pdfgen import canvas
from datetime import datetime
from django.template.loader import render_to_string
import logging
from django.core.files.storage import FileSystemStorage
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.core.files.storage import default_storage
from django import forms
from django.views.generic.edit import FormView


class UnitView(View):
    def get(self, request, *args, **kwargs):
        units = Unit.objects.all()
        context = {
            'units': units,
        }
        return render(request, 'unit-list.html', context)

    def post(self, request, *args, **kwargs):
        unit_name = request.POST.get('unit_name')
        if unit_name:
            Unit.objects.create(unit_name=unit_name)
        return redirect('units') 


class ProfileView(View):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        user_form = UserEditForm(instance=request.user)
        return render(request, 'profile.html', {
            'user_form': user_form,
        })

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        user_form = UserEditForm(request.POST, instance=request.user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, 'profile.html', {
            'user_form': user_form,
        })
    

class DashbView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        total_products = ProductList.objects.count()

        today = datetime.date.today()
        total_buys_today = ProductHistory.objects.filter(transaction_type='buy', created_date=today).aggregate(total_buys=Sum('quantity'))['total_buys'] or 0

        total_sells_today = ProductHistory.objects.filter(transaction_type='sell', created_date=today).aggregate(total_sells=Sum('quantity'))['total_sells'] or 0

        context['total_products'] = total_products
        context['total_buys_today'] = total_buys_today
        context['total_sells_today'] = total_sells_today

        return context


class DashboardView(View):
    def get(self, request):
        products = ProductStock.objects.all()
        product_names = [product.product.product_name for product in products]
        quantities = [product.stock_quantity for product in products]

        total_quantity = sum(quantities)

        context = {
            'product_names': product_names,
            'quantities': quantities,
            'total_quantity': total_quantity,
        }

        return render(request, 'dashboard.html', context)


class AddProductView(View):
    def get(self, request):
        form = ProductForm()
        return render(request, 'product-list.html', {'form': form, 'products': ProductList.objects.all()})

    def post(self, request):
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            quantity = form.cleaned_data.get('initial_quantity', 0.0)

            stock, created = ProductStock.objects.get_or_create(product=product)
            stock.stock_quantity += quantity
            stock.save()

            history = ProductHistory(product=product, transaction_type='buy', quantity=quantity)
            history.save()

            messages.success(request, 'Product added successfully.')
            return redirect('product-list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            return render(request, 'product-list.html', {
                'form': form, 
                'products': ProductList.objects.all(),
                'modal_open': True
            })


class ProductListView(View):
    def get(self, request):
        query = request.GET.get('q')
        sort_by = request.GET.get('sort_by', 'product_id')
        sort_order = request.GET.get('sort_order', 'asc')

        form = ProductForm()
        units = Unit.objects.all()  

        if query:
            if query.isdigit():
                product_list = ProductList.objects.filter(product_id=query)
            else:
                product_list = ProductList.objects.filter(product_name__icontains=query)
        else:
            product_list = ProductList.objects.all() 

        if sort_order == 'desc':
            sort_by = '-' + sort_by

        product_list = product_list.order_by(sort_by)

        paginator = Paginator(product_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        total_products = product_list.count()

        return render(request, 'product-list.html', {
            'form': form,
            'units': units,  
            'page_obj': page_obj,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'total_products': total_products
        })

    # def post(self, request):
    #     if 'action' in request.POST and request.POST['action'] == 'delete':
    #         product_ids = request.POST.getlist('product_ids')
    #         ProductList.objects.filter(id__in=product_ids).delete()
    #         return redirect('product-list')

    #     form = ProductForm(request.POST)
    #     if form.is_valid():
    #         product = form.save()
    #         quantity = form.cleaned_data['initial_quantity']

    #         stock, created = ProductStock.objects.get_or_create(product=product)
    #         if not created:
    #             stock.stock_quantity += quantity
    #             stock.save()
    #         else:
    #             stock.stock_quantity = quantity
    #             stock.save()

    #         ProductHistory.objects.create(
    #             product=product,
    #             transaction_type='buy',
    #             quantity=quantity
    #         )

    #         return redirect('product-list')

    #     product_list = ProductList.objects.all()
    #     units = Unit.objects.all()  
    #     paginator = Paginator(product_list, 10)
    #     page_number = request.GET.get('page')
    #     page_obj = paginator.get_page(page_number)

    #     total_products = product_list.count()

    #     return render(request, 'product-list.html', {
    #         'form': form,
    #         'units': units,  
    #         'page_obj': page_obj,
    #         'modal_open': True,
    #         'total_products': total_products
    #     })

    def post(self, request):
        if 'action' in request.POST and request.POST['action'] == 'delete':
            product_ids = request.POST.getlist('product_ids')
            ProductList.objects.filter(id__in=product_ids).delete()
            return redirect('product-list')

        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            quantity = form.cleaned_data['initial_quantity']

            stock, created = ProductStock.objects.get_or_create(product=product)
            if not created:
                stock.stock_quantity += quantity
                stock.save()
            else:
                stock.stock_quantity = quantity
                stock.save()

            ProductHistory.objects.create(
                product=product,
                transaction_type='buy',
                quantity=quantity
            )

            return redirect('product-list')
        else:
            product_list = ProductList.objects.all()  
            paginator = Paginator(product_list, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            return render(request, 'product-list.html', {
                'form': form,
                'units': Unit.objects.all(),
                'page_obj': page_obj,
                'modal_open': True  # This will keep the modal open if there are errors
            })



class DeactivateProductView(View):
    def post(self, request, product_id):
        product = get_object_or_404(ProductList, id=product_id)

        if product.is_active:
            product.is_active = False
            product.save()

            ProductStock.objects.filter(product=product).update(is_active=False)

        return redirect('product-list')


class ActivateProductView(View):
    def post(self, request, product_id):
        product = get_object_or_404(ProductList, id=product_id)
        
        if not product.is_active:
            product.is_active = True
            product.save()

            ProductStock.objects.filter(product=product).update(is_active=True)
        
        return redirect('product-list')


class ToggleProductStatusView(View):
    def post(self, request, product_id):
        # Fetch the product by ID
        product = get_object_or_404(ProductList, id=product_id)

        product.is_active = not product.is_active
        product.save()

        if product.is_active:
            pass

        return JsonResponse({'status': 'success', 'is_active': product.is_active})


class Index(View):
    def get(self, request):
        stock_threshold = request.GET.get('stockThreshold', request.session.get('low_stock_threshold', 100))
        request.session['low_stock_threshold'] = stock_threshold

        try:
            stock_threshold = int(stock_threshold)
        except ValueError:
            stock_threshold = 100

        total_products = ProductList.objects.count()
        low_stock_count = ProductStock.objects.filter(stock_quantity__lt=stock_threshold).count()

        today = now().date()

        total_buys = ProductHistory.objects.filter(transaction_type='buy', created_date__date=today).values('product_id').distinct().count()
        total_sells = ProductHistory.objects.filter(transaction_type='sell', created_date__date=today).values('product_id').distinct().count()

        last_7_days = [today - timedelta(days=i) for i in range(7)]
        dates = []
        buys = []
        sells = []
        for day in last_7_days:
            buys_on_day = ProductHistory.objects.filter(transaction_type='buy', created_date__date=day).values('product_id').distinct().count()
            sells_on_day = ProductHistory.objects.filter(transaction_type='sell', created_date__date=day).values('product_id').distinct().count()
            dates.append(day.strftime('%Y-%m-%d'))
            buys.append(buys_on_day)
            sells.append(sells_on_day)

        product_data = ProductList.objects.all()

        product_stock_data = []
        for product in product_data:
            stock = ProductStock.objects.filter(product_id=product).aggregate(
                total_stock=Sum('stock_quantity')
            )['total_stock'] or 0
            product_stock_data.append((product.product_name, stock))

        product_stock_data.sort(key=lambda x: x[1], reverse=True)
        top_products = product_stock_data[:7]
        other_stock = sum(stock for name, stock in product_stock_data[7:])
        top_products.append(("Other", other_stock))
        pie_chart_labels = [name for name, stock in top_products]
        pie_chart_data = [stock for name, stock in top_products]

        low_stock_product_data = []
        for product in product_data:
            stock = ProductStock.objects.filter(product_id=product).aggregate(
                total_stock=Sum('stock_quantity')
            )['total_stock'] or 0
            if stock < stock_threshold:
                low_stock_product_data.append((product.product_name, stock))
        low_stock_product_data.sort(key=lambda x: x[1])
        low_stock_labels = [name for name, stock in low_stock_product_data]
        low_stock_data = [stock for name, stock in low_stock_product_data]

        product_type_data = ProductList.objects.values('product_type').annotate(
            total_products=Sum('id')
        ).order_by('product_type')
        
        product_type_labels = [data['product_type'] for data in product_type_data]
        product_type_counts = [data['total_products'] for data in product_type_data]

        return render(request, 'index.html', {
            'total_products': total_products,
            'low_stock_count': low_stock_count,
            'total_buys': total_buys,
            'total_sells': total_sells,
            'dates': dates,
            'buys': buys,
            'sells': sells,
            'stock_threshold': stock_threshold,
            'pie_chart_data': pie_chart_data,
            'pie_chart_labels': pie_chart_labels,
            'low_stock_labels': low_stock_labels,
            'low_stock_data': low_stock_data,
            'product_type_labels':product_type_labels,
            'product_type_counts':product_type_counts,
        })

    def post(self, request):
        if 'low_stock_threshold' in request.POST:
            try:
                low_stock_threshold = int(request.POST.get('low_stock_threshold', 50))
                request.session['low_stock_threshold'] = low_stock_threshold
            except ValueError:
                request.session['low_stock_threshold'] = 50 

        return redirect('index')  


class Add_User(CreateView):
    model = CustomUser
    form_class = UserForm
    template_name = 'add_user.html'
    success_url = reverse_lazy('index')  

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return redirect(self.success_url)
    

class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email_or_phone = request.POST.get('email_or_phone')
        password = request.POST.get('password')

        user = self.authenticate_user(request, email_or_phone, password)

        if user is not None:
            login(request, user)
            return redirect('/') 
        return render(request, self.template_name, {'error': 'Invalid email or phone number and password'})

    def authenticate_user(self, request, email_or_phone, password):
        user = authenticate(request, email=email_or_phone, password=password)
        
        if user is None:
            try:
                user = CustomUser.objects.get(phone_number=email_or_phone)
                user = authenticate(request, username=user.email, password=password)
            except CustomUser.DoesNotExist:
                user = None
                
        return user


class ProductStockView(View):
    def get(self, request):
        query = request.GET.get('q')
        sort_by = request.GET.get('sort_by', 'product_id')
        sort_order = request.GET.get('sort_order', 'asc')
        stock_threshold = request.GET.get('stockThreshold')

        if sort_by not in ['product_id', 'product_name', 'stock_quantity']:
            sort_by = 'product_id'

        if request.GET.get('previous_sort_by') == sort_by:
            sort_order = 'desc' if sort_order == 'asc' else 'asc'
        else:
            sort_order = 'asc'

        if query:
            if query.isdigit():
                products = ProductList.objects.filter(product_id=query)  
            else:
                products = ProductList.objects.filter(product_name__icontains=query) 
        else:
            products = ProductList.objects.all()  

        stocks = ProductStock.objects.filter(product__in=products)

        if stock_threshold:
            try:
                stock_threshold = int(stock_threshold)
                stocks = stocks.filter(stock_quantity__lte=stock_threshold)
            except ValueError:
                stock_threshold = ''

        if sort_order == 'asc':
            stocks = stocks.order_by(sort_by)
        else:
            stocks = stocks.order_by(f'-{sort_by}')

        paginator = Paginator(stocks, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        low_stock_count = request.session.get('low_stock_count', 500)
        all_products = ProductList.objects.all()

        context = {
            'stocks': page_obj,
            'error_message': request.session.pop('error_message', None),
            'form_data': request.session.pop('form_data', None),
            'stock_threshold': stock_threshold,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'query': query,
            'previous_sort_by': sort_by,
            'all_products': all_products,
            'low_stock_count': low_stock_count,
        }
        return render(request, 'product-stock.html', context)

    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        transaction_type = request.POST.get('transaction_type')

        form_data = {
            'product_id': product_id,
            'quantity': quantity,
            'transaction_type': transaction_type,
        }

        if not quantity or float(quantity) <= 0:
            request.session['error_message'] = 'Quantity must be a positive number.'
            request.session['form_data'] = form_data
            return redirect('product-stock')

        quantity = float(quantity)
        product = get_object_or_404(ProductList, pk=product_id)

        stock, created = ProductStock.objects.get_or_create(product=product)

        if transaction_type == 'buy':
            stock.stock_quantity += quantity
        elif transaction_type == 'sell':
            if stock.stock_quantity < quantity:
                request.session['error_message'] = f'Insufficient stock. You have only {stock.stock_quantity:.2f} units left.'
                request.session['form_data'] = form_data
                return redirect('product-stock')
            stock.stock_quantity -= quantity

        stock.save()

        ProductHistory.objects.create(
            product=product,
            transaction_type=transaction_type,
            quantity=quantity
        )

        return redirect('product-stock')


class EditQuantityView(View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        history_id = request.POST.get('history_id')
        
        form_data = {
            'product_id': product_id,
            'quantity': quantity,
        }

        if not quantity or float(quantity) <= 0:
            request.session['error_message'] = 'Quantity must be a positive number.'
            request.session['form_data'] = form_data
            return redirect('product-stock')

        quantity = float(quantity)
        product = get_object_or_404(ProductList, pk=product_id)
        stock, created = ProductStock.objects.get_or_create(product=product)

        current_history_entry = ProductHistory.objects.filter(id=history_id).first()
        if current_history_entry:
            old_quantity = current_history_entry.quantity
        else:
            old_quantity = 0

        difference = quantity - old_quantity

        stock.stock_quantity += difference
        stock.save()

        if current_history_entry:
            current_history_entry.quantity = quantity
            current_history_entry.save()
        else:
            ProductHistory.objects.create(
                product=product,
                transaction_type='adjustment',
                quantity=quantity
            )

        return redirect('product-stock')


class ReturnQuantityView(View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        product_stock = ProductStock.objects.get(product_id=product_id)
        product_stock.stock_quantity += float(quantity)
        product_stock.save()

        ProductHistory.objects.create(
            product_id=product_id,
            transaction_type='return',
            quantity=float(quantity)
        )

        return JsonResponse({'status': 'success'})


class RecentBuyView(View):
    template_name = 'recent_buy.html'
    
    def get(self, request, *args, **kwargs):
        recent_buys = ProductHistory.objects.filter(transaction_type='buy').order_by('-created_at')
        return render(request, self.template_name, {'recent_buys': recent_buys})

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        product = ProductList.objects.get(id=product_id)
        ProductHistory.objects.create(
            product=product,
            transaction_type='buy',
            quantity=quantity
        )

        return redirect('recent-buy')


class RecentSellView(View):
    template_name = 'recent_sell.html'

    def get(self, request, *args, **kwargs):
        recent_sells = ProductHistory.objects.filter(transaction_type='sell').order_by('-created_at')
        return render(request, self.template_name, {'recent_sells': recent_sells})


class ProductHistoryView(View):
    
    def get(self, request):
        search_query = request.GET.get('search', '')
        sort_by = request.GET.get('sort_by', 'created_at')
        sort_order = request.GET.get('sort_order', 'asc')
        selected_product_id = request.GET.get('product_filter', '')

        order_by = sort_by if sort_order == 'asc' else '-' + sort_by

        history_list = ProductHistory.objects.all()

        if search_query:
            if search_query.isdigit():
                history_list = history_list.filter(product__product_id=search_query) 
            else:
                history_list = history_list.filter(Q(product__product_name__icontains=search_query)) 

        if selected_product_id:
            history_list = history_list.filter(product_id=selected_product_id)

        history_list = history_list.order_by(order_by)

        paginator = Paginator(history_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        all_products = ProductList.objects.all()

        context = {
            'history_list': page_obj,
            'search_query': search_query,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'all_products': all_products,
            'selected_product_id': selected_product_id,
        }
        return render(request, 'product-history.html', context)

    def post(self, request):
        product_id = request.POST.get('product_id')
        new_quantity = int(request.POST.get('product_quantity'))
        new_transaction_type = request.POST.get('transaction_type')
        history_id = request.POST.get('history_id', None)

        product = get_object_or_404(ProductList, id=product_id)
        product_stock, created = ProductStock.objects.get_or_create(product=product)

        if history_id:
            history_entry = get_object_or_404(ProductHistory, id=history_id)
            original_quantity = history_entry.quantity
            original_transaction_type = history_entry.transaction_type

            if original_transaction_type == 'sell':
                product_stock.stock_quantity += original_quantity
            elif original_transaction_type == 'buy':
                product_stock.stock_quantity -= original_quantity

            if new_transaction_type == 'sell':
                if new_quantity > product_stock.stock_quantity:
                    return self._render_error(request, "sell", new_quantity, product_stock.stock_quantity)
                product_stock.stock_quantity -= new_quantity
            elif new_transaction_type == 'buy':
                product_stock.stock_quantity += new_quantity

            history_entry.transaction_type = new_transaction_type
            history_entry.quantity = new_quantity
            history_entry.save()

        else:
            if new_transaction_type == 'sell':
                if new_quantity > product_stock.stock_quantity:
                    return self._render_error(request, "sell", new_quantity, product_stock.stock_quantity)
                product_stock.stock_quantity -= new_quantity
            elif new_transaction_type == 'buy':
                product_stock.stock_quantity += new_quantity

            ProductHistory.objects.create(
                product=product,
                transaction_type=new_transaction_type,
                quantity=new_quantity
            )

        product_stock.save()

        return redirect('product-history')

    def _render_error(self, request, transaction_type, requested_quantity, available_quantity):
        """Helper function to render error page when stock is insufficient."""
        error_message = f"Cannot {transaction_type} {requested_quantity} products. Only {available_quantity} products are available."
        all_products = ProductList.objects.all()
        history_list = ProductHistory.objects.all().order_by('-created_at')
        
        context = {
            'history_list': history_list,
            'error': error_message,
            'all_products': all_products
        }
        return render(request, 'product-history.html', context)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


@method_decorator(login_required, name='dispatch')
class ChangePasswordView(View):
    def post(self, request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_new_password = request.POST.get('confirm_new_password')

            user = request.user

            print(f"Old Password: {old_password}")
            print(f"New Password: {new_password}")
            print(f"Confirm New Password: {confirm_new_password}")

            if not user.check_password(old_password):
                return JsonResponse({'success': False, 'error': 'Old password is incorrect.'})

            if new_password != confirm_new_password:
                return JsonResponse({'success': False, 'error': 'New passwords do not match.'})

            user.set_password(new_password)
            user.save()

            update_session_auth_hash(request, user)

            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Invalid request.'})


@method_decorator(login_required, name='dispatch')
class SettingsView(View):
    template_name = 'settings.html'

    def get(self, request):
        return render(request, self.template_name)


class EditHistoryQuantityView(View):
    def post(self, request):
        history_id = request.POST.get('history_id')
        new_quantity = request.POST.get('quantity')

        try:
            new_quantity = float(new_quantity) 
            if new_quantity < 0:
                return JsonResponse({'status': 'error', 'message': 'Quantity cannot be negative.'})

            history = ProductHistory.objects.get(id=history_id)
            stock = ProductStock.objects.get(product=history.product)

            difference = new_quantity - history.quantity

            if history.transaction_type == 'buy':
                stock.stock_quantity += difference
            elif history.transaction_type == 'sell':
                stock.stock_quantity -= difference

            history.quantity = new_quantity
            history.save()
            stock.save()

            return JsonResponse({'status': 'success', 'message': 'Quantity updated successfully.'})
        
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid quantity value.'})
        except ProductHistory.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product history not found.'})
        except ProductStock.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product stock not found.'})


class DashboardView(TemplateView):
    template_name = 'product-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = ProductList.objects.count()
        return context


class Chart(View):
    def get(self, request):
        return render(request, 'chart.html')
    

def daily_additions(request):
    today = timezone.now().date()
    last_week = today - timedelta(days=6)
    
    history = ProductHistory.objects.filter(created_date__range=[last_week, today])
    
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    counts = [0] * 7  
    
    for record in history:
        date_str = record.created_date.strftime('%Y-%m-%d')
        if date_str in dates:
            index = dates.index(date_str)
            counts[index] += record.quantity
    
    context = {
        'dates': dates,
        'counts': counts,
    }
    
    return render(request, 'daily_additions.html', context)


class TodayTransactionsView(View):
    def get(self, request):
        today = timezone.now().date()
        print(today)
        
        total_buys = ProductHistory.objects.filter(transaction_type='Buy', created_at__date=today).aggregate(total=Sum('quantity'))['total'] or 0
        print(total_buys)
        total_sells = ProductHistory.objects.filter(transaction_type='sell', created_at__date=today).aggregate(total=Sum('quantity'))['total'] or 0
        
        return render(request, 'today_transactions.html', {
            'total_buys': total_buys,
            'total_sells': total_sells,
        })


class ProductListBulkDeleteView(View):
    def post(self, request):
        if 'action' in request.POST and request.POST['action'] == 'delete':
            product_ids = request.POST.getlist('product_ids')
            ProductList.objects.filter(id__in=product_ids).delete()
        return redirect('product-list')


class CompanyForm(forms.Form):
    company_name = forms.CharField(max_length=100)
    company_heading = forms.CharField(max_length=100)
    company_image = forms.ImageField(required=False)

    COLUMN_CHOICES = [
        ('product_id', 'Product ID'),
        ('product_name', 'Product Name'),
        ('product_type', 'Product Type'),
        ('created_at', 'Created Date'),
        ('quantity', 'Quantity'),
        ('unit', 'Unit'),
        ('transaction_type', 'Transaction Type'),
    ]

    selected_columns = forms.MultipleChoiceField(
        choices=COLUMN_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )


class AddCompanyAndGeneratePDFView(FormView):
    template_name = 'unit-list.html'
    form_class = CompanyForm
    success_url = reverse_lazy('units')

    def form_valid(self, form):
        self.request.session['company_name'] = form.cleaned_data['company_name']
        self.request.session['company_heading'] = form.cleaned_data['company_heading']
        self.request.session['selected_columns'] = form.cleaned_data.get('selected_columns', [])

        if form.cleaned_data.get('company_image'):
            company_image = form.cleaned_data['company_image']
            image_path = default_storage.save(company_image.name, company_image)
            image_url = self.request.build_absolute_uri(default_storage.url(image_path)) 
            self.request.session['company_logo'] = image_url
        else:
            self.request.session['company_logo'] = self.request.session.get('company_logo', '')

        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial['company_name'] = self.request.session.get('company_name', '')
        initial['company_heading'] = self.request.session.get('company_heading', '')
        initial['selected_columns'] = self.request.session.get('selected_columns', [])
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = self.request.session.get('company_name', '')
        context['company_heading'] = self.request.session.get('company_heading', '')
        context['company_logo'] = self.request.session.get('company_logo', '')
        context['selected_columns'] = self.request.session.get('selected_columns', [])

        context['all_columns'] = [col[0] for col in self.form_class.COLUMN_CHOICES]

        return context


# class DownloadPDFView(View):
#     def get(self, request, *args, **kwargs):
#         history_list = ProductHistory.objects.all()
#         selected_columns = request.session.get('selected_columns', [])

#         company_name = request.session.get('company_name', 'Your Company')
#         company_heading = request.session.get('company_heading', 'Product History Report')
#         company_image = request.session.get('company_logo', None)

#         context = {
#             'company_name': company_name,
#             'company_heading': company_heading,
#             'company_image': company_image,
#             'current_date': datetime.now().strftime('%Y-%m-%d'),
#             'history_list': history_list,
#             'selected_columns': selected_columns, 
#         }

#         html_string = render_to_string('pdf_template.html', context)

#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename=product_history.pdf'

#         pisa_status = pisa.CreatePDF(html_string, dest=response)

#         if pisa_status.err:
#             return HttpResponse('We had some errors <pre>' + html_string + '</pre>')

#         return response



from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from xhtml2pdf import pisa
from .models import ProductHistory  # Assuming these are your models
from django.template.loader import render_to_string


class DownloadPDFView(View):
    def get(self, request, *args, **kwargs):
        # Capture the selected product ID from the request (from query params or session)
        selected_product_id = request.GET.get('product_filter', None)

        # Fetch product history, filtered by the selected product if one is chosen
        if selected_product_id:
            history_list = ProductHistory.objects.filter(product_id=selected_product_id)
        else:
            history_list = ProductHistory.objects.all()

        # Fetch the selected columns from session, or provide defaults
        selected_columns = request.session.get('selected_columns', [])

        # Fetch company details from session or use defaults
        company_name = request.session.get('company_name', 'Your Company')
        company_heading = request.session.get('company_heading', 'Product History Report')
        company_image = request.session.get('company_logo', None)

        # Prepare the context for rendering the PDF
        context = {
            'company_name': company_name,
            'company_heading': company_heading,
            'company_image': company_image,
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'history_list': history_list,
            'selected_columns': selected_columns,  # These are the columns user selected
        }

        # Render the HTML string for PDF
        html_string = render_to_string('pdf_template.html', context)

        # Generate the PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=product_history.pdf'

        pisa_status = pisa.CreatePDF(html_string, dest=response)

        # Handle PDF generation errors
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html_string + '</pre>')

        return response
