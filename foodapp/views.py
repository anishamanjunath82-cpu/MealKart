from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg, Count, Sum
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import random
import uuid

from .models import (
    UserProfile, Hotel, Category, FoodItem, Combo, Coupon,
    DeliveryPartner, Order, OrderItem, Cart, CartItem, Payment, Favourite, Review
)
from .forms import SignupForm, LoginForm, UserProfileForm

# --- Authentication Views ---

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please Sign In.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()
    return render(request, 'auth/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('user')
            remember_me = form.cleaned_data.get('remember_me')
            login(request, user)
            
            if not remember_me:
                request.session.set_expiry(0) # Expiries when browser closes
                
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username/email or password.")
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        step = request.POST.get('step')
        
        if step == 'request':
            try:
                user = User.objects.get(email=email)
                # Simulate OTP sending
                otp = str(random.randint(100000, 999999))
                request.session['reset_email'] = email
                request.session['reset_otp'] = otp
                # For demo purposes, print OTP in console and show it as message
                print(f"PASSWORD RESET OTP FOR {email}: {otp}")
                messages.success(request, f"OTP sent successfully to {email}! [Demo OTP: {otp}]")
                return render(request, 'auth/forgot_password.html', {'step': 'verify', 'email': email})
            except User.DoesNotExist:
                messages.error(request, "No account found with this email address.")
                
        elif step == 'verify':
            entered_otp = request.POST.get('otp')
            session_otp = request.session.get('reset_otp')
            if entered_otp == session_otp:
                messages.success(request, "OTP verified! Please enter your new password.")
                return render(request, 'auth/forgot_password.html', {'step': 'reset'})
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                return render(request, 'auth/forgot_password.html', {'step': 'verify', 'email': request.session.get('reset_email')})
                
        elif step == 'reset':
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            email = request.session.get('reset_email')
            
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'auth/forgot_password.html', {'step': 'reset'})
                
            import re
            if (len(new_password) < 8 or 
                not re.search(r'[A-Z]', new_password) or 
                not re.search(r'[a-z]', new_password) or 
                not re.search(r'\d', new_password) or 
                not re.search(r'[@$!%*?&#]', new_password)):
                messages.error(request, "Password must be at least 8 characters and include uppercase, lowercase, digit, and special character.")
                return render(request, 'auth/forgot_password.html', {'step': 'reset'})
                
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                # Clean up session
                del request.session['reset_email']
                del request.session['reset_otp']
                messages.success(request, "Password reset successful! You can now login.")
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, "An error occurred. Please try again.")
                return redirect('forgot_password')
                
    return render(request, 'auth/forgot_password.html', {'step': 'request'})

# --- Home & Restaurant Views ---

@login_required
def home_view(request):
    categories = Category.objects.all()
    hotels = Hotel.objects.all()
    trending_foods = FoodItem.objects.filter(is_trending=True)[:10]
    combos = Combo.objects.all()
    coupons = Coupon.objects.filter(active=True, expiry_date__gte=timezone.now().date())
    
    # Get user favorites
    fav_ids = Favourite.objects.filter(user=request.user).values_list('food_item_id', flat=True)
    
    # Cart details for navigation
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_count = cart.items.aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

    # User Profile logic (create if missing)
    UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'categories': categories,
        'hotels': hotels,
        'trending_foods': trending_foods,
        'combos': combos,
        'coupons': coupons,
        'fav_ids': fav_ids,
        'cart_count': cart_count,
        'user': request.user
    }
    return render(request, 'home.html', context)

@login_required
def hotel_menu_view(request, hotel_id):
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    food_items = hotel.menu_items.all()
    reviews = hotel.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or hotel.rating
    
    # Categories available in this hotel's menu
    hotel_categories = Category.objects.filter(food_items__hotel=hotel).distinct()
    
    fav_ids = Favourite.objects.filter(user=request.user).values_list('food_item_id', flat=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_count = cart.items.aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
    
    # Handle Review Submission
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            Review.objects.create(
                user=request.user,
                hotel=hotel,
                rating=int(rating),
                comment=comment
            )
            # Update hotel rating average
            avg = hotel.reviews.aggregate(Avg('rating'))['rating__avg']
            if avg:
                hotel.rating = avg
                hotel.save()
            messages.success(request, "Review submitted successfully!")
            return redirect('hotel_menu', hotel_id=hotel.id)
            
    context = {
        'hotel': hotel,
        'food_items': food_items,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'hotel_categories': hotel_categories,
        'fav_ids': fav_ids,
        'cart_count': cart_count
    }
    return render(request, 'menu.html', context)

# --- Dynamic Search API ---

@login_required
def search_api(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    
    foods = FoodItem.objects.all()
    
    if category_id:
        foods = foods.filter(category_id=category_id)
        
    if query:
        foods = foods.filter(
            Q(name__icontains=query) |
            Q(hotel__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(description__icontains=query)
        )
        
    fav_ids = list(Favourite.objects.filter(user=request.user).values_list('food_item_id', flat=True))
    
    food_list = []
    for food in foods:
        food_list.append({
            'id': food.id,
            'name': food.name,
            'description': food.description,
            'price': float(food.price),
            'rating': float(food.rating),
            'image': food.image.url if food.image else '/static/images/default_food.jpg',
            'hotel_id': food.hotel.id,
            'hotel_name': food.hotel.name,
            'category_name': food.category.name if food.category else 'General',
            'is_veg': food.is_veg,
            'preparation_time': food.preparation_time,
            'is_favorite': food.id in fav_ids
        })
        
    return JsonResponse({'results': food_list})

# --- Wishlist / Favorites API ---

@login_required
def toggle_favorite(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        food_id = data.get('food_id')
        food_item = get_object_or_404(FoodItem, pk=food_id)
        
        fav, created = Favourite.objects.get_or_create(user=request.user, food_item=food_item)
        
        if not created:
            fav.delete()
            is_favorite = False
        else:
            is_favorite = True
            
        return JsonResponse({'success': True, 'is_favorite': is_favorite})
    return JsonResponse({'error': 'Invalid Request'}, status=400)

# --- Shopping Cart Views & API ---

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all().select_related('food_item', 'food_item__hotel')
    
    # Calculate costs
    subtotal = sum(item.food_item.price * item.quantity for item in items)
    
    # Calculate GST (18%)
    gst = subtotal * Decimal('0.18')
    
    # Flat delivery charge (free over 500, or average 40)
    delivery_charge = Decimal('40.00') if subtotal < 500 and subtotal > 0 else Decimal('0.00')
    
    # Check for coupon in session
    coupon_code = request.session.get('coupon_code')
    discount = Decimal('0.00')
    coupon_error = None
    applied_coupon = None
    
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code, active=True, expiry_date__gte=timezone.now().date())
            if subtotal >= coupon.min_purchase_amount:
                discount = subtotal * (Decimal(coupon.discount_percentage) / Decimal('100.00'))
                applied_coupon = coupon
            else:
                coupon_error = f"Minimum order value of ₹{coupon.min_purchase_amount} required for this coupon."
                del request.session['coupon_code']
        except Coupon.DoesNotExist:
            coupon_error = "Invalid or expired coupon code."
            del request.session['coupon_code']
            
    grand_total = subtotal - discount + gst + delivery_charge
    
    context = {
        'items': items,
        'subtotal': round(subtotal, 2),
        'gst': round(gst, 2),
        'delivery_charge': round(delivery_charge, 2),
        'discount': round(discount, 2),
        'grand_total': round(max(grand_total, 0), 2),
        'applied_coupon': applied_coupon,
        'coupon_error': coupon_error,
    }
    return render(request, 'cart.html', context)

from decimal import Decimal

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        food_id = data.get('food_id')
        quantity = int(data.get('quantity', 1))
        
        food_item = get_object_or_404(FoodItem, pk=food_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if cart already has items from a DIFFERENT hotel
        cart_items = cart.items.all()
        if cart_items.exists():
            first_item = cart_items.first()
            if first_item.food_item.hotel != food_item.hotel:
                # Ask user if they want to clear cart (we will handle it by clearing cart in this demo)
                cart.items.all().delete()
                
        cart_item, created = CartItem.objects.get_or_create(cart=cart, food_item=food_item)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        
        total_count = cart.items.aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
        return JsonResponse({'success': True, 'cart_count': total_count, 'message': f"{food_item.name} added to cart!"})
        
    return JsonResponse({'error': 'Invalid Request'}, status=400)

@login_required
def update_cart_item(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        item_id = data.get('item_id')
        action = data.get('action') # 'increase', 'decrease', 'remove'
        
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        
        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        elif action == 'remove':
            cart_item.delete()
            
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()
        subtotal = sum(item.food_item.price * item.quantity for item in items)
        gst = subtotal * Decimal('0.18')
        delivery_charge = Decimal('40.00') if subtotal < 500 and subtotal > 0 else Decimal('0.00')
        
        # Recalculate coupon
        coupon_code = request.session.get('coupon_code')
        discount = Decimal('0.00')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
                if subtotal >= coupon.min_purchase_amount:
                    discount = subtotal * (Decimal(coupon.discount_percentage) / Decimal('100.00'))
                else:
                    del request.session['coupon_code']
            except Coupon.DoesNotExist:
                del request.session['coupon_code']
                
        grand_total = subtotal - discount + gst + delivery_charge
        cart_count = cart.items.aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
        
        return JsonResponse({
            'success': True,
            'quantity': cart_item.quantity if cart_item.id and action != 'remove' and cart_item.quantity > 0 else 0,
            'subtotal': float(subtotal),
            'gst': float(gst),
            'delivery_charge': float(delivery_charge),
            'discount': float(discount),
            'grand_total': float(max(grand_total, 0)),
            'cart_count': cart_count
        })
    return JsonResponse({'error': 'Invalid Request'}, status=400)

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        code = data.get('coupon_code', '').strip()
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        subtotal = sum(item.food_item.price * item.quantity for item in cart.items.all())
        
        try:
            coupon = Coupon.objects.get(code__iexact=code, active=True, expiry_date__gte=timezone.now().date())
            if subtotal >= coupon.min_purchase_amount:
                request.session['coupon_code'] = coupon.code
                return JsonResponse({'success': True, 'message': f"Coupon '{coupon.code}' applied successfully!"})
            else:
                return JsonResponse({'success': False, 'message': f"Minimum order value of ₹{coupon.min_purchase_amount} required."})
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': "Invalid or expired coupon code."})
            
    return JsonResponse({'error': 'Invalid Request'}, status=400)

@login_required
def remove_coupon(request):
    if request.method == 'POST':
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
        return JsonResponse({'success': True, 'message': "Coupon removed."})
    return JsonResponse({'error': 'Invalid Request'}, status=400)

# --- Checkout & Payment Flow ---

@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.all()
    if not items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')
        
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    subtotal = sum(item.food_item.price * item.quantity for item in items)
    gst = subtotal * Decimal('0.18')
    delivery_charge = Decimal('40.00') if subtotal < 500 else Decimal('0.00')
    
    coupon_code = request.session.get('coupon_code')
    discount = Decimal('0.00')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code)
            discount = subtotal * (Decimal(coupon.discount_percentage) / Decimal('100.00'))
        except Coupon.DoesNotExist:
            pass
            
    grand_total = subtotal - discount + gst + delivery_charge
    
    if request.method == 'POST':
        address = request.POST.get('delivery_address')
        landmark = request.POST.get('landmark')
        phone = request.POST.get('phone_number')
        instructions = request.POST.get('instructions')
        
        if address and phone:
            # Update user profile details
            profile.saved_address = address
            profile.landmark = landmark
            profile.phone_number = phone
            profile.save()
            
            # Save checkout choices in session temporarily for the payment step
            request.session['checkout_info'] = {
                'address': address,
                'landmark': landmark,
                'phone': phone,
                'instructions': instructions,
                'subtotal': float(subtotal),
                'gst': float(gst),
                'delivery_charge': float(delivery_charge),
                'discount': float(discount),
                'grand_total': float(grand_total)
            }
            return redirect('payment')
        else:
            messages.error(request, "Please enter your delivery address and phone number.")
            
    context = {
        'items': items,
        'profile': profile,
        'grand_total': round(grand_total, 2)
    }
    return render(request, 'checkout.html', context)

@login_required
def payment_view(request):
    checkout_info = request.session.get('checkout_info')
    if not checkout_info:
        messages.warning(request, "Please fill in checkout details first.")
        return redirect('checkout')
        
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if payment_method:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all()
            first_item = cart_items.first()
            hotel = first_item.food_item.hotel
            
            # Create Order
            order = Order.objects.create(
                user=request.user,
                hotel=hotel,
                total_amount=Decimal(str(checkout_info['subtotal'])),
                discount_amount=Decimal(str(checkout_info['discount'])),
                delivery_charges=Decimal(str(checkout_info['delivery_charge'])),
                gst_amount=Decimal(str(checkout_info['gst'])),
                grand_total=Decimal(str(checkout_info['grand_total'])),
                payment_method=payment_method,
                delivery_address=checkout_info['address'],
                landmark=checkout_info['landmark'],
                phone_number=checkout_info['phone'],
                instructions=checkout_info['instructions']
            )
            
            # Create Order Items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    food_item=item.food_item,
                    quantity=item.quantity,
                    price=item.food_item.price
                )
                
            # Create Payment Record
            transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
            status = 'Success' if payment_method != 'COD' else 'Pending'
            Payment.objects.create(
                order=order,
                transaction_id=transaction_id,
                payment_method=payment_method,
                status=status
            )
            
            # Assign a random Delivery Partner
            partners = DeliveryPartner.objects.all()
            if partners.exists():
                order.delivery_partner = random.choice(partners)
                order.save()
                
            # Clear Cart & Coupon Session
            cart.items.all().delete()
            if 'coupon_code' in request.session:
                del request.session['coupon_code']
            del request.session['checkout_info']
            
            # Store latest order ID in session for payment success page
            request.session['latest_order_id'] = order.id
            return redirect('payment_success')
        else:
            messages.error(request, "Please choose a payment method.")
            
    context = {
        'grand_total': checkout_info['grand_total']
    }
    return render(request, 'payment.html', context)

@login_required
def payment_success_view(request):
    order_id = request.session.get('latest_order_id')
    if not order_id:
        return redirect('home')
        
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    context = {
        'order': order,
        'payment': order.payment
    }
    return render(request, 'payment_success.html', context)

# --- Order Tracking Views ---

@login_required
def order_tracking_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    # Simulate step-by-step progress for the demo if it's not Delivered yet
    # We can check order date and increment status if enough time has passed.
    # In a real app, this is done by admin, but for this college project, we can auto-advance
    # the status based on seconds elapsed since order creation to make it feel ALIVE!
    time_diff = (timezone.now() - order.order_date).total_seconds()
    
    # Placed -> 0s
    # Accepted -> 20s
    # Preparing -> 45s
    # PickedUp -> 80s
    # OutForDelivery -> 120s
    # Delivered -> 180s
    
    current_status = order.status
    if current_status != 'Delivered':
        if time_diff >= 180:
            order.status = 'Delivered'
        elif time_diff >= 120:
            order.status = 'OutForDelivery'
        elif time_diff >= 80:
            order.status = 'PickedUp'
        elif time_diff >= 45:
            order.status = 'Preparing'
        elif time_diff >= 20:
            order.status = 'Accepted'
        
        if order.status != current_status:
            order.save()
            
    # Calculate percentage for progress bar
    status_percentages = {
        'Placed': 16,
        'Accepted': 33,
        'Preparing': 50,
        'PickedUp': 66,
        'OutForDelivery': 83,
        'Delivered': 100
    }
    progress_percentage = status_percentages.get(order.status, 0)
    
    # Mock Delivery partner location changes for tracking map
    # We can calculate coordinates close to hotel/user based on progress
    lat_hotel = 12.9716
    lng_hotel = 77.5946
    lat_user = 12.9816
    lng_user = 77.6046
    
    # Calculate partner location interpolation
    frac = progress_percentage / 100.0
    partner_lat = lat_hotel + (lat_user - lat_hotel) * frac
    partner_lng = lng_hotel + (lng_user - lng_hotel) * frac
    
    # Get the user's saved address and hotel's address
    user_address = ""
    if hasattr(request.user, 'profile') and request.user.profile.saved_address:
        user_address = request.user.profile.saved_address
        if request.user.profile.landmark:
            user_address += f", Near {request.user.profile.landmark}"
    
    hotel_address = order.hotel.address if order.hotel.address else f"{order.hotel.name}, New Delhi"

    context = {
        'order': order,
        'progress_percentage': progress_percentage,
        'partner_lat': partner_lat,
        'partner_lng': partner_lng,
        'time_diff': int(time_diff),
        'user_address': user_address,
        'hotel_address': hotel_address,
    }
    return render(request, 'order_tracking.html', context)

# --- Profile & History Views ---

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Failed to update profile. Please verify your inputs.")
    else:
        form = UserProfileForm(instance=profile)
        
    # Get favorite food items
    favorites = Favourite.objects.filter(user=request.user).select_related('food_item', 'food_item__hotel')
    
    # Order history
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    
    context = {
        'form': form,
        'favorites': favorites,
        'orders': orders
    }
    return render(request, 'profile.html', context)

@login_required
def reorder(request, order_id):
    old_order = get_object_or_404(Order, pk=order_id, user=request.user)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Clear existing cart first
    cart.items.all().delete()
    
    # Add old items to cart
    for item in old_order.items.all():
        CartItem.objects.create(
            cart=cart,
            food_item=item.food_item,
            quantity=item.quantity
        )
        
    messages.success(request, f"Added items from Order #{old_order.id} to your cart!")
    return redirect('cart')

# --- Static Pages ---

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if name and email and message:
            # Mock form submission
            messages.success(request, "Thank you for contacting us! We will get back to you shortly.")
            return redirect('contact')
    return render(request, 'contact.html')
