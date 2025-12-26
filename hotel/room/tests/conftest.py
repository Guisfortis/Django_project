import pytest
from datetime import date, timedelta
from decimal import Decimal
from rest_framework.test import APIClient
from room.models import Hotels, Room_types, Rooms, Guests, Bookings


@pytest.fixture
def api_client():
    """Базовый клиент для тестирования API"""
    return APIClient()


@pytest.fixture
def hotel():
    return Hotels.objects.create(
        name='Grand Plaza Hotel',
        address='123 Main Street',
        city='New York',
        country='USA',
        phone='+12345678901',
        star_rating=5
    )


@pytest.fixture
def hotel_with_low_rating():
    """Создает отель с низким рейтингом"""
    return Hotels.objects.create(
        name='Budget Hotel',
        address='456 Side Street',
        city='Chicago',
        country='Russia',
        phone='+19876543210',
        star_rating=2
    )


@pytest.fixture
def room_type(hotel):
    return Room_types.objects.create(
        hotel=hotel,
        name='Deluxe Suite',
        description='Spacious suite with king bed and ocean view',
        base_price=Decimal('250.00'),
        max_guests=3
    )


@pytest.fixture
def economy_room_type(hotel):
    """Создает экономный тип комнаты"""
    return Room_types.objects.create(
        hotel=hotel,
        name='Standard Room',
        description='Basic room with twin beds',
        base_price=Decimal('99.99'),
        max_guests=2
    )


@pytest.fixture
def room(hotel, room_type):
    return Rooms.objects.create(
        hotel=hotel,
        type=room_type,
        room_number='301',
        floor=3,
        is_available=True
    )


@pytest.fixture
def unavailable_room(hotel, room_type):
    """Создает недоступную комнату"""
    return Rooms.objects.create(
        hotel=hotel,
        type=room_type,
        room_number='302',
        floor=3,
        is_available=False
    )


@pytest.fixture
def guest():
    return Guests.objects.create(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        phone='+12345678902',
        passport='AB1234567'
    )


@pytest.fixture
def another_guest():
    return Guests.objects.create(
        first_name='Jane',
        last_name='Smith',
        email='jane.smith@example.com',
        phone='+19876543211',
        passport='CD9876543'
    )


@pytest.fixture
def booking(guest, room):
    check_in = date.today() + timedelta(days=1)
    check_out = check_in + timedelta(days=3)
    
    return Bookings.objects.create(
        guest=guest,
        room=room,
        check_in_date=check_in,
        check_out_date=check_out,
        total_price=Decimal('750.00'),
        status='confirmed'
    )


@pytest.fixture
def hotel_data():
    return {
        'name': 'New Luxury Hotel',
        'address': '789 Park Avenue',
        'city': 'Los Angeles',
        'country': 'USA',
        'phone': '+79277693636',
        'star_rating': 5
    }





@pytest.fixture
def room_type_data(hotel):
    """Данные для создания типа комнаты"""
    return {
        'hotel': hotel.id,
        'name': 'Executive Suite',
        'description': 'Luxury executive suite with workspace',
        'base_price': '350.00',
        'max_guests': 4
    }


@pytest.fixture
def room_data(hotel, room_type):
    """Данные для создания комнаты"""
    return {
        'hotel': hotel.id,
        'type': room_type.id,
        'room_number': '401',
        'floor': 4,
        'is_available': True
    }


@pytest.fixture
def guest_data():
    """Данные для создания гостя"""
    return {
        'first_name': 'Michael',
        'last_name': 'Johnson',
        'email': 'michael.j@example.com',
        'phone': '+79276871635',
        'passport': 'EF1122334'
    }


@pytest.fixture
def booking_data(guest, room):
    """Данные для создания бронирования"""
    check_in = date.today() + timedelta(days=7)
    check_out = check_in + timedelta(days=5)
    
    return {
        'guest': guest.id,
        'room': room.id,
        'check_in_date': check_in.isoformat(),
        'check_out_date': check_out.isoformat(),
        'total_price': '1250.00',
        'status': 'pending'
    }


@pytest.fixture
def invalid_booking_data(guest, room):
    """Некорректные данные бронирования (дата выезда раньше заезда)"""
    check_in = date.today() + timedelta(days=5)
    check_out = check_in - timedelta(days=2)
    
    return {
        'guest': guest.id,
        'room': room.id,
        'check_in_date': check_in.isoformat(),
        'check_out_date': check_out.isoformat(),
        'total_price': '500.00',
        'status': 'confirmed'
    }







