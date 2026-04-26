from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from .models import Product, Category
from .forms import CategoryForm, ProductForm, OrderForm, ContactForm


def product_list(request):
    products = Product.objects.all()
    return render(
        request,
        'products.html',
        {
            'products': products,
            'count': products.count(),
        },
    )


def category_list(request):
    categories = Category.objects.all()
    return render(
        request,
        'categories.html',
        {
            'categories': categories,
            'count': categories.count(),
        },
    )


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.user.is_authenticated:
        return redirect('products')
    error_message = None
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('products')
        error_message = 'Please fix the highlighted fields and try again.'
    else:
        form = UserCreationForm()
    return render(
        request,
        'register.html',
        {
            'form': form,
            'error_message': error_message,
        },
    )


@require_http_methods(['GET', 'POST'])
def user_login(request):
    if request.user.is_authenticated:
        return redirect('products')
    error_message = None
    next_url = None
    username_value = ''
    if request.method == 'POST':
        next_url = request.POST.get('next')
        username_value = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        user = authenticate(request, username=username_value, password=password)
        if user is not None:
            login(request, user)
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('products')
        error_message = 'Please enter a correct username and password.'
    else:
        next_url = request.GET.get('next')
    return render(
        request,
        'login.html',
        {
            'next': next_url,
            'error_message': error_message,
            'username_value': username_value,
        },
    )


@require_POST
def user_logout(request):
    logout(request)
    return redirect('products')


@login_required
@require_http_methods(['GET', 'POST'])
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})


@login_required
@require_http_methods(['GET', 'POST'])
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})


@login_required
@require_http_methods(['GET', 'POST'])
def create_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.save()
            return redirect('products')
    else:
        form = OrderForm()
    return render(request, 'order_form.html', {'form': form, 'product': product})


@require_http_methods(['GET', 'POST'])
def contact_view(request):
    submitted_data = None
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            submitted_data = form.cleaned_data
    else:
        form = ContactForm()
    return render(
        request,
        'contact_form.html',
        {'form': form, 'submitted_data': submitted_data},
    )
