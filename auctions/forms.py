
from django import forms
from .models import Auction


class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = [
            'starting_price',
            'start_time',
            'end_time',
        ]

        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        starting_price = cleaned_data.get('starting_price')

        if start_time and end_time and end_time <= start_time:
            self.add_error(
                'end_time',
                'End time must be after start time.'
            )

        if starting_price is not None and starting_price <= 0:
            self.add_error(
                'starting_price',
                'Starting price must be greater than zero.'
            )

        return cleaned_data
