from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Profile, Order, Rating


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required', required=True)
    first_name = forms.CharField(max_length=150, help_text='Required', required=True)
    last_name = forms.CharField(max_length=150, help_text='Required', required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username):
            self.add_error("username", "Username is already used.")
        if User.objects.filter(email=email).exists():
            self.add_error("email", "Email is already used.")
        return self.cleaned_data


class SignupProfileForm(forms.ModelForm):
    agreement = forms.BooleanField(widget=forms.CheckboxInput(attrs={'style': 'vertical-align: inherit'}),
                                   required=True)

    class Meta:
        model = Profile
        fields = ("address", "city", "country", "phone", "delivery", "agreement", "subscription",)


class SubscribeForm(forms.Form):
    email = forms.EmailField(max_length=200, help_text="Required", required=True)


class UserEditForm(forms.ModelForm):
    username = forms.CharField(max_length=150, help_text='Required', required=True)

    first_name = forms.CharField(max_length=150, help_text='Required', required=True)
    last_name = forms.CharField(max_length=150, help_text='Required', required=True)

    email = forms.EmailField(max_length=200, help_text='Required', required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(
                username=self.instance.username).exists():
            self.add_error("email", "Email is already used")
        return email


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("address", "city", "country", "phone", "delivery", "subscription",)


class CheckoutForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = True

    agreement = forms.BooleanField(widget=forms.CheckboxInput(attrs={'style': 'vertical-align: inherit'}),
                                   required=True)
    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'email', 'address', 'city', 'country', 'phone', 'delivery', 'agreement')
