
from django import forms
from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'category',
            'title',
            'description',
            'price',
            'image',
            'sale_type',
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
