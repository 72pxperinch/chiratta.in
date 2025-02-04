from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.models import User

import json
import razorpay

from .forms import *
from .models import *

def default_context(request):
    web = Web.objects.first()

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, order_status='DRAFT')
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'id': None, 'get_cart_total': 0, 'get_cart_items_count': 0, }
    context = {'order': order, 'items': items, 'web': web}
    return context


# Create your views here.
def home_view(request):
    products = Product.objects.all()
    context = default_context(request)
    context['products'] = products
    return render(request, 'store/store.html', context)


def product_view(request, pid):
    product = Product.objects.get(id=pid)
    context = default_context(request)
    context['product'] = product
    return render(request, 'store/product.html', context)


def cart_view(request):
    context = default_context(request)
    return render(request, 'store/cart.html', context)


def checkout_view(request):
    address = request.user.address_set.first()
    context = default_context(request)
    context['address'] = address
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    product_id = data['product_id']
    data_action = data['data_action'].lower()
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, order_status='DRAFT')
        order_item, item_created = OrderItem.objects.get_or_create(order=order, product_id=product_id)

        if data_action == 'add':
            order_item.quantity += 1
        elif data_action == 'remove':
            order_item.quantity -= 1

        order_item.save()

        if order_item.quantity <= 0:
            order_item.delete()

        return JsonResponse("Saved", safe=False)
    else:
        return JsonResponse("Something Went Wrong!", safe=False)


def save_checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST, request.FILES)

        if form.is_valid():
            user = User.objects.get(username=request.user.username)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']

            user.save()

            user_address = Address.objects.filter(customer=user).first()

            if not user_address:
                user_address = Address.objects.create(
                    customer=user,
                    address=form.cleaned_data['street_address'],
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    country=form.cleaned_data['country'],
                    pin_code=form.cleaned_data['pin_code'],
                    mobile=form.cleaned_data['phone_number']
                )
            else:
                user_address.address = form.cleaned_data['street_address']
                user_address.city = form.cleaned_data['city']
                user_address.state = form.cleaned_data['state']
                user_address.country = form.cleaned_data['country']
                user_address.pin_code = form.cleaned_data['pin_code']
                user_address.mobile = form.cleaned_data['phone_number']

            user_address.save()

            order = Order.objects.get(customer=user, order_status='DRAFT')
            order.shipping_address = user_address

            order.save()

            messages.add_message(request, messages.WARNING, "Verify the data and make payment")
            return redirect('store-make_payment')
        else:
            print(form.errors)
            for key in form.errors:

                message = form.errors[key]
                if form.errors[key] == 'This field is required.':
                    message = key + " field is required"
                messages.add_message(request, messages.ERROR, message)
            return redirect('store-checkout')


def make_payment(request):
    if not request.user.is_authenticated:
        return redirect('user-log-in')

    customer = request.user
    address = request.user.address_set.first()
    context = default_context(request)
    order = context['order']

    if not len(context['items']):
        order.delete()
        return redirect('store')

    client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY, settings.RAZOR_PAY_SECRET))

    if request.method == 'POST':

        params_dict = {
            'razorpay_order_id': request.POST.get('razorpay_order_id'),
            'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
            'razorpay_signature': request.POST.get('razorpay_signature')
        }

        if request.POST.get('razorpay_payment_id'):
            order.order_status = "ACCEPTED"
            order.pg_order_id = request.POST.get('razorpay_order_id')
            order.signature = request.POST.get('razorpay_signature')
            order.transaction_id = request.POST.get('razorpay_payment_id')
            order.save()

            subject = 'Your Order Placed Successfully!'
            message = f'Hi {customer.first_name}, Your Order Placed Successfully from ' + str(web.name.title())
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [customer.email, ]
            send_mail(subject, message, email_from, recipient_list)

            messages.add_message(request, messages.SUCCESS, "Order Placed Successfully!")
            return redirect('store-invoice', order_id=order.id)
        else:
            messages.add_message(request, messages.ERROR, "Oops, Something went wrong!")
            return redirect('store-make_payment')

    order_amount = order.get_cart_total
    order_currency = 'INR'
    razorpay_order = client.order.create(data={
        'receipt': str(order.id),
        'amount': order_amount * 100,
        'currency': order_currency,
        'payment_capture': 1
    })
    order.pg_order_id = razorpay_order['id']

    razorpay_order_data = {
        'key': settings.RAZOR_PAY_KEY,
        'amount': (order_amount * 100),
        'name': Web.objects.first().name,
        'description': '',
        'theme': {
            'color': '#333333'
        },
        'prefill': {
            'name': request.user.first_name + " " + request.user.last_name,
            'customer_email': request.user.email,
            'contact': address.mobile
        },
        'order_id': order.pg_order_id
    }
    context['razorpay_order_data'] = razorpay_order_data
    context['address'] = address
    return render(request, 'store/sale_preview.html', context)


def orders(request):
    if request.user.is_authenticated:
        customer = request.user
        orders_fetched = Order.objects.filter(customer=customer).exclude(order_status="DRAFT")
        orders_list = []
        for order in orders_fetched:
            items_in_order = order.orderitem_set.all()
            orders_list.append({'order': order, 'items': items_in_order})
        context = default_context(request)
        context['orders'] = orders_list
        return render(request, 'store/orders.html', context)
    else:
        return redirect('user-log-in')


def get_invoice(request, order_id):
    if request.user.is_authenticated:
        customer = request.user
        address = Address.objects.get(customer=customer)
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            context = {'order': {'id': None, 'get_cart_total': 0, 'get_cart_items_count': 0}, 'items': []}
            return render(request, 'store/invoice.html', context)

        items = OrderItem.objects.filter(order=order)
        context = {'order': order, 'items': items, 'address': address}
        return render(request, 'store/invoice.html', context)
    else:
        return redirect('user-log-in')


def about_view(request):
    context = default_context(request)
    return render(request, 'store/about.html', context)


def contact_view(request):
    if request.method == 'POST':
        form = SendMessageForm(request.POST)
        if form.is_valid():
            message = Message.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message'],
            )
            message.save()
            messages.add_message(request, messages.SUCCESS, "You message is successfully sent!")
        else:
            for key in form.errors:
                message = form.errors[key]
                if form.errors[key] == 'This field is required.':
                    message = key + " field is required"
                messages.add_message(request, messages.ERROR, message)

    context = default_context(request)
    return render(request, 'store/contact.html', context)


def policy_view(request, data_name):
    data_name_list = ['terms-and-conditions', 'privacy-policy', 'refund-and-cancellation-policy', 'shipping-policy']
    if data_name not in data_name_list:
        return redirect(to='about')
    context = default_context(request)
    context['data_name'] = data_name
    data_id = '_'.join(data_name.split('-'))
    context['data_title'] = ' '.join(data_name.split('-'))
    context['data'] = getattr(context['web'], data_id)
    return render(request, 'store/policy.html', context)
