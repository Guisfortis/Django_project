from datetime import date
from django.db import models
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
    
    
class Hotels(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255, db_index=True)
    phone = PhoneNumberField(verbose_name='phone')
    star_rating = models.IntegerField(db_index=True, validators=[MaxValueValidator(7), 
                                                                 MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)


class Room_types(models.Model):
    hotel = models.ForeignKey('Hotels', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(max_length=255)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,  
        default=Decimal('0.00')
    )
    max_guests = models.IntegerField(db_index=True)
    
    
    def __str__(self):
        return str(self.name)
    

class Rooms(models.Model):
    hotel = models.ForeignKey('Hotels', on_delete=models.CASCADE)
    type = models.ForeignKey('Room_types', on_delete=models.CASCADE)
    room_number = models.CharField(db_index=True)
    floor = models.IntegerField()
    is_available = models.BooleanField(default=True)
    
    
    def __str__(self):
        return str(self.room_number)


class Guests(models.Model):
    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=150, db_index=True)
    email = models.EmailField(("email"), max_length=254)
    phone = PhoneNumberField(verbose_name='phone')
    passport = models.CharField(max_length=100)
    registration_date = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Bookings(models.Model):
    guest = models.ForeignKey('Guests', on_delete=models.CASCADE)
    room = models.ForeignKey('Rooms', on_delete=models.CASCADE)
    check_in_date = models.DateField(verbose_name='arrival')
    check_out_date = models.DateField(verbose_name='departure')
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,  
        default=Decimal('0.00')
    )
    status = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now=True)
    
    
    def clean(self):
        if self.check_out_date <= self.check_in_date:
            raise ValidationError({
                'check_out_date': 'Дата выезда должна быть позже даты заезда.'
            })
        
        if self.check_in_date < date.today():
            raise ValidationError({
                'check_in_date': 'Дата заезда не может быть в прошлом.'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Booking {self.guest}"
    