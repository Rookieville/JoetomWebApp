from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
import json
import datetime

from django.contrib import messages

from .models import * 
from .utils import cookieCart, cartData, guestOrder
from .forms import CreateUserForm
from .forms import OrderForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users, admin_only

def home(request):
     context = {}
     return render(request, 'store/home.html', context)

def contact(request):
     context = {}
     return render(request, 'store/ContactUs.html', context)


def loginPage(request):

     if request.user.is_authenticated:
          return redirect('userPage')
     else:
          if request.method == 'POST':
               username = request.POST.get('username')
               password = request.POST.get('password')

               user = authenticate(request, username=username, password=password)

               if user is not None:
                    login(request, user)
                    return redirect('home')
               else:
                    messages.info(request, 'Username OR password is incorrect')



     context = {}
     return render(request, 'store/login.html', context)


def logoutUser(request):
     logout(request)
     return redirect('home')

def register(request):
     if request.user.is_authenticated:
          return redirect('store')
     else:
          form = CreateUserForm()

          if request.method == 'POST':
               form = CreateUserForm(request.POST)
               if form.is_valid():
                    user = form.save()
                    username = form.cleaned_data.get('username')
                    email = form.cleaned_data.get('email')


                    Customer.objects.create(
                         user=user,
                         name=user.username,
                         email=user.email,
                         )

                    messages.success(request, 'Account was created for ' + username)

                    return redirect('login')



     context = {'form':form}
     return render(request, 'store/register.html', context)

@login_required(login_url='login')
def userPage(request):
     orders = request.user.customer.order_set.all()

     total_orders = orders.count()
     delivered = orders.filter(status='Delivered').count()
     pending = orders.filter(status='Pending').count()

     print('ORDERS:', orders)

     context = {'orders':orders, 'total_orders':total_orders,
     'delivered':delivered,'pending':pending}
     return render(request, 'store/userPage.html', context)


def store(request):
     data = cartData(request)

     cartItems = data['cartItems']
     order = data['order']
     items = data['items']

     products = Product.objects.all()
     context = {'products':products, 'cartItems':cartItems}
     return render(request, 'store/store.html', context)

#@login_required(login_url='login')
def cart(request):
     data = cartData(request)

     cartItems = data['cartItems']
     order = data['order']
     items = data['items']

     context = {'items':items, 'order':order, 'cartItems':cartItems}
     return render(request, 'store/cart.html', context)

#@login_required(login_url='login')
def checkout(request):
     data = cartData(request)
     
     cartItems = data['cartItems']
     order = data['order']
     items = data['items']

     context = {'items':items, 'order':order, 'cartItems':cartItems}
     return render(request, 'store/checkout.html', context)

#Order list
@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def myorders(request):
     orders=Order.objects.filter(user=request.user).order_by('-id')
     return render(request, '',{'orders':orders})

# Order Detail
def orderlist(request,id):
     order=Order.objects.get(pk=id)
     orderitems=OrderItem.objects.filter(order=order).order_by('-id')
     return render(request, 'store/orderlist.html',{'orderitems':orderitems})

def userorderlist(request,id):
     order=Order.objects.get(pk=id)
     orderitems=OrderItem.objects.filter(order=order).order_by('-id')
     return render(request, 'store/userorderlist.html',{'orderitems':orderitems})


def updateItem(request):
     data = json.loads(request.body)
     productId = data['productId']
     action = data['action']
     print('Action:', action)
     print('Product:', productId)

     customer = request.user.customer
     product = Product.objects.get(id=productId)
     order, created = Order.objects.get_or_create(customer=customer, complete=False)

     orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

     if action == 'add':
          orderItem.quantity = (orderItem.quantity + 1)
     elif action == 'remove':
          orderItem.quantity = (orderItem.quantity - 1)

     orderItem.save()

     if orderItem.quantity <= 0:
          orderItem.delete()

     return JsonResponse('Item was added', safe=False)

def processOrder(request):
     transaction_id = datetime.datetime.now().timestamp()
     data = json.loads(request.body)

     if request.user.is_authenticated:
          customer = request.user.customer
          order, created = Order.objects.get_or_create(customer=customer, complete=False)
     else:
          customer, order = guestOrder(request, data)

     total = float(data['form']['total'])
     order.transaction_id = transaction_id

     if total == order.get_cart_total:
          order.complete = True
     order.save()

     if order.shipping == True:
          ShippingAddress.objects.create(
          customer=customer,
          order=order,
          address=data['shipping']['address'],
          city=data['shipping']['city'],
          state=data['shipping']['state'],
          zipcode=data['shipping']['zipcode'],
          )

     return JsonResponse('Payment submitted..', safe=False)








#Testing
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def dashboard(request):
     orders = Order.objects.all()
     customers = Customer.objects.all()

     total_customers = customers.count()

     total_orders = orders.count()
     delivered = orders.filter(status='Delivered').count()
     pending = orders.filter(status='Pending').count()

     context = {'orders':orders, 'customers':customers,
     'total_orders':total_orders,'delivered':delivered,
     'pending':pending }

     return render(request, 'store/dashboard.html', context)


@login_required(login_url='login')
def customer(request, pk_test):
     customer = Customer.objects.get(id=pk_test)

     orders = customer.order_set.all()
     order_count = orders.count()

     myFilter = OrderFilter(request.GET, queryset=orders)
     orders = myFilter.qs 

     context = {'customer':customer, 'orders':orders, 'order_count':order_count,
     'myFilter':myFilter}
     return render(request, 'store/customer.html',context)



def products(request):
     products = Product.objects.all()

     return render(request, 'store/products.html', {'products':products})




@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request):
     action = 'create'
     form = OrderForm()
     if request.method == 'POST':
          form = OrderForm(request.POST)
          if form.is_valid():
               form.save()
               return redirect('/')

     context =  {'action':action, 'form':form}
     return render(request, 'store/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
     order = Order.objects.get(id=pk)
     form = OrderForm(instance=order)
     print('ORDER:', order)
     if request.method == 'POST':

          form = OrderForm(request.POST, instance=order)
          if form.is_valid():
               form.save()
               return redirect('dashboard')

     context = {'form':form}
     return render(request, 'store/order_form.html', context)


@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
     order = Order.objects.get(id=pk)
     if request.method == "POST":
          order.delete()
          return redirect('dashboard')

     context = {'item':order}
     return render(request, 'store/delete.html', context)