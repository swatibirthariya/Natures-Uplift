from django import forms

class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=200)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    pincode = forms.CharField(max_length=10)
    delivery_type = forms.ChoiceField(choices=(('normal','Normal (1.5 days)'),('fast','Fast (+₹50)')))
