from django.contrib import admin
from .models import ProductList, ProductStock, ProductHistory, CustomUser
from django.contrib import admin
from .models import ProductList, ProductStock, ProductHistory, Unit

class ProductStockInline(admin.StackedInline):
    model = ProductStock
    can_delete = False
    verbose_name_plural = 'Stock'

class ProductListAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'product_name', 'product_type', 'unit')
    inlines = [ProductStockInline]
    fields = ('product_id', 'product_name', 'product_type', 'unit')

    def save_model(self, request, obj, form, change):
        if not change:  # if creating a new product
            if ProductList.objects.filter(product_id=obj.product_id).exists():
                # Handle the case where the product_id is not unique
                self.message_user(request, "A product with this ID already exists.", level='error')
                return
            obj.save()
            # Create ProductStock entry for new product
            ProductStock.objects.create(product=obj, stock_quantity=form.cleaned_data.get('stock_quantity', 0))
        else:
            super().save_model(request, obj, form, change)

class ProductStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'stock_quantity')

class ProductHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'transaction_type', 'quantity', 'created_at')

admin.site.register(ProductList, ProductListAdmin)
admin.site.register(ProductStock, ProductStockAdmin)
admin.site.register(ProductHistory, ProductHistoryAdmin)

admin.site.register(CustomUser)
admin.site.register(Unit)



