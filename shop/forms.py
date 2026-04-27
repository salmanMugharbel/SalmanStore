from django import forms
from .models import Category, Product, Order


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'quantity']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Price cannot be negative.')
        return price

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError('Quantity cannot be negative.')
        return quantity


class OrderForm(forms.ModelForm):
    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product

    class Meta:
        model = Order
        fields = ['quantity']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError('Quantity must be greater than zero.')
        if self.product and quantity and quantity > self.product.quantity:
            raise forms.ValidationError(
                f'Only {self.product.quantity} item(s) available in stock.'
            )
        return quantity


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
