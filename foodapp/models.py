from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    saved_address = models.TextField(blank=True, null=True)
    landmark = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.user.username

class Hotel(models.Model):
    name = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.0, validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    delivery_time = models.IntegerField(help_text="In minutes")
    delivery_charges = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    distance = models.DecimalField(max_digits=4, decimal_places=1, help_text="In km")
    is_veg_only = models.BooleanField(default=False)
    has_non_veg = models.BooleanField(default=True)
    image = models.ImageField(upload_to='hotels/', blank=True, null=True, default='hotels/default_hotel.jpg')
    description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True, default='categories/default_category.jpg')
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name

class FoodItem(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='menu_items')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='food_items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.0, validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    is_veg = models.BooleanField(default=True)
    preparation_time = models.IntegerField(help_text="In minutes")
    image = models.ImageField(upload_to='foods/', blank=True, null=True, default='foods/default_food.jpg')
    is_trending = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.hotel.name}"

class Combo(models.Model):
    name = models.CharField(max_length=100)
    food_items = models.ManyToManyField(FoodItem, related_name='combos')
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discount_price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='combos/', blank=True, null=True, default='combos/default_combo.jpg')
    
    def __str__(self):
        return self.name

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    active = models.BooleanField(default=True)
    expiry_date = models.DateField()
    min_purchase_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    description = models.CharField(max_length=100, blank=True, null=True)

    def is_valid(self):
        return self.active and self.expiry_date >= timezone.now().date()
        
    def __str__(self):
        return self.code

class DeliveryPartner(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    vehicle_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=50, default='Bike')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.5)
    photo = models.ImageField(upload_to='partners/', blank=True, null=True, default='partners/default_partner.jpg')
    
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('Placed', 'Order Placed'),
        ('Accepted', 'Restaurant Accepted'),
        ('Preparing', 'Food Being Prepared'),
        ('PickedUp', 'Picked Up'),
        ('OutForDelivery', 'Out For Delivery'),
        ('Delivered', 'Delivered'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Placed')
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    delivery_charges = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    gst_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    delivery_address = models.TextField()
    landmark = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    instructions = models.TextField(blank=True, null=True)
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    estimated_arrival_time = models.IntegerField(default=30, help_text="In minutes")
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.food_item.name} (Order #{self.order.id})"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Guest Cart {self.session_key}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.food_item.name}"

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.status}"

class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'food_item')
        
    def __str__(self):
        return f"{self.user.username} liked {self.food_item.name}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        target = self.hotel.name if self.hotel else self.food_item.name
        return f"Review by {self.user.username} on {target} ({self.rating}/5)"
