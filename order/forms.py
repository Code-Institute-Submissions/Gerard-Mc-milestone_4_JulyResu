from django import forms
from checkout.models import OrderLineItem


class CustomProductForm(forms.ModelForm):
    class Meta:
        model = OrderLineItem
        fields = (
            'category', 'complexity', 'variations', 'user_description',
            'fast_delivery',)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['id'] = field
            self.fields[field].widget.attrs['class'] = 'form-check-input w-100'
            self.fields[field].widget.attrs['onclick'] = 'total()'
            self.fields['user_description'].widget.attrs['class'] = '' \
                'form-check-input w-100'
        self.fields['user_description'].widget.attrs['placeholder'] = '' \
            'Your product\'s description...'
        self.fields['user_description'].widget.attrs['style'] = '' \
            'max-height: 100px'
        self.fields['fast_delivery'].label = "Fast Delivery +15%"
