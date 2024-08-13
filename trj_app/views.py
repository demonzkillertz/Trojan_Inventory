from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem, CustomUser, Order, OrderItem, Category, RootCategory, FavoriteItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login , logout, update_session_auth_hash
from .forms import SignUpForm
from django.http import HttpResponse
from django.contrib import messages
import json
from django.core.cache import cache

def home(request):
    if request.user.is_authenticated:
        fav=FavoriteItem.objects.filter(user=request.user)
        favourite=[favour.product.title for favour in fav]
    else:
        favourite=[]
    products = Product.objects.all()
    root_categories = RootCategory.objects.all()
    context = {'products': products, 'rcat':root_categories,'favourite':favourite}
    print(favourite)
    return render(request, 'home.html', context)

def category(request):
    if request.user.is_authenticated:
        favourite=FavoriteItem.objects.filter(user=request.user)
    else:
        favourite=[]
    root_categories = RootCategory.objects.all()
    products=Product.objects.all()
    return render(request,'category.html',{'cat':root_categories,'fav':favourite, 'products':products})

def category_view(request,category_name):
        category = get_object_or_404(Category, name=category_name)
        rcategory = get_object_or_404(RootCategory, category_id=category.id)
        if request.user.is_authenticated:
            favourite=FavoriteItem.objects.filter(user=request.user)
        else:
            favourite=[]
        root_categories = RootCategory.objects.all()
        products = Product.objects.filter(categories=category)
        return render(request,'category.html',{'cat':root_categories,'fav':favourite, 'products':products, 'category':rcategory})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if not product.image2:
        product.image2=""
    if not product.image3:
        product.image3=""

    detail_list =(product.description).split(",")
    product.detail=detail_list   
    products = Product.objects.exclude(pk=product_id)
    return render(request, 'product.html', {'product': product, 'products':products})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST) 
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            
            # Check if the username is already taken
            if CustomUser.objects.filter(username=username).exists():
                form.add_error('username', 'This username is already taken.',extra_tags='signup')
                return render(request, 'signup.html', {'form': form})
            
            # Check if the email is already taken
            if CustomUser.objects.filter(email=email).exists():
                form.add_error('email', 'This email address is already registered.')
                return render(request, 'signup.html', {'form': form})
            try:
                user = form.save(commit=False)  # Get the unsaved user object from the form
                user.set_password(form.cleaned_data['password'])  # Hash the password
                user.save()
                return redirect('login')  # Redirect to login page after successful registration
            except Exception as e:
                # Log the error for debugging
                print(f"An error occurred while saving user data: {e}")
                # Handle the error gracefully, such as displaying an error message to the user
                return HttpResponse("An error occurred while processing your request. Please try again later.", status=500)
        else:
            print(form)
            print('Form contains are invalid')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        if username_or_email and password:
            if '@' in username_or_email:
                try:
                    user = CustomUser.objects.get(email=username_or_email)
                except CustomUser.DoesNotExist:
                    messages.error(request, 'Login failed: User does not exist', extra_tags='login_message')
            else:
                try:
                    user = CustomUser.objects.get(username=username_or_email)
                except CustomUser.DoesNotExist:
                    messages.error(request, 'Login failed: User does not exist', extra_tags='login_message')

            if user.check_password(password):
                login(request, user)
                return redirect('home')  # Redirect to the 'store' page upon successful login
            else:
                messages.error(request, 'Login failed: User does not exist', extra_tags='login_message')
        else:
            messages.error(request, 'Login failed: User does not exist', extra_tags='login_message')
  
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER', '/'))

def search_view(request):
    if request.user.is_authenticated:
        favourite=FavoriteItem.objects.filter(user=request.user)
    else:
        favourite=[]
    root_categories = RootCategory.objects.all()
    query = request.GET.get('query')
    products = []
    if query:
        products = Product.objects.filter(title__icontains=query)
    else:
        products = Product.objects.all()
    return render(request, 'search.html', {'query': query, 'products': products, 'rcat':root_categories, 'fav':favourite})


@login_required
def cart_view(request):
    user = request.user
    cart_items = CartItem.objects.filter(cart__user=user)
    return render(request, 'cart.html', {'cart_items': cart_items})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def delete_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    print(cart_item)
    cart = cart_item.cart
    print(cart)
    cart_item.delete()
    if cart.items.count() == 0:
        cart.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def rent(request,product_id,quantity=1):
    product = get_object_or_404(Product, pk=product_id)
    for _ in range(quantity):
        add_to_cart(request,product_id=product.product_id)
    return redirect('cart')

@login_required
def myacc_view(request):
    return render(request, 'myaccount.html')

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def mycart(request):
    user = request.user
    cart_items = CartItem.objects.filter(cart__user=user)
    return render(request, 'accart.html', {'cart_items': cart_items})

@login_required
def order_view(request):
    if request.method == 'POST':
        selected_items_list =cache.get('selected_items_list')
        print(selected_items_list)
        order = Order.objects.create(user=request.user, total_price='100')
        for item_data in selected_items_list:
            cart_item_id = item_data.id
            quantity = item_data.quantity

            cart_item = get_object_or_404(CartItem, pk=cart_item_id)
            product = cart_item.product

            # Decrease the quantity of the product
            product.available_quantity -= quantity
            product.save()

            # Create OrderItem
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

            # Optionally, you may want to delete the cart item after ordering
            cart_item.delete()
        print("Order placed successfully")
    user_orders = Order.objects.filter(user=request.user)
    return render(request, 'order.html',{'user_orders':user_orders})


@login_required
def checkout(request):
    selected_items_list = []
    if request.method == 'POST':
        selected_items_ids = request.POST.getlist('selected_items')
        quantities = {}
        # Iterate over each selected item ID and retrieve its quantity from the POST data
        for item_id in selected_items_ids:
            quantity_key = f'quantity-{item_id}'
            quantity = request.POST.get(quantity_key)
            if quantity:
                quantities[item_id] = int(quantity)
        
        selected_items = CartItem.objects.filter(id__in=selected_items_ids)
        
        for item in selected_items:
            item.quantity = quantities.get(str(item.id), 1)  # Default quantity to 1 if not found
            selected_items_list.append(item)
    cache.set('selected_items_list',selected_items_list)
    print(selected_items_list)   
    return render(request, 'checkout.html', {'cart_items1': selected_items_list})




@login_required
def changepass(request):
    if request.method == 'POST':
        # Retrieve old password, new password, and confirm new password from the POST request
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        if request.user.check_password(old_password):
            if new_password1 == new_password2:
                request.user.set_password(new_password1)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Your password was successfully updated!', extra_tags="changepass_message")
                return redirect('changepass')  # Redirect to profile page after successful password change
            else:
                messages.error(request, "New passwords don't match.", extra_tags='changepass_message')
        else:
            messages.error(request, 'Incorrect old password.', extra_tags='changepass_message')
    else:
        # Handle GET request
        return render(request, 'changepassword.html')
    return render(request, 'changepassword.html')

@login_required
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user = request.user
    favorite_item, created = FavoriteItem.objects.get_or_create(user=user, product=product)
    if created:
        messages.success(request, f"{product.title} has been added to your favorites!")
    else:
        favorite_item.delete()
        messages.info(request, f"{product.title} has been removed from your favorites.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def rent_view(request):
    user_orders = Order.objects.filter(user=request.user, status='Delivered')
    return render(request, 'rent.html',{'user_orders':user_orders})

@login_required
def favourite_view(request):
    favourite=FavoriteItem.objects.filter(user=request.user)
    return render(request, 'favourite.html',{'favourite':favourite})