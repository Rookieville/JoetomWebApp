from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from .models import Customer, Order


class OrderForm(ModelForm):
	class Meta:
		model = Order
		fields = '__all__'
		exclude = ['user', 'customer', 'date_ordered', 'complete', 'transaction_id']


class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1','password2',]