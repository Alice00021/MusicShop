from django.shortcuts import render, redirect
from django.http import JsonResponse

from .models import *
import json
import datetime

from django.contrib.auth import authenticate, login
from .forms import LoginForm

from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm






def store(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order, created= Order.objects.get_or_create(customer=customer, complete=False)
        items=order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0,'get_cart_items':0, 'shipping': False}
        cartItems=order['get_cart_items']

    products=Product.objects.all()
    context ={'products': products, 'cartItems': cartItems}
    return render (request, 'store/store.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order, created= Order.objects.get_or_create(customer=customer, complete=False)
        items=order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0,'get_cart_items':0,'shipping': False}
        cartItems = order.get_cart_items

    context ={'items':items, 'order':order, 'cartItems': cartItems}
    return render (request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order, created= Order.objects.get_or_create(customer=customer, complete=False)
        items=order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0,'get_cart_items':0,'shipping': False}
        cartItems = order.get_cart_items

    context ={'items':items, 'order':order , 'cartItems': cartItems}
    return render (request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('ProductId:', productId)

    customer= request.user.customer
    product= Product.objects.get(id=productId)
    order, created= Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created= OrderItem.objects.get_or_create(order=order, product=product)

    if action =='add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity<=0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)



def processOrder(request):
    transaction_id=datetime.datetime.now().timestamp()
    data = json.loads(request.body)



    if request.user.is_authenticated:
        customer = request.user.customer
        order, created= Order.objects.get_or_create(customer=customer, complete=False)
        total= float(data['form']['total'])
        order.transaction_id= transaction_id

        if total == order.get_cart_total:
            order.complete= True
        order.save()

        if order.shipping== True:
            ShippingAddress.objects.create(
                customer=customer, 
                order=order,
                address=data['shipping'] ['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode= data['shipping']['zipcode'],
            )

    else:
        print('User is not logged in..') 
    print('Data:', request.body)
    return JsonResponse('Payment complete', safe=False)

""" def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('store')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    
    return render(request, 'store/login.html', {'form': form}) """


from django.contrib.auth import login

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Проверяем, есть ли пользователь в модели User
                if not User.objects.filter(username=username).exists():
                    user = form.save()  # Создаем новую запись в модели User
                    user.set_password(password)  # Сохраняем пароль пользователя
                    user.save()
                login(request, user)
                return redirect('store')  
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    
    return render(request, 'store/login.html', {'form': form})


def registerPage(request):
    form=UserCreationForm()

    if request.method =='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('')
        
    context={'form': form}
    return render(request, 'store/register.html', context)

""" def loginPage(request):
    form=UserCreationForm()
    context={'form': form}
    return render(request, 'store/login.html', context)

 """