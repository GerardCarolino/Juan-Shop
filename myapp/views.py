from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from .models import User, Product, Category, Cart, Order, OrderItem
from .forms import UserRegistrationForm, VendorRegistrationForm, ProductForm, ProfileUpdateForm
import uuid

# Home and Product Views
def home(request):
    featured_products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()[:6]
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'myapp/home.html', context)

def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    search = request.GET.get('search')
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'myapp/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'myapp/product_detail.html', context)

# Authentication Views
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('myapp:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'myapp/register.html', {'form': form})

def vendor_register(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Vendor registration successful!')
            return redirect('myapp:vendor_dashboard')
    else:
        form = VendorRegistrationForm()
    return render(request, 'myapp/vendor_register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.user_type == 'vendor':
                return redirect('myapp:vendor_dashboard')
            return redirect('myapp:buyer_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'myapp/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('myapp:home')

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('myapp:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'myapp/profile.html', {'form': form})

# Vendor Views
@login_required
def vendor_dashboard(request):
    if request.user.user_type != 'vendor':
        return redirect('myapp:home')
    
    products = Product.objects.filter(vendor=request.user)
    orders = OrderItem.objects.filter(vendor=request.user).select_related('order')
    
    total_products = products.count()
    total_orders = orders.values('order').distinct().count()
    total_revenue = orders.aggregate(total=Sum('price'))['total'] or 0
    
    context = {
        'products': products,
        'orders': orders[:10],
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
    }
    return render(request, 'myapp/vendor_dashboard.html', context)

@login_required
def product_create(request):
    if request.user.user_type != 'vendor':
        messages.error(request, 'Only vendors can add products!')
        return redirect('myapp:home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('myapp:vendor_dashboard')
    else:
        form = ProductForm()
    return render(request, 'myapp/product_form.html', {'form': form, 'action': 'Add'})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('myapp:vendor_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'myapp/product_form.html', {'form': form, 'action': 'Edit'})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('myapp:vendor_dashboard')
    return render(request, 'myapp/product_confirm_delete.html', {'product': product})

# Buyer/Cart Views
@login_required
def buyer_dashboard(request):
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    context = {
        'recent_orders': recent_orders,
    }
    return render(request, 'myapp/buyer_dashboard.html', context)

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        if product.stock <= 0:
            messages.error(request, 'Product is out of stock!')
            return redirect('myapp:product_detail', slug=product.slug)
        
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart!')
        return redirect('myapp:product_detail', slug=product.slug)
    
    return redirect('myapp:product_list')

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    total = sum(item.get_total() for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'myapp/cart.html', context)

@login_required
def update_cart(request, cart_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        return redirect('myapp:cart')
    return redirect('myapp:cart')

@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('myapp:cart')

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('myapp:cart')
    
    total = sum(item.get_total() for item in cart_items)
    
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            order_number=str(uuid.uuid4())[:8].upper(),
            total_amount=total,
            shipping_address=request.POST.get('address'),
            shipping_city=request.POST.get('city'),
            shipping_zip=request.POST.get('zip'),
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                vendor=item.product.vendor,
                quantity=item.quantity,
                price=item.product.price,
            )
        
        cart_items.delete()
        
        messages.success(request, f'🎉 Purchase Successful! Order #{order.order_number} placed!')
        return redirect('myapp:order_history')
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'myapp/checkout.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'myapp/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'myapp/order_detail.html', {'order': order})