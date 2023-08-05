from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views import View
from .models import *
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.db.models import Q
# Create your views here.
import datetime


class Index(View):

    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.POST.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity - 1
                else:
                    cart[product] = quantity + 1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1

        request.session['cart'] = cart
        print('cart', request.session['cart'])
        return redirect('homepage')

    def get(self, request):
        return HttpResponseRedirect(f'/store{request.get_full_path()[1:]}')


def store(request):
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}
    products = None
    categories = Categories.get_all_categories()
    categoryID = request.GET.get('category')
    if categoryID:
        products = Product.get_products_by_category_id(categoryID)
    else:
        products = Product.get_all_products()

    data = {}
    data['products'] = products
    data['categories'] = categories

    print('You are :', request.session.get('email'))
    return render(request, 'index.html', data)


class Login(View):
    return_url = None

    def get(self, request):
        Login.return_url = request.GET.get('return_url')
        return render(request, 'login.html')


    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id

                if Login.return_url:
                    return HttpResponseRedirect(Login.return_url)
                else:
                    Login.return_url = None
                    return redirect('homepage')
            else:
                error_message = 'invalid !!'
        else:
            error_message = 'invalid !!'

        print(email, password)
        return render(request, 'login.html', {'error': error_message})


def logout(request):
    request.session.clear()
    return redirect('login')


class Signup (View):
    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        postData = request.POST
        firstname = postData.get('firstname')
        lastname = postData.get('lastname')
        phone = postData.get('phone')
        email = postData.get('email')
        password = postData.get('password')
        # validation
        value = {
            'first_name': firstname,
            'last_name': lastname,
            'phone': phone,
            'email': email
        }
        error_message = None

        customer = Customer(
            firstname=firstname,
            lastname=lastname,
            phone=phone,
            email=email,
            password=password
                            )
        error_message = self.validateCustomer(customer)

        if not error_message:
            print(firstname, lastname, phone, email, password)
            customer.password = make_password(customer.password)
            customer.register()
            return redirect('homepage')
        else:
            data = {
                'error': error_message,
                'values': value
            }
            return render(request, 'signup.html', data)


    def validateCustomer(self, customer):
        error_message = None
        if (not customer.firstname):
            error_message = "Please Enter your First Name !!"
        elif len (customer.firstname) < 3:
            error_message = 'First Name must be 3 char long or more'
        elif not customer.lastname:
            error_message = 'Please Enter your Last Name'
        elif len(customer.lastname) < 3:
            error_message = 'Last Name must be 3 char long or more'
        elif not customer.phone:
            error_message = 'Enter your Phone Number'
        elif len(customer.phone) < 10:
            error_message = 'Phone Number must be 10 char Long'
        elif len(customer.password) < 5:
            error_message = 'Password must be 5 char long'
        elif len(customer.email) < 5:
            error_message = 'Email must be 5 char long'
        elif customer.isExists():
            error_message = 'Email Address Already Registered..'
        # saving

        return error_message


class Cart(View):
    def get(self, request):
        ids = list(request.session.get('cart').keys())
        products = Product.get_products_by_id(ids)
        print(products)
        return render(request, 'cart.html', {'products': products})


class Checkout(View):
    def post(self, request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        cart = request.session.get('cart')
        customer = request.session.get('customer')
        products = Product.get_products_by_id(list(cart.keys()))
        print(address, phone, cart, customer, products)

        for product in products:
            print(cart.get(str(product.id)))
            order = Order(
                customer=Customer(id=customer),
                product=product,
                price=product.price,
                address=address,
                phone=phone,
                quantity=cart.get(str(product.id)))
            order.save()
        request.session['cart'] = {}
        return redirect('cart')



class OrderView(View):

    def get(self, request):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        print(orders)
        return render(request, 'orders.html', {'orders': orders})






def search_result(request):
    query = request.GET.get("q")
    categories = Categories.get_all_categories()
    result = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query) | Q(
            price__icontains=query))
    if result:
        context = {
            "result": result,
            "categories": categories
        }
        return render(request, 'search.html', context)
    else:
        return render(request, 'error.html')


