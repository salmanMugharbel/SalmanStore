from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from .models import Product, Category
from .forms import CategoryForm, ProductForm, OrderForm, ContactForm


def product_image_url(product_id):
    return f'https://picsum.photos/seed/store-product-{product_id}/420/520'


def product_list(request):
    if request.user.is_authenticated:
        products = Product.objects.select_related('category').filter(owner=request.user)
    else:
        products = Product.objects.none()
    sort_value = request.GET.get('sort', 'default')
    category_filter_raw = request.GET.get('category', '').strip()
    category_filter_id = None
    selected_category = None
    if category_filter_raw.isdigit():
        category_filter_id = int(category_filter_raw)
        products = products.filter(category_id=category_filter_id)
        selected_category = Category.objects.filter(
            id=category_filter_id,
            owner=request.user if request.user.is_authenticated else None,
        ).first()

    if sort_value == 'price_asc':
        products = products.order_by('price', 'id')
    elif sort_value == 'price_desc':
        products = products.order_by('-price', 'id')
    else:
        sort_value = 'default'
        products = products.order_by('id')

    product_cards = [
        {
            'obj': product,
            'image_url': product_image_url(product.id),
        }
        for product in products
    ]
    return render(
        request,
        'products.html',
        {
            'products': product_cards,
            'count': len(product_cards),
            'sort_value': sort_value,
            'category_filter_id': category_filter_id,
            'selected_category': selected_category,
        },
    )


def product_detail(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(
            Product.objects.select_related('category'),
            id=product_id,
            owner=request.user,
        )
    else:
        product = get_object_or_404(
            Product.objects.select_related('category'),
            id=product_id,
            owner=None,
        )
    related_products = Product.objects.filter(category=product.category).exclude(
        id=product.id
    )[:4]
    related_cards = [
        {'obj': item, 'image_url': product_image_url(item.id)} for item in related_products
    ]
    return render(
        request,
        'product_detail.html',
        {
            'product': product,
            'product_image_url': product_image_url(product.id),
            'related_products': related_cards,
        },
    )


def category_list(request):
    if request.user.is_authenticated:
        categories = Category.objects.filter(owner=request.user)
    else:
        categories = Category.objects.none()
    category_cards = [
        {
            'obj': category,
            'image_url': f'https://picsum.photos/seed/store-category-{category.id}/520/340',
        }
        for category in categories
    ]
    return render(
        request,
        'categories.html',
        {
            'categories': category_cards,
            'count': len(category_cards),
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
            category = form.save(commit=False)
            category.owner = request.user
            category.save()
            return redirect('categories')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})


@login_required
@require_http_methods(['GET', 'POST'])
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        form.fields['category'].queryset = Category.objects.filter(owner=request.user)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            return redirect('products')
    else:
        form = ProductForm()
        form.fields['category'].queryset = Category.objects.filter(owner=request.user)
    return render(request, 'product_form.html', {'form': form})


@login_required
@require_http_methods(['GET', 'POST'])
def create_order(request, product_id):
    product = get_object_or_404(Product, id=product_id, owner=request.user)
    if request.method == 'POST':
        form = OrderForm(request.POST, product=product)
        if form.is_valid():
            with transaction.atomic():
                product.refresh_from_db()
                requested_qty = form.cleaned_data['quantity']
                if requested_qty > product.quantity:
                    form.add_error(
                        'quantity',
                        f'Only {product.quantity} item(s) available in stock.',
                    )
                else:
                    order = form.save(commit=False)
                    order.product = product
                    order.owner = request.user
                    order.save()
                    Product.objects.filter(id=product.id).update(
                        quantity=F('quantity') - requested_qty
                    )
                    return redirect('products')
    else:
        form = OrderForm(product=product)
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


@require_http_methods(['GET'])
def contact_no_csrf_page(request):
    return render(request, 'contact_no_csrf.html')
