from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group

from store.models import Web

web = Web.objects.first()

# Create your views here.
def register_view(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            customer_group = Group.objects.get(name='customers')
            if not customer_group:
                customer_group = Group.objects.create(name='customers')
            customer_group.user_set.add(user)
            messages.success(request, 'You are successfully registered!')
            return redirect('user-log-in')
        else:
            for key in form.errors:
                message = form.errors[key]
                if form.errors[key] == 'This field is required.':
                    message = key + " field is required"
                messages.add_message(request, messages.ERROR, message)

    context = {
        'title': web.name.upper(),
        'heading': "Don't have an account?",
        'form': form
    }
    return render(request, 'users/register.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.add_message(request, messages.ERROR, "Username or password doesn't match")

    context = {
        'title': web.name.upper(),
        'heading': "Welcome back"
    }
    return render(request, 'users/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('user-log-in')


def test_view(request):
    customer = request.user
    return redirect('store')
