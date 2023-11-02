from django.shortcuts import render, redirect
from django.http import JsonResponse

from .models import *
import json
import datetime

from django.contrib.auth import authenticate, login
from .forms import LoginForm

from django.contrib.auth.models import User, auth

from django.contrib.auth.forms import UserCreationForm

from django.contrib import messages
from django.shortcuts import render, redirect






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
    """ if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Проверяем, есть ли пользователь в модели User
                if not User.objects.filter(username=username).exists():
                    user = form.save(commit=False)  # Создаем новую запись в модели User
                    user.set_password(password)  # Сохраняем пароль пользователя
                    user.save()
                login(request, user)
                return redirect('store')  
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    
    return render(request, 'store/login.html', {'form': form})
 """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('store')
        else:
            messages.info(request, 'Invalid Username or Password')
            return redirect('login')



    else:
        return render(request, 'store/login.html')

def registerPage(request):
    """ form=UserCreationForm()

    if request.method =='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('')
        
    context={'form': form}
    return render(request, 'store/register.html', context) """


    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password==confirm_password:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username is already taken')
                return redirect(store)
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email is already taken')
                return redirect(store)
            else:
                user = User.objects.create_user(username=username, password=password, 
                                        email=email, first_name=first_name, last_name=last_name)
                user.save()
                
                return redirect('login')


        else:
            messages.info(request, 'Both passwords are not matching')
            return redirect(store)
            

    else:
        return render(request, 'store/register.html')
    


def logout_view(request):
    auth.logout(request)
    return redirect('store')


