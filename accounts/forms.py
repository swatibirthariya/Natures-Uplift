from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Address
import re
from .models import Address


from django import forms
from .models import Address
import re

from django import forms
from .models import Address
import re

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'pincode']

        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address',
                'required': True
            }),
            'phone': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '10-digit mobile number',
                'required': True
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'House no, Street, Area',
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City',
                'required': True
            }),
            'pincode': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '6-digit pincode',
                'required': True
            }),
        }

    # ✅ Name validation
    def clean_full_name(self):
        name = self.cleaned_data['full_name']
        if not re.fullmatch(r'[A-Za-z ]+', name):
            raise forms.ValidationError("Name should contain only letters.")
        return name

    # ✅ Phone validation
    def clean_phone(self):
        phone = str(self.cleaned_data['phone'])
        if not re.fullmatch(r'[6-9]\d{9}', phone):
            raise forms.ValidationError("Enter a valid 10-digit mobile number.")
        return phone

    # ✅ Pincode validation
    def clean_pincode(self):
        pincode = str(self.cleaned_data['pincode'])
        if not re.fullmatch(r'\d{6}', pincode):
            raise forms.ValidationError("Enter a valid 6-digit pincode.")
        return pincode
    
# ===== Registration Form =====
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Mobile number'}), required=False)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}), required=False)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}))

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone', 'email', 'password1', 'password2')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.fullmatch(r'[6-9]\d{9}', phone):
            raise forms.ValidationError("Enter a valid 10-digit Indian mobile number")
        return phone


# ===== Login Form =====
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Mobile number or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


# ===== OTP Form =====
class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'placeholder': 'Enter OTP'}))


# ===== Reset Password Form =====
class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match.")


