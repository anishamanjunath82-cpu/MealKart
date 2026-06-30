import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mealKart.settings')
django.setup()

from foodapp.forms import SignupForm
from django.contrib.auth.models import User

def run_tests():
    print("--- Testing Password Strength Validation ---")
    
    # Clean database entries that might interfere
    User.objects.filter(username='testbuyer_strength').delete()
    User.objects.filter(email='strength@test.com').delete()

    base_data = {
        'full_name': 'Strength Tester',
        'email': 'strength@test.com',
        'phone_number': '+919876543210',
        'date_of_birth': '1995-05-15',
        'gender': 'M',
        'username': 'testbuyer_strength',
    }

    test_cases = [
        ('123', False, "Too short"),
        ('short1!', False, "No uppercase"),
        ('SHORT12!', False, "No lowercase"),
        ('ShortPass!', False, "No numbers"),
        ('ShortPass12', False, "No special characters"),
        ('MealKart@2026', True, "Valid Strong Password"),
    ]

    failures = 0
    for pwd, expected_valid, desc in test_cases:
        data = base_data.copy()
        data['password'] = pwd
        data['confirm_password'] = pwd
        
        form = SignupForm(data=data)
        is_valid = form.is_valid()
        
        # Check if validation succeeded/failed as expected
        # (note: is_valid cleans all fields, so if password is valid, form should be valid)
        password_errors = form.errors.get('password')
        
        if expected_valid:
            if password_errors:
                print(f"[FAIL] Password '{pwd}' ({desc}) expected valid, but got errors: {password_errors}")
                failures += 1
            else:
                print(f"[PASS] Password '{pwd}' ({desc}) accepted as strong.")
        else:
            if not password_errors:
                print(f"[FAIL] Password '{pwd}' ({desc}) expected invalid, but form accepted it.")
                failures += 1
            else:
                print(f"[PASS] Password '{pwd}' ({desc}) rejected correctly. Error: {password_errors[0]}")
                
    print("--------------------------------------------")
    if failures == 0:
        print("ALL FORM PASSWORD STRENGTH TESTS PASSED!")
    else:
        print(f"FAILED {failures} test case(s).")
        
if __name__ == '__main__':
    run_tests()
