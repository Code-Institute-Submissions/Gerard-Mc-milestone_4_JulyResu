from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            'default_phone_number', 'default_email', 'default_postcode',
            'default_town_or_city', 'default_street_address1',
            'default_street_address2', 'default_country',
            'default_county')

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        self.fields['default_phone_number'].widget.attrs['autofocus'] = True
        for field in self.fields:
            self.fields[field].widget.attrs['id'] = field
            self.fields[field].widget.attrs['class'] = 'w-100 mb-2'
        self.fields['default_phone_number'].label = "Phone Number"
        self.fields['default_email'].label = "Email"
        self.fields['default_postcode'].label = "Postcode"
        self.fields['default_town_or_city'].label = "Town or City"
        self.fields['default_street_address1'].label = "Street Address 1"
        self.fields['default_street_address2'].label = "Street Address 2"
        self.fields['default_country'].label = "Country"
        self.fields['default_county'].label = "County"
