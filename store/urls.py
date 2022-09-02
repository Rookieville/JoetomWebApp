from django.urls import path
from . import views
from django.contrib import admin


urlpatterns = [
        #Leave as empty string for base url
	path('', views.home, name="home"),
	path('store/', views.store, name="store"),
	path('admin/', admin.site.urls),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('contact/', views.contact, name="contact"),
	path('register/', views.register, name="register"),
	path('login/', views.loginPage, name="login"),
	path('logout/', views.logoutUser, name="logout"),
	path('userPage/', views.userPage, name="userPage"),
	path('dashboard/', views.dashboard, name="dashboard"),
	path('products/', views.products, name='products'),
	path('orderlist/<int:id>', views.orderlist, name='orderlist'),
	path('userorderlist/<int:id>', views.userorderlist, name='userorderlist'),
   	path('customer/<str:pk_test>/', views.customer, name="customer"),

   	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
    	path('create_order/', views.createOrder, name="create_order"),
    	path('update_order/<str:pk>/', views.updateOrder, name="update_order"),
    	path('delete_order/<str:pk>/', views.deleteOrder, name="delete_order"),

]