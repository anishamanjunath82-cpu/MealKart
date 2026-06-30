from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import UserProfile
import re

class SignupForm(forms.Form):
    GENDER_CHOICES = [
        ('', 'Select Gender'),
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    full_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-control'}))
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'form-control'}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}))
    saved_address = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Delivery Address (e.g. Hostels, Block A, etc.)', 'class': 'form-control', 'rows': 2}))
    landmark = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Landmark (Optional)', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not re.match(r'^\+?1?\d{9,15}$', phone):
            raise ValidationError("Enter a valid phone number.")
        return phone

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
            if not re.search(r'[A-Z]', password):
                raise ValidationError("Password must contain at least one uppercase letter.")
            if not re.search(r'[a-z]', password):
                raise ValidationError("Password must contain at least one lowercase letter.")
            if not re.search(r'\d', password):
                raise ValidationError("Password must contain at least one digit.")
            if not re.search(r'[@$!%*?&#]', password):
                raise ValidationError("Password must contain at least one special character (e.g. @, $, !, %, *, ?, &, #).")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        full_name = cleaned_data.get('full_name')
        names = full_name.split(' ', 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ''
        
        user = User.objects.create_user(
            username=cleaned_data.get('username'),
            email=cleaned_data.get('email'),
            password=cleaned_data.get('password'),
            first_name=first_name,
            last_name=last_name
        )
        
        UserProfile.objects.create(
            user=user,
            phone_number=cleaned_data.get('phone_number'),
            date_of_birth=cleaned_data.get('date_of_birth'),
            gender=cleaned_data.get('gender'),
            saved_address=cleaned_data.get('saved_address'),
            landmark=cleaned_data.get('landmark')
        )
        return user


class LoginForm(forms.Form):
    username_or_email = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'placeholder': 'Username or Email', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        if username_or_email and password:
            user = None
            # Check if email was entered
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    username = user_obj.username
                except User.DoesNotExist:
                    username = username_or_email
            else:
                username = username_or_email
                
            user = authenticate(username=username, password=password)
            
            if user is None:
                raise ValidationError("Incorrect username/email or password.")
            elif not user.is_active:
                raise ValidationError("This account is inactive.")
            
            cleaned_data['user'] = user
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'date_of_birth', 'gender', 'saved_address', 'landmark']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(choices=UserProfile.GENDER_CHOICES, attrs={'class': 'form-control'}),
            'saved_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'landmark': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile.save()
        return profile
