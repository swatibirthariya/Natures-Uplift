from django import forms

class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=200)
    email = forms.EmailField()
    delivery_type = forms.ChoiceField(choices=(('normal','Normal (1.5 days)'),('fast','Fast (+₹50)')))
    phone = forms.CharField(
        max_length=10,
        min_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'type': 'tel',
            'maxlength': '10',
            'inputmode': 'numeric',
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if not re.fullmatch(r'[6-9]\d{9}', phone):
            raise forms.ValidationError(
                "Enter a valid 10-digit Indian mobile number"
            )

        return phone
        pincode = forms.CharField(max_length=10)
