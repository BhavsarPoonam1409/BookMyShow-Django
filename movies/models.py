from django.db import models
from django.contrib.auth.models import User



class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class CastMember(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name

class Movie(models.Model):
    AGE_CERTIFICATION_CHOICES = [
        ('U', 'U'),
        ('UA', 'UA'),
        ('A', 'A'),
    ]

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="movies/")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    cast = models.ManyToManyField(CastMember,blank=True,related_name='movies')
    description = models.TextField(blank=True, null=True)

    genre = models.ManyToManyField(Genre, blank=True, related_name='movies')
    language = models.ManyToManyField(Language, blank=True, related_name='movies')

    trailer_url = models.URLField(blank=True, null=True)

    age_certification = models.CharField(
        max_length=2,
        choices=AGE_CERTIFICATION_CHOICES,
        blank=True,
        null=True
    )

    duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Duration in minutes"
    )

    release_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name


class MoviePoster(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='posters'
    )
    image = models.ImageField(upload_to="movies/posters/")

    def __str__(self):
        return f"{self.movie.name} Poster"


# class Theater(models.Model):
#     name = models.CharField(max_length=255)
#     movie = models.ForeignKey(
#         Movie,
#         on_delete=models.CASCADE,
#         related_name='theaters'
#     )
#     time = models.DateTimeField()

#     def __str__(self):
#         return f'{self.name} - {self.movie.name} at {self.time}'

# class Theater(models.Model):
#     name = models.CharField(max_length=255)

#     city = models.CharField(
#         max_length=100,
#         blank=True,
#         null=True
#     )

#     movie = models.ForeignKey(
#         Movie,
#         on_delete=models.CASCADE,
#         related_name='theaters'
#     )

#     time = models.DateTimeField()

#     ticket_price = models.DecimalField(
#         max_digits=8,
#         decimal_places=2,
#         default=0
#     )

#     def __str__(self):
#         return f'{self.name} - {self.movie.name} at {self.time}'

class Theater(models.Model):

    name = models.CharField(max_length=255)

    city = models.CharField(
        max_length=100
    )

    screen = models.CharField(
        max_length=100,
        default="Screen 1"
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='theaters'
    )

    time = models.DateTimeField()

    ticket_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f'{self.name} - {self.movie.name} at {self.time}'


# class Seat(models.Model):
#     theater = models.ForeignKey(
#         Theater,
#         on_delete=models.CASCADE,
#         related_name='seats'
#     )
#     seat_number = models.CharField(max_length=10)
#     is_booked = models.BooleanField(default=False)

#     def __str__(self):
#         return f'{self.seat_number} in {self.theater.name}'

class Seat(models.Model):
    theater = models.ForeignKey(
        Theater,
        on_delete=models.CASCADE,
        related_name='seats'
    )
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)
    is_reserved = models.BooleanField(default=False)
    reserved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    reserved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['theater']),
            models.Index(fields=['theater', 'is_booked']),
            models.Index(fields=['theater', 'is_reserved']),
        ]

    def __str__(self):
        return f'{self.seat_number} in {self.theater.name}'


class Booking(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True, db_index=True)

    ticket = models.FileField(
        upload_to="tickets/",
        blank=True,
        null=True
    )

    class Meta:
        indexes = [
            # models.Index(fields=['booked_at']),
            models.Index(fields=['theater', 'booked_at']),
            models.Index(fields=['movie', 'booked_at']),
        ]

    def __str__(self):
        return f'Booking by {self.user.username} for {self.seat.seat_number} at {self.theater.name}'


class Review(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='movie_reviews'
    )

    rating = models.PositiveIntegerField()
    review_text = models.TextField()

    is_verified_viewer = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('movie', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.movie.name}'


class Payment(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ('created', 'Created'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    theater = models.ForeignKey(
        Theater,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    razorpay_order_id = models.CharField(
        max_length=200,
        unique=True
    )

    razorpay_payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    transaction_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='created',
        db_index=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    reserved_seats = models.TextField(
    blank=True,
    null=True
    )

    class Meta:
        indexes = [
            # models.Index(fields=['created_at']),
            # models.Index(fields=['status']),
            models.Index(fields=['status', 'created_at']),
            # models.Index(fields=['theater', 'created_at']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.status}'