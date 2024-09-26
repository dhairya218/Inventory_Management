from django import forms
from .models import ProductList, CustomUser
from django.contrib.auth.forms import PasswordChangeForm
from .models import ProductHistory
from django import forms
from django.core.exceptions import ValidationError
import re

from django import forms
from .models import ProductHistory, Unit

from django import forms
from .models import Unit

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['unit_name']


class ProductHistoryForm(forms.ModelForm):
    class Meta:
        model = ProductHistory
        fields = ['transaction_type', 'quantity']
        widgets = {
            'transaction_type': forms.Select(choices=[('buy', 'Buy'), ('sell', 'Sell')]),
            'quantity': forms.NumberInput(attrs={'min': 0, 'step': 'any'}) 
        }


class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']


# class ProductForm(forms.ModelForm):
#     initial_quantity = forms.FloatField()

#     class Meta:
#         model = ProductList
#         fields = ['product_name','unit', 'product_type']

#     unit = forms.ModelChoiceField(queryset=Unit.objects.all(), empty_label="Select Unit")

#     def clean_product_name(self):
#         product_name = self.cleaned_data.get('product_name')
#         regex = "^[^<>'\"/;`%]*$"
        
#         if not re.match(regex, product_name):
#             raise ValidationError("You can't use special characters in the product name.")

#         if ProductList.objects.filter(product_name=product_name).exists():
#             raise ValidationError("This product name is already in use.")

#         return product_name

#     def clean_product_type(self):
#         product_type = self.cleaned_data.get('product_type')
#         regex = "^[^<>'\"/;`%]*$"
        
#         if not re.match(regex, product_type):
#             raise ValidationError("You can't use special characters in the product type.")

#         return product_type

#     def clean_initial_quantity(self):
#         initial_quantity = self.cleaned_data.get('initial_quantity')
        
#         if initial_quantity < 0:
#             raise ValidationError("Quantity cannot be negative.")
        
#         return initial_quantity

# import re
# from django.core.exceptions import ValidationError

# class ProductForm(forms.ModelForm):
#     initial_quantity = forms.FloatField()

#     class Meta:
#         model = ProductList
#         fields = ['product_name', 'unit', 'product_type']

#     unit = forms.ModelChoiceField(queryset=Unit.objects.all(), empty_label="Select Unit")

#     def clean_product_name(self):
#         product_name = self.cleaned_data.get('product_name')

#         # Updated regex to block all special characters, allowing only letters, numbers, and spaces
#         regex = "^[a-zA-Z0-9 ]+$"  

#         if not re.match(regex, product_name):
#             raise ValidationError("You can't use special characters in the product name.")

#         if ProductList.objects.filter(product_name=product_name).exists():
#             raise ValidationError("This product name is already in use.")

#         return product_name

#     def clean_product_type(self):
#         product_type = self.cleaned_data.get('product_type')

#         regex = "^[a-zA-Z0-9 ]+$"  # Allow only letters, numbers, and spaces
#         if not re.match(regex, product_type):
#             raise ValidationError("You can't use special characters in the product type.")

#         return product_type

#     def clean_initial_quantity(self):
#         initial_quantity = self.cleaned_data.get('initial_quantity')

#         if initial_quantity < 0:
#             raise ValidationError("Quantity cannot be negative.")

#         return initial_quantity

import re
from django.core.exceptions import ValidationError
from django import forms

class ProductForm(forms.ModelForm):
    initial_quantity = forms.FloatField()

    class Meta:
        model = ProductList
        fields = ['product_name', 'unit', 'product_type']

    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), empty_label="Select Unit")

    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')

        # Regex to block all special characters, allowing only letters, numbers, and spaces
        regex = "^[a-zA-Z0-9 ]+$"  

        if not re.match(regex, product_name):
            raise ValidationError("You can't use special characters in the product name.")

        if ProductList.objects.filter(product_name=product_name).exists():
            raise ValidationError("This product name is already in use.")

        return product_name

    def clean_product_type(self):
        product_type = self.cleaned_data.get('product_type')

        # Same regex to block special characters in product type
        regex = "^[a-zA-Z0-9 ]+$"
        if not re.match(regex, product_type):
            raise ValidationError("You can't use special characters in the product type.")

        return product_type

    def clean_initial_quantity(self):
        initial_quantity = self.cleaned_data.get('initial_quantity')

        if initial_quantity < 0:
            raise ValidationError("Quantity cannot be negative.")

        return initial_quantity



class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'role', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    role = forms.ChoiceField(choices=[(CustomUser.Manager, 'Manager'), (CustomUser.Staff, 'Staff')])



class CompanyForm(forms.Form):
    company_name = forms.CharField(max_length=255, required=False)
    company_heading = forms.CharField(max_length=255, required=False)
    company_image = forms.ImageField(required=False)
    selected_columns = forms.MultipleChoiceField(
        choices=[
            ('company_name', 'Company Name'),
            ('company_image', 'Company Image'),
            ('product_id', 'Product ID'),
            ('product_name', 'Product Name'),
            ('product_type', 'Product Type'),
            ('created_at', 'Created Date'),
            ('quantity', 'Quantity'),
            ('unit', 'Unit'),
            ('transaction_type', 'Transaction Type')
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple
    )