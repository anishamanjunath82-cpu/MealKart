import os
import django
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mealKart.settings')
django.setup()

from django.contrib.auth.models import User
from foodapp.models import UserProfile, Hotel, Category, FoodItem, Coupon, DeliveryPartner
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

def generate_placeholders():
    print("Generating placeholder images...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Paths for media
    media_paths = {
        'hotel': os.path.join(base_dir, 'media', 'hotels', 'default_hotel.jpg'),
        'category': os.path.join(base_dir, 'media', 'categories', 'default_category.jpg'),
        'food': os.path.join(base_dir, 'media', 'foods', 'default_food.jpg'),
        'partner': os.path.join(base_dir, 'media', 'partners', 'default_partner.jpg'),
    }
    
    # Paths for static/images
    static_paths = {
        'hotel': os.path.join(base_dir, 'static', 'images', 'default_hotel.jpg'),
        'food': os.path.join(base_dir, 'static', 'images', 'default_food.jpg'),
        'category': os.path.join(base_dir, 'static', 'images', 'default_category.jpg'),
        'partner': os.path.join(base_dir, 'static', 'images', 'default_partner.jpg'),
        'hero_biryani': os.path.join(base_dir, 'static', 'images', 'hero_biryani.jpg'),
        'hero_pizza': os.path.join(base_dir, 'static', 'images', 'hero_pizza.jpg'),
        'hero_burger': os.path.join(base_dir, 'static', 'images', 'hero_burger.jpg'),
    }

    # Helper function to write simple colored PNGs
    def save_colored_img(path, text, bg_color, size=(600, 400)):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img = Image.new('RGB', size, color=bg_color)
        draw = ImageDraw.Draw(img)
        # Inner white border
        draw.rectangle([15, 15, size[0]-15, size[1]-15], outline=(255, 255, 255), width=3)
        
        # Text drawing
        try:
            font = ImageFont.load_default()
        except:
            font = None
            
        draw.text((30, size[1]//2 - 10), text, fill=(255, 255, 255), font=font)
        img.save(path, 'JPEG', quality=85)

    # 1. Media placeholders
    save_colored_img(media_paths['hotel'], "mealKart - Restaurant", (255, 76, 48))
    save_colored_img(media_paths['category'], "mealKart - Category", (40, 167, 69))
    save_colored_img(media_paths['food'], "mealKart - Delicious Food", (0, 123, 255))
    save_colored_img(media_paths['partner'], "mealKart - Delivery Captain", (108, 117, 125))

    # 2. Static placeholders
    save_colored_img(static_paths['hotel'], "mealKart - Restaurant", (255, 76, 48))
    save_colored_img(static_paths['food'], "mealKart - Delicious Food", (0, 123, 255))
    save_colored_img(static_paths['category'], "mealKart - Category", (40, 167, 69))
    save_colored_img(static_paths['partner'], "mealKart - Delivery Captain", (108, 117, 125))
    
    # Hero sliders images
    save_colored_img(static_paths['hero_biryani'], "Royal Spicy Biryani - Flat 50% Off", (44, 24, 16), size=(1200, 600))
    save_colored_img(static_paths['hero_pizza'], "Cheesy Hot Pizza Combo - Buy 1 Get 1 Free", (24, 44, 16), size=(1200, 600))
    save_colored_img(static_paths['hero_burger'], "Juicy Gourmet Burgers - Free Delivery", (16, 24, 44), size=(1200, 600))
    
    print("Placeholder images generated successfully.")

def seed_database():
    print("Seeding database records...")
    
    # 1. Create Superuser (admin/adminpass) if not exists
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@mealkart.pro', 'adminpass')
        admin.first_name = "System"
        admin.last_name = "Admin"
        admin.save()
        UserProfile.objects.get_or_create(user=admin, phone_number="9999999999", saved_address="System Head Office, New Delhi")
        print("Superuser created (User: admin, Pass: adminpass)")
    else:
        print("Superuser already exists.")

    # 2. Create Categories
    categories_data = ['Pizza', 'Burgers', 'Biryani', 'Chinese', 'Desserts', 'Beverages']
    categories = {}
    for cat_name in categories_data:
        cat, created = Category.objects.get_or_create(name=cat_name)
        categories[cat_name] = cat
    print(f"Created/Verified {len(categories)} categories.")

    # 3. Create Hotels
    hotels_data = [
        {
            'name': 'Pizza Palazzo',
            'rating': Decimal('4.40'),
            'delivery_time': 25,
            'delivery_charges': Decimal('30.00'),
            'distance': Decimal('2.4'),
            'is_veg_only': False,
            'has_non_veg': True,
            'description': 'Delicious wood-fired pizzas, garlic breads, and pasta specials.',
            'address': 'G Block, Connaught Place, New Delhi',
            'featured': True
        },
        {
            'name': 'Royal Biryani House',
            'rating': Decimal('4.60'),
            'delivery_time': 30,
            'delivery_charges': Decimal('40.00'),
            'distance': Decimal('1.8'),
            'is_veg_only': False,
            'has_non_veg': True,
            'description': 'Authentic Hyderabadi and Lucknowi Biryanis cooked in traditional dum style.',
            'address': 'Daryaganj, Old Delhi',
            'featured': True
        },
        {
            'name': 'Burger Bistro',
            'rating': Decimal('4.20'),
            'delivery_time': 20,
            'delivery_charges': Decimal('20.00'),
            'distance': Decimal('3.1'),
            'is_veg_only': False,
            'has_non_veg': True,
            'description': 'Premium gourmet burgers, crispy loaded fries, and signature milkshakes.',
            'address': 'Saket District Centre, New Delhi',
            'featured': False
        },
        {
            'name': 'Golden Dragon Chinese',
            'rating': Decimal('4.10'),
            'delivery_time': 35,
            'delivery_charges': Decimal('45.00'),
            'distance': Decimal('4.5'),
            'is_veg_only': False,
            'has_non_veg': True,
            'description': 'Spicy Hakka Noodles, Manchurian, Spring Rolls, and dimsums.',
            'address': 'Rajouri Garden, New Delhi',
            'featured': False
        },
        {
            'name': 'Sweet Delights',
            'rating': Decimal('4.50'),
            'delivery_time': 15,
            'delivery_charges': Decimal('15.00'),
            'distance': Decimal('1.2'),
            'is_veg_only': True,
            'has_non_veg': False,
            'description': '100% pure vegetarian waffles, pancakes, cakes, and ice creams.',
            'address': 'Vasant Kunj, New Delhi',
            'featured': True
        }
    ]
    
    hotels = {}
    for h_data in hotels_data:
        hotel, created = Hotel.objects.get_or_create(name=h_data['name'], defaults=h_data)
        if not created:
            # Update fields
            for key, val in h_data.items():
                setattr(hotel, key, val)
            hotel.save()
        hotels[h_data['name']] = hotel
    print(f"Created/Updated {len(hotels)} restaurants.")

    # 4. Create Food Items
    foods_data = [
        # Pizza Palazzo
        {
            'hotel': 'Pizza Palazzo',
            'category': 'Pizza',
            'name': 'Margherita Pizza',
            'description': 'Classic cheese pizza topped with mozzarella and fresh basil leaves.',
            'price': Decimal('199.00'),
            'rating': Decimal('4.50'),
            'is_veg': True,
            'preparation_time': 15,
            'is_trending': True
        },
        {
            'hotel': 'Pizza Palazzo',
            'category': 'Pizza',
            'name': 'Pepperoni Feast Pizza',
            'description': 'Double pepperoni topped with stringy mozzarella cheese and pizza sauce.',
            'price': Decimal('299.00'),
            'rating': Decimal('4.60'),
            'is_veg': False,
            'preparation_time': 20,
            'is_trending': True
        },
        {
            'hotel': 'Pizza Palazzo',
            'category': 'Pizza',
            'name': 'Veggie Supreme Pizza',
            'description': 'Loaded with onions, bell peppers, tomatoes, mushrooms, and black olives.',
            'price': Decimal('249.00'),
            'rating': Decimal('4.30'),
            'is_veg': True,
            'preparation_time': 18,
            'is_trending': False
        },
        {
            'hotel': 'Pizza Palazzo',
            'category': 'Beverages',
            'name': 'Garlic Bread Stix',
            'description': 'Baked fresh with garlic butter, served with a cheesy dip.',
            'price': Decimal('99.00'),
            'rating': Decimal('4.20'),
            'is_veg': True,
            'preparation_time': 10,
            'is_trending': False
        },

        # Royal Biryani House
        {
            'hotel': 'Royal Biryani House',
            'category': 'Biryani',
            'name': 'Special Chicken Dum Biryani',
            'description': 'Richly flavored basmati rice layered with marinated chicken, saffron, and ghee.',
            'price': Decimal('279.00'),
            'rating': Decimal('4.80'),
            'is_veg': False,
            'preparation_time': 25,
            'is_trending': True
        },
        {
            'hotel': 'Royal Biryani House',
            'category': 'Biryani',
            'name': 'Aromatic Veg Dum Biryani',
            'description': 'Fresh vegetables slow-cooked in dum style with long grain basmati rice.',
            'price': Decimal('219.00'),
            'rating': Decimal('4.40'),
            'is_veg': True,
            'preparation_time': 20,
            'is_trending': False
        },
        {
            'hotel': 'Royal Biryani House',
            'category': 'Biryani',
            'name': 'Mutton Keema Biryani',
            'description': 'Delicate minced mutton cooked with traditional Indian spices and layered with rice.',
            'price': Decimal('349.00'),
            'rating': Decimal('4.70'),
            'is_veg': False,
            'preparation_time': 30,
            'is_trending': True
        },

        # Burger Bistro
        {
            'hotel': 'Burger Bistro',
            'category': 'Burgers',
            'name': 'Classic Crunch Chicken Burger',
            'description': 'Crispy fried chicken breast fillet topped with lettuce and mayo on a toasted bun.',
            'price': Decimal('149.00'),
            'rating': Decimal('4.30'),
            'is_veg': False,
            'preparation_time': 12,
            'is_trending': True
        },
        {
            'hotel': 'Burger Bistro',
            'category': 'Burgers',
            'name': 'Double Cheese Aloo Tikki Burger',
            'description': 'Crispy potato patty layered with two cheese slices, onion rings, and secret sauce.',
            'price': Decimal('119.00'),
            'rating': Decimal('4.10'),
            'is_veg': True,
            'preparation_time': 10,
            'is_trending': False
        },
        {
            'hotel': 'Burger Bistro',
            'category': 'Burgers',
            'name': 'Peri Peri Crispy French Fries',
            'description': 'Perfectly salted crispy fries tossed in a spicy peri peri seasoning.',
            'price': Decimal('89.00'),
            'rating': Decimal('4.40'),
            'is_veg': True,
            'preparation_time': 8,
            'is_trending': True
        },

        # Golden Dragon Chinese
        {
            'hotel': 'Golden Dragon Chinese',
            'category': 'Chinese',
            'name': 'Spicy Schezwan Hakka Noodles',
            'description': 'Stir-fried noodles with assorted vegetables, egg ribbons, and a spicy schezwan sauce.',
            'price': Decimal('179.00'),
            'rating': Decimal('4.20'),
            'is_veg': False,
            'preparation_time': 15,
            'is_trending': False
        },
        {
            'hotel': 'Golden Dragon Chinese',
            'category': 'Chinese',
            'name': 'Veg Manchurian Gravy',
            'description': 'Deep-fried vegetable balls simmered in a tangy, spicy soy-garlic gravy.',
            'price': Decimal('159.00'),
            'rating': Decimal('4.00'),
            'is_veg': True,
            'preparation_time': 18,
            'is_trending': False
        },

        # Sweet Delights
        {
            'hotel': 'Sweet Delights',
            'category': 'Desserts',
            'name': 'Molten Chocolate Lava Cake',
            'description': 'Indulgent cake with a warm, gooey liquid chocolate core.',
            'price': Decimal('129.00'),
            'rating': Decimal('4.70'),
            'is_veg': True,
            'preparation_time': 8,
            'is_trending': True
        },
        {
            'hotel': 'Sweet Delights',
            'category': 'Desserts',
            'name': 'Warm Gulab Jamun (3 Pcs)',
            'description': 'Traditional soft milk-solid balls soaked in sweet cardamom-infused sugar syrup.',
            'price': Decimal('79.00'),
            'rating': Decimal('4.60'),
            'is_veg': True,
            'preparation_time': 5,
            'is_trending': False
        },
        {
            'hotel': 'Sweet Delights',
            'category': 'Desserts',
            'name': 'Belgian Chocolate Waffles',
            'description': 'Crispy bubble waffle topped with melted dark Belgian chocolate and icing sugar.',
            'price': Decimal('149.00'),
            'rating': Decimal('4.50'),
            'is_veg': True,
            'preparation_time': 12,
            'is_trending': True
        }
    ]

    for f_data in foods_data:
        h_name = f_data.pop('hotel')
        c_name = f_data.pop('category')
        hotel = hotels[h_name]
        category = categories[c_name]
        
        food, created = FoodItem.objects.get_or_create(
            hotel=hotel,
            name=f_data['name'],
            defaults={
                'category': category,
                'description': f_data['description'],
                'price': f_data['price'],
                'rating': f_data['rating'],
                'is_veg': f_data['is_veg'],
                'preparation_time': f_data['preparation_time'],
                'is_trending': f_data['is_trending']
            }
        )
        
        # Restore dict for console print / loop consistency
        f_data['hotel'] = h_name
        f_data['category'] = c_name
        
    print(f"Created/Verified {len(foods_data)} menu items.")

    # 5. Create Promo Coupons
    coupons_data = [
        {
            'code': 'WELCOME50',
            'discount_percentage': 50,
            'active': True,
            'expiry_date': timezone.now().date() + timezone.timedelta(days=90),
            'min_purchase_amount': Decimal('200.00'),
            'description': 'Flat 50% discount on your first order. Grab it!'
        },
        {
            'code': 'PIZZA20',
            'discount_percentage': 20,
            'active': True,
            'expiry_date': timezone.now().date() + timezone.timedelta(days=30),
            'min_purchase_amount': Decimal('350.00'),
            'description': 'Craving Pizza? Get 20% off on your pizza orders.'
        },
        {
            'code': 'FREEDEL',
            'discount_percentage': 100,
            'active': True,
            'expiry_date': timezone.now().date() + timezone.timedelta(days=60),
            'min_purchase_amount': Decimal('500.00'),
            'description': 'Free delivery plus extra savings on orders over ₹500.'
        }
    ]

    for c_data in coupons_data:
        coupon, created = Coupon.objects.get_or_create(code=c_data['code'], defaults=c_data)
        if not created:
            for key, val in c_data.items():
                setattr(coupon, key, val)
            coupon.save()
            
    print(f"Created/Verified {len(coupons_data)} promotional coupons.")

    # 6. Create Delivery Partners
    partners_data = [
        {
            'name': 'Ramesh Kumar',
            'phone_number': '9876543210',
            'vehicle_number': 'DL-3C-AS-4512',
            'vehicle_type': 'Motorcycle',
            'rating': Decimal('4.80')
        },
        {
            'name': 'Vikram Singh',
            'phone_number': '9876543222',
            'vehicle_number': 'DL-4S-BN-8754',
            'vehicle_type': 'Electric Scooter',
            'rating': Decimal('4.60')
        }
    ]

    for p_data in partners_data:
        partner, created = DeliveryPartner.objects.get_or_create(name=p_data['name'], defaults=p_data)
        if not created:
            for key, val in p_data.items():
                setattr(partner, key, val)
            partner.save()
            
    print(f"Created/Verified {len(partners_data)} delivery partners.")

if __name__ == '__main__':
    generate_placeholders()
    seed_database()
    print("Database seeding completed successfully!")
