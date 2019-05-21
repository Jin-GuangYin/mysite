from django import forms
from django.contrib import auth 
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(label = "username", required=True, \
                               widget=forms.TextInput(attrs={'class':'form-control', \
                               "placeholder" : 'please input username'}))#必须填写的项required设为True，默认为True
    password = forms.CharField(label = "password",  \
                               widget=forms.PasswordInput(attrs={'class':'form-control', \
                               "placeholder" : 'please input passworld'}))

    def clean(self):
        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]

        user = auth.authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError("username or password is wrong")
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data



class RegForm(forms.Form):
    username = forms.CharField(label = "username", required=True, \
                               max_length = 30,
                               min_length = 3,
                               widget=forms.TextInput(attrs={'class':'form-control', \
                               "placeholder" : 'please input username'}))#必须填写的项required设为True，默认为True
    email = forms.EmailField(label = "email", required=True, \
                             widget=forms.EmailInput(attrs={'class':'form-control', \
                             "placeholder" : 'please input email'}))#必须填写的项required设为True，默认为True
    password = forms.CharField(label = "password",  \
                               widget=forms.PasswordInput(attrs={'class':'form-control', \
                               "placeholder" : 'please input passworld'}))
    password_again = forms.CharField(label = "password_again",  \
                               widget=forms.PasswordInput(attrs={'class':'form-control', \
                               "placeholder" : 'please reinput passworld'}))

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("username has existed")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("email has existed")
        return email

    def clean_password_again(self):
        password = self.cleaned_data["password"]
        password_again = self.cleaned_data["password_again"]
        if password != password_again:
            raise forms.ValidationError("password is not equal")
        return password_again


