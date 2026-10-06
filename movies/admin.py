from django.contrib import admin
from .models import (
    Movie, Theater, Seat, Booking,
    Genre, Language, MoviePoster, Review, CastMember,Payment
)



@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(MoviePoster)
class MoviePosterAdmin(admin.ModelAdmin):
    list_display = ['movie', 'image']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'movie',
        'user',
        'rating',
        'is_verified_viewer',
        'is_reported',
        'created_at'
    ]


@admin.register(CastMember)
class CastMemberAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'description']


@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ['name', 'movie', 'time']


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['theater', 'seat_number', 'is_booked']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'seat', 'movie', 'theater', 'booked_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'theater',
        'amount',
        'status',
        'razorpay_order_id',
        'razorpay_payment_id',
        'created_at'
    ]