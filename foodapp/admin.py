from django.contrib import admin
from django.db.models import Sum
from .models import UserProfile, Hotel, Category, FoodItem, Combo, Coupon, DeliveryPartner, Order, OrderItem, Payment, Favourite, Review

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'date_of_birth', 'gender')
    search_fields = ('user__username', 'phone_number')

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'delivery_time', 'delivery_charges', 'distance', 'is_veg_only', 'featured')
    list_filter = ('is_veg_only', 'has_non_veg', 'featured')
    search_fields = ('name', 'address')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'category', 'price', 'rating', 'is_veg', 'is_trending')
    list_filter = ('is_veg', 'is_trending', 'category', 'hotel')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_trending')

@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_price')
    search_fields = ('name', 'description')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'active', 'expiry_date', 'min_purchase_amount')
    list_filter = ('active', 'expiry_date')
    search_fields = ('code', 'description')

@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'vehicle_number', 'vehicle_type', 'rating')
    search_fields = ('name', 'vehicle_number')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'hotel', 'order_date', 'status', 'total_amount', 'grand_total', 'payment_method')
    list_filter = ('status', 'payment_method', 'order_date', 'hotel')
    search_fields = ('id', 'user__username', 'phone_number', 'delivery_address')
    inlines = [OrderItemInline]
    readonly_fields = ('order_date',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'transaction_id', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'order__id')

@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'food_item', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'food_item__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'hotel', 'food_item', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'comment')
