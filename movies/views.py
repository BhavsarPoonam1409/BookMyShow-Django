from .tasks import generate_and_send_ticket
import re
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect ,get_object_or_404,HttpResponse
from .models import Movie,Theater,Seat,Booking,Review,Payment,Genre, Language
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db import IntegrityError,transaction
from django.utils import timezone
from .forms import ReviewForm
from urllib.parse import urlparse, parse_qs
from django.db.models import Avg,Q,Count,Sum,Min
from django.core.paginator import Paginator
from django.contrib import messages
from datetime import timedelta,datetime
from django.db.models.functions import TruncDate,TruncHour
from django.db.models.functions import ExtractHour
import razorpay
from django.conf import settings
import json 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import hmac
import hashlib
from django.contrib.auth.models import User


# def movie_list(request):
#     search_query=request.GET.get('search')
#     if search_query:
#         movies=Movie.objects.filter(name__icontains=search_query)
#     else:
#         movies=Movie.objects.all()
#     return render(request,'movies/movie_list.html',{'movies':movies})

# def movie_list(request):

#     search_query = request.GET.get('search')
#     genre_id = request.GET.get('genre')
#     language_id = request.GET.get('language')

#     movies = Movie.objects.all()

#     if search_query:
#         movies = movies.filter(
#             name__icontains=search_query
#         )

#     if genre_id:
#         movies = movies.filter(
#             genre__id=genre_id
#         )

#     if language_id:
#         movies = movies.filter(
#             language__id=language_id
#         )

#     movies = movies.distinct()

#     genres = Genre.objects.all()
#     languages = Language.objects.all()

#     return render(
#         request,
#         'movies/movie_list.html',
#         {
#             'movies': movies,
#             'genres': genres,
#             'languages': languages,
#         }
#     )

# def movie_list(request):

#     search_query = request.GET.get('search')
#     genre_id = request.GET.get('genre')
#     language_id = request.GET.get('language')
#     city = request.GET.get('city')
#     theater_id = request.GET.get('theater')
#     rating = request.GET.get('rating')
#     release_date = request.GET.get('release_date')
#     show_time = request.GET.get('show_time')
#     sort = request.GET.get('sort')

#     movies = Movie.objects.all()

#     # Search by movie name
#     if search_query:
#         movies = movies.filter(
#             name__icontains=search_query
#         )

#     # Genre filter
#     if genre_id:
#         movies = movies.filter(
#             genre__id=genre_id
#         )

#     # Language filter
#     if language_id:
#         movies = movies.filter(
#             language__id=language_id
#         )

#     # City filter
#     if city:
#         movies = movies.filter(
#             theaters__city__iexact=city
#         )

#     # Theater filter
#     if theater_id:
#         movies = movies.filter(
#             theaters__id=theater_id
#         )

#     # Rating filter
#     if rating:
#         movies = movies.filter(
#             rating__gte=rating
#         )

#     # Release date filter
#     if release_date:
#         movies = movies.filter(
#             release_date=release_date
#         )

#     # Show timing filter
#     if show_time:
#         movies = movies.filter(
#             theaters__time__hour=show_time
#         )

#     # Remove duplicate movies
#     movies = movies.distinct()

#     # Sorting
#     if sort == 'newest':
#         movies = movies.order_by('-release_date')

#     elif sort == 'rating':
#         movies = movies.order_by('-rating')

#     elif sort == 'price_low':
#         movies = movies.order_by(
#             'theaters__ticket_price'
#         )

#     elif sort == 'price_high':
#         movies = movies.order_by(
#             '-theaters__ticket_price'
#         )

#     else:
#         movies = movies.order_by('name')

#     # Filter data for dropdowns
#     genres = Genre.objects.all()
#     languages = Language.objects.all()

#     theaters = Theater.objects.all().select_related(
#         'movie'
#     )

#     cities = Theater.objects.values_list(
#         'city',
#         flat=True
#     ).distinct().order_by('city')

#     return render(
#         request,
#         'movies/movie_list.html',
#         {
#             'movies': movies,
#             'genres': genres,
#             'languages': languages,
#             'theaters': theaters,
#             'cities': cities,
#         }
#     )

# def movie_list(request):

#     search_query = request.GET.get('search', '')
#     genre_id = request.GET.get('genre', '')
#     language_id = request.GET.get('language', '')
#     city = request.GET.get('city', '')
#     theater_id = request.GET.get('theater', '')
#     release_date = request.GET.get('release_date', '')
#     min_rating = request.GET.get('min_rating', '')
#     show_date = request.GET.get('show_date', '')
#     sort_by = request.GET.get('sort', 'name')

#     movies = Movie.objects.all()

#     # Search by movie name
#     if search_query:
#         movies = movies.filter(
#             name__icontains=search_query
#         )

#     # Filter by genre
#     if genre_id:
#         movies = movies.filter(
#             genre__id=genre_id
#         )

#     # Filter by language
#     if language_id:
#         movies = movies.filter(
#             language__id=language_id
#         )

#     # Filter by city
#     if city:
#         movies = movies.filter(
#             theaters__city__icontains=city
#         )

#     # Filter by theater
#     if theater_id:
#         movies = movies.filter(
#             theaters__id=theater_id
#         )

#     # Filter by release date
#     if release_date:
#         movies = movies.filter(
#             release_date=release_date
#         )

#     # Filter by minimum rating
#     if min_rating:
#         movies = movies.filter(
#             rating__gte=min_rating
#         )

#     # Filter by show date
#     if show_date:
#         movies = movies.filter(
#             theaters__time__date=show_date
#         )

#     # Remove duplicate movies
#     movies = movies.distinct()

#     # Popularity and ticket price
#     movies = movies.annotate(
#         booking_count=Count(
#             'booking',
#             distinct=True
#         ),
#         lowest_ticket_price=Min(
#             'theaters__ticket_price'
#         )
#     )

#     # Sorting
#     if sort_by == 'popularity':
#         movies = movies.order_by(
#             '-booking_count',
#             'name'
#         )

#     elif sort_by == 'newest':
#         movies = movies.order_by(
#             '-release_date',
#             'name'
#         )

#     elif sort_by == 'rating':
#         movies = movies.order_by(
#             '-rating',
#             'name'
#         )

#     elif sort_by == 'price_low':
#         movies = movies.order_by(
#             'lowest_ticket_price',
#             'name'
#         )

#     elif sort_by == 'price_high':
#         movies = movies.order_by(
#             '-lowest_ticket_price',
#             'name'
#         )

#     else:
#         movies = movies.order_by('name')

#     # Get filter options
#     genres = Genre.objects.all().order_by('name')
#     languages = Language.objects.all().order_by('name')

#     theaters = Theater.objects.select_related(
#         'movie'
#     ).order_by('name')

#     # Get cities from theaters
#     cities = Theater.objects.values_list(
#         'city',
#         flat=True
#     ).distinct().order_by('city')

#     # Pagination
#     paginator = Paginator(movies, 6)

#     page_number = request.GET.get('page')

#     page_obj = paginator.get_page(page_number)

#     # Recommended for You
#     recommended_movies = Movie.objects.none()

#     if request.user.is_authenticated:

#         booked_movie_ids = Booking.objects.filter(
#             user=request.user
#         ).values_list(
#             'movie_id',
#             flat=True
#         )

#         viewed_movie_ids = request.session.get(
#             'recently_viewed_movies',
#             []
#         )

#         related_movie_ids = list(booked_movie_ids) + viewed_movie_ids

#         if related_movie_ids:

#             related_movies = Movie.objects.filter(
#                 id__in=related_movie_ids
#             )

#             genre_ids = Genre.objects.filter(
#                 movies__in=related_movies
#             ).values_list(
#                 'id',
#                 flat=True
#             )

#             language_ids = Language.objects.filter(
#                 movies__in=related_movies
#             ).values_list(
#                 'id',
#                 flat=True
#             )

#             recommended_movies = Movie.objects.filter(
#                 Q(genre__id__in=genre_ids) |
#                 Q(language__id__in=language_ids)
#             ).exclude(
#                 id__in=related_movie_ids
#             ).distinct().order_by(
#                 '-rating'
#             )[:6]

#     return render(
#         request,
#         'movies/movie_list.html',
#         {
#             'movies': page_obj,
#             'page_obj': page_obj,
#             'genres': genres,
#             'languages': languages,
#             'theaters': theaters,
#             'cities': cities,
#             'recommended_movies': recommended_movies,

#             'search_query': search_query,
#             'genre_id': genre_id,
#             'language_id': language_id,
#             'city': city,
#             'theater_id': theater_id,
#             'release_date': release_date,
#             'min_rating': min_rating,
#             'show_date': show_date,
#             'sort_by': sort_by,
#         }
#     )

# def movie_list(request):

#     search_query = request.GET.get('search', '')
#     genre_id = request.GET.get('genre', '')
#     language_id = request.GET.get('language', '')
#     city = request.GET.get('city', '')
#     theater_id = request.GET.get('theater', '')
#     release_date = request.GET.get('release_date', '')
#     min_rating = request.GET.get('min_rating', '')
#     show_date = request.GET.get('show_date', '')
#     sort_by = request.GET.get('sort', 'name')

#     movies = Movie.objects.all()

#     # Search by movie name
#     if search_query:
#         movies = movies.filter(
#             name__icontains=search_query
#         )

#     # Filter by genre
#     if genre_id:
#         movies = movies.filter(
#             genre__id=genre_id
#         )

#     # Filter by language
#     if language_id:
#         movies = movies.filter(
#             language__id=language_id
#         )

#     # Filter by city
#     if city:
#         movies = movies.filter(
#             theaters__city__icontains=city
#         )

#     # Filter by theater
#     if theater_id:
#         movies = movies.filter(
#             theaters__id=theater_id
#         )

#     # Filter by release date
#     if release_date:
#         movies = movies.filter(
#             release_date=release_date
#         )

#     # Filter by minimum rating
#     if min_rating:
#         movies = movies.filter(
#             rating__gte=min_rating
#         )

#     # Filter by show date
#     if show_date:
#         movies = movies.filter(
#             theaters__time__date=show_date
#         )

#     # Remove duplicate movies
#     movies = movies.distinct()

#     # Booking count and lowest ticket price
#     movies = movies.annotate(
#         booking_count=Count(
#             'booking',
#             distinct=True
#         ),
#         lowest_ticket_price=Min(
#             'theaters__ticket_price'
#         )
#     )

#     # Sorting
#     if sort_by == 'popularity':

#         movies = movies.order_by(
#             '-booking_count',
#             'name'
#         )

#     elif sort_by == 'newest':

#         movies = movies.order_by(
#             '-release_date',
#             'name'
#         )

#     elif sort_by == 'rating':

#         movies = movies.order_by(
#             '-rating',
#             'name'
#         )

#     elif sort_by == 'price_low':

#         movies = movies.order_by(
#             'lowest_ticket_price',
#             'name'
#         )

#     elif sort_by == 'price_high':

#         movies = movies.order_by(
#             '-lowest_ticket_price',
#             'name'
#         )

#     else:

#         movies = movies.order_by(
#             'name'
#         )

#     # Get filter options
#     genres = Genre.objects.all().order_by('name')

#     languages = Language.objects.all().order_by('name')

#     theaters = Theater.objects.select_related(
#         'movie'
#     ).order_by('name')

#     # Get cities from theaters
#     cities = Theater.objects.values_list(
#         'city',
#         flat=True
#     ).distinct().order_by('city')

#     # Pagination
#     paginator = Paginator(
#         movies,
#         6
#     )

#     page_number = request.GET.get(
#         'page'
#     )

#     page_obj = paginator.get_page(
#         page_number
#     )

#     # Recommended for You
#     recommended_movies = Movie.objects.none()

#     if request.user.is_authenticated:

#         booked_movie_ids = Booking.objects.filter(
#             user=request.user
#         ).values_list(
#             'movie_id',
#             flat=True
#         )

#         viewed_movie_ids = request.session.get(
#             'recently_viewed_movies',
#             []
#         )

#         related_movie_ids = list(
#             booked_movie_ids
#         ) + viewed_movie_ids

#         if related_movie_ids:

#             related_movies = Movie.objects.filter(
#                 id__in=related_movie_ids
#             )

#             genre_ids = Genre.objects.filter(
#                 movies__in=related_movies
#             ).values_list(
#                 'id',
#                 flat=True
#             )

#             language_ids = Language.objects.filter(
#                 movies__in=related_movies
#             ).values_list(
#                 'id',
#                 flat=True
#             )

#             recommended_movies = Movie.objects.filter(
#                 Q(genre__id__in=genre_ids) |
#                 Q(language__id__in=language_ids)
#             ).exclude(
#                 id__in=related_movie_ids
#             ).distinct().order_by(
#                 '-rating'
#             )[:6]

#     return render(
#         request,
#         'movies/movie_list.html',
#         {
#             'movies': page_obj,
#             'page_obj': page_obj,

#             'genres': genres,
#             'languages': languages,
#             'theaters': theaters,
#             'cities': cities,

#             'recommended_movies': recommended_movies,

#             'search_query': search_query,
#             'genre_id': genre_id,
#             'language_id': language_id,
#             'city': city,
#             'theater_id': theater_id,
#             'release_date': release_date,
#             'min_rating': min_rating,
#             'show_date': show_date,
#             'sort_by': sort_by,
#         }
#     )

def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    theaters = Theater.objects.filter(
        movie=movie
    ).order_by('time')

    return render(
        request,
        'movies/theater_list.html',
        {
            'movie': movie,
            'theaters': theaters,
        }
    )

# def theater_list(request,movie_id):
#     movie = get_object_or_404(Movie,id=movie_id)
#     theater=Theater.objects.filter(movie=movie)
#     return render(request,'movies/theater_list.html',{'movie':movie,'theaters':theater})

def movie_list(request):

    search_query = request.GET.get('search', '')
    genre_id = request.GET.get('genre', '')
    language_id = request.GET.get('language', '')
    city = request.GET.get('city', '')
    theater_id = request.GET.get('theater', '')
    release_date = request.GET.get('release_date', '')
    min_rating = request.GET.get('min_rating', '')
    show_date = request.GET.get('show_date', '')
    sort_by = request.GET.get('sort', 'name')

    movies = Movie.objects.all()

    if search_query:
        movies = movies.filter(
            name__icontains=search_query
        )

    if genre_id:
        movies = movies.filter(
            genre__id=genre_id
        )

    if language_id:
        movies = movies.filter(
            language__id=language_id
        )

    if city:
        movies = movies.filter(
            theaters__city__icontains=city
        )

    if theater_id:
        movies = movies.filter(
            theaters__id=theater_id
        )

    if release_date:
        movies = movies.filter(
            release_date=release_date
        )

    if min_rating:
        movies = movies.filter(
            rating__gte=min_rating
        )

    if show_date:
        movies = movies.filter(
            theaters__time__date=show_date
        )

    movies = movies.distinct()

    movies = movies.annotate(
        booking_count=Count(
            'booking',
            distinct=True
        ),
        lowest_ticket_price=Min(
            'theaters__ticket_price'
        )
    )

    if sort_by == 'popularity':

        movies = movies.order_by(
            '-booking_count',
            'name'
        )

    elif sort_by == 'newest':

        movies = movies.order_by(
            '-release_date',
            'name'
        )

    elif sort_by == 'rating':

        movies = movies.order_by(
            '-rating',
            'name'
        )

    elif sort_by == 'price_low':

        movies = movies.order_by(
            'lowest_ticket_price',
            'name'
        )

    elif sort_by == 'price_high':

        movies = movies.order_by(
            '-lowest_ticket_price',
            'name'
        )

    else:

        movies = movies.order_by(
            'name'
        )

    genres = Genre.objects.all().order_by(
        'name'
    )

    languages = Language.objects.all().order_by(
        'name'
    )

    theaters = Theater.objects.select_related(
        'movie'
    ).order_by(
        'name'
    )

    cities = Theater.objects.values_list(
        'city',
        flat=True
    ).distinct().order_by(
        'city'
    )

    paginator = Paginator(
        movies,
        6
    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )

    # ==========================================
    # RECENTLY VIEWED MOVIES
    # ==========================================

    recently_viewed_movies = Movie.objects.none()

    viewed_movie_ids = request.session.get(
        'recently_viewed_movies',
        []
    )

    viewed_movie_ids = [
        int(movie_id)
        for movie_id in viewed_movie_ids
        if str(movie_id).isdigit()
    ]

    if viewed_movie_ids:

        recently_viewed_movies = Movie.objects.filter(
            id__in=viewed_movie_ids
        )

        recently_viewed_movies = list(
            recently_viewed_movies
        )

        movie_order = {
            movie_id: position
            for position, movie_id
            in enumerate(viewed_movie_ids)
        }

        recently_viewed_movies.sort(
            key=lambda movie: movie_order.get(
                movie.id,
                999
            )
        )

        recently_viewed_movies = recently_viewed_movies[:5]

    # ==========================================
    # RECOMMENDED FOR YOU
    # ==========================================

    recommended_movies = Movie.objects.none()

    if request.user.is_authenticated:

        booked_movie_ids = list(
            Booking.objects.filter(
                user=request.user
            ).values_list(
                'movie_id',
                flat=True
            )
        )

        related_movie_ids = list(
            set(
                booked_movie_ids +
                viewed_movie_ids
            )
        )

        if related_movie_ids:

            related_movies = Movie.objects.filter(
                id__in=related_movie_ids
            )

            genre_ids = Genre.objects.filter(
                movies__in=related_movies
            ).values_list(
                'id',
                flat=True
            ).distinct()

            language_ids = Language.objects.filter(
                movies__in=related_movies
            ).values_list(
                'id',
                flat=True
            ).distinct()

            recommended_movies = Movie.objects.filter(
                Q(
                    genre__id__in=genre_ids
                )
                |
                Q(
                    language__id__in=language_ids
                )
            ).exclude(
                id__in=related_movie_ids
            ).distinct().annotate(
                booking_count=Count(
                    'booking',
                    distinct=True
                )
            ).order_by(
                '-rating',
                '-booking_count',
                'name'
            )[:6]

    return render(
        request,
        'movies/movie_list.html',
        {
            'movies': page_obj,
            'page_obj': page_obj,

            'genres': genres,
            'languages': languages,
            'theaters': theaters,
            'cities': cities,

            'recently_viewed_movies':
                recently_viewed_movies,

            'recommended_movies':
                recommended_movies,

            'search_query': search_query,
            'genre_id': genre_id,
            'language_id': language_id,
            'city': city,
            'theater_id': theater_id,
            'release_date': release_date,
            'min_rating': min_rating,
            'show_date': show_date,
            'sort_by': sort_by,
        }
    )

# @login_required(login_url='/login/')
# def book_seats(request,theater_id):
#     theaters=get_object_or_404(Theater,id=theater_id)
#     seats=Seat.objects.filter(theater=theaters)
#     if request.method=='POST':
#         selected_Seats= request.POST.getlist('seats')
#         error_seats=[]
#         if not selected_Seats:
#             return render(request,"movies/seat_selection.html",{'theater':theaters,'seats':seats,'error':"No seat selected"})
#         for seat_id in selected_Seats:
#             seat=get_object_or_404(Seat,id=seat_id,theater=theaters)
#             if seat.is_booked:
#                 error_seats.append(seat.seat_number)
#                 continue
#             try:
#                 Booking.objects.create(
#                     user=request.user,
#                     seat=seat,
#                     movie=theaters.movie,
#                     theater=theaters
#                 )
#                 seat.is_booked=True
#                 seat.save()
#             except IntegrityError:
#                 error_seats.append(seat.seat_number)
#         if error_seats:
#             error_message=f"The following seats are already booked: {', '.join(error_seats)}"
#             return render(request,'movies/seat_selection.html',{'theater':theaters,"seats":seats,'error':error_message})
#         return redirect('profile')
#     return render(request,'movies/seat_selection.html',{'theaters':theaters,"seats":seats})





# @login_required(login_url='/login/')
# def book_seats(request, theater_id):
#     theater = get_object_or_404(Theater, id=theater_id)
#     seats = Seat.objects.filter(theater=theater)

#     if request.method == 'POST':
#         selected_seats = request.POST.getlist('seats')
#         print("Selected seats:", selected_seats)  

#         if not selected_seats:
#             return render(request, "movies/seat_selection.html", {
#                 'theater': theater,
#                 'seats': seats,
#                 'error': "No seat selected"
#             })

#         error_seats = []
#         for seat_id in selected_seats:
#             seat = get_object_or_404(Seat, id=seat_id, theater=theater)
#             if seat.is_booked:
#                 error_seats.append(seat.seat_number)
#                 continue
#             try:
#                 Booking.objects.create(
#                     user=request.user,
#                     seat=seat,
#                     movie=theater.movie,
#                     theater=theater
#                 )
#                 seat.is_booked = True
#                 seat.save()
#             except IntegrityError:
#                 error_seats.append(seat.seat_number)

#         if error_seats:
#             error_message = f"The following seats are already booked: {', '.join(error_seats)}"
#             return render(request, 'movies/seat_selection.html', {
#                 'theater': theater,
#                 'seats': seats,
#                 'error': error_message
#             })

#         return redirect('profile')

#     return render(request, 'movies/seat_selection.html', {
#         'theater': theater,
#         'seats': seats
#     })

@login_required(login_url='/login/')
def book_seats(request, theater_id):

    theater = get_object_or_404(Theater, id=theater_id)

    def seat_sort_key(seat):
        match = re.match(r'([A-Za-z]+)(\d+)', seat.seat_number)

        if match:
            return match.group(1), int(match.group(2))

        return seat.seat_number, 0

    # Change Seats par click karne par
    # purani reserved seats release karna
    if request.GET.get('change') == '1':

        old_seat_ids = request.session.get('reserved_seats', [])

        Seat.objects.filter(
            id__in=old_seat_ids,
            reserved_by=request.user,
            is_reserved=True
        ).update(
            is_reserved=False,
            reserved_by=None,
            reserved_at=None
        )

        request.session.pop('reserved_seats', None)
        request.session.pop('reservation_theater_id', None)

    seats_queryset = Seat.objects.filter(
        theater=theater
    )

    current_time = timezone.now()

    # Remove expired reservations
    expired_seats = seats_queryset.filter(
        is_reserved=True,
        reserved_at__lt=current_time - timedelta(minutes=2)
    )

    expired_seats.update(
        is_reserved=False,
        reserved_by=None,
        reserved_at=None
    )

    # Get seats again after expired reservations are removed
    seats = list(
        Seat.objects.filter(
            theater=theater
        )
    )

    # Natural seat ordering
    seats.sort(key=seat_sort_key)

    if request.method == 'POST':

        selected_seats = request.POST.getlist('seats')

        if not selected_seats:

            return render(
                request,
                "movies/seat_selection.html",
                {
                    'theater': theater,
                    'seats': seats,
                    'error': "No seat selected"
                }
            )

        error_seats = []

        with transaction.atomic():

            selected_seat_objects = Seat.objects.select_for_update().filter(
                id__in=selected_seats,
                theater=theater
            )

            for seat in selected_seat_objects:

                if seat.is_booked:

                    error_seats.append(
                        seat.seat_number
                    )

                    continue

                if seat.is_reserved and seat.reserved_by != request.user:

                    error_seats.append(
                        seat.seat_number
                    )

                    continue

                seat.is_reserved = True
                seat.reserved_by = request.user
                seat.reserved_at = current_time
                seat.save()

        if error_seats:

            error_message = (
                f"These seats are not available: "
                f"{', '.join(error_seats)}"
            )

            seats = list(
                Seat.objects.filter(
                    theater=theater
                )
            )

            seats.sort(key=seat_sort_key)

            return render(
                request,
                'movies/seat_selection.html',
                {
                    'theater': theater,
                    'seats': seats,
                    'error': error_message
                }
            )

        request.session['reserved_seats'] = selected_seats

        request.session['reservation_theater_id'] = theater.id

        return redirect('reservation')

    return render(
        request,
        'movies/seat_selection.html',
        {
            'theater': theater,
            'seats': seats
        }
    )

@login_required(login_url='/login/')
def reservation(request):

    selected_seats = request.session.get(
        'reserved_seats',
        []
    )

    theater_id = request.session.get(
        'reservation_theater_id'
    )

    if not selected_seats or not theater_id:
        return redirect('movie_list')

    theater = get_object_or_404(
        Theater,
        id=theater_id
    )

    seats = Seat.objects.filter(
        id__in=selected_seats,
        theater=theater,
        reserved_by=request.user,
        is_reserved=True
    )

    if not seats.exists():
        return redirect('movie_list')

    first_seat = seats.first()

    expiry_time = first_seat.reserved_at + timedelta(minutes=2)

    if timezone.now() >= expiry_time:

        seats.update(
            is_reserved=False,
            reserved_by=None,
            reserved_at=None
        )

        request.session.pop(
            'reserved_seats',
            None
        )

        request.session.pop(
            'reservation_theater_id',
            None
        )

        return redirect(
            'book_seats',
            theater_id=theater.id
        )

    remaining_seconds = int(
        (expiry_time - timezone.now()).total_seconds()
    )

    # Calculate total amount
    amount = seats.count() * 200

    # Create a new Razorpay order
    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    order = client.order.create({
        'amount': int(amount * 100),
        'currency': 'INR',
        'payment_capture': 1
    })

    payment = Payment.objects.create(
        user=request.user,
        theater=theater,
        amount=amount,
        razorpay_order_id=order['id'],
        status='created',
        reserved_seats=','.join(selected_seats)
)

    return render(
        request,
        'movies/reservation.html',
        {
            'theater': theater,
            'seats': seats,
            'expiry_time': expiry_time,
            'remaining_seconds': remaining_seconds,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': payment.razorpay_order_id,
            'amount': amount,
            'payment_id': payment.id
        }
    )
# def movie_detail(request, movie_id):
#     movie = get_object_or_404(Movie, id=movie_id)

#     return render(
#         request,
#         'movies/movie_detail.html',
#         {'movie': movie}
#     )

# def movie_detail(request, movie_id):
#     movie = get_object_or_404(Movie, id=movie_id)

#     trailer_embed_url = None

#     if movie.trailer_url:
#         url = movie.trailer_url

#         if "youtube.com/watch" in url:
#             video_id = parse_qs(urlparse(url).query).get('v')

#             if video_id:
#                 trailer_embed_url = f"https://www.youtube-nocookie.com/embed/{video_id[0]}"

#         elif "youtu.be/" in url:
#             video_id = url.split("youtu.be/")[1].split("?")[0]

#             trailer_embed_url = f"https://www.youtube-nocookie.com/embed/{video_id}"

#     return render(
#         request,
#         'movies/movie_detail.html',
#         {
#             'movie': movie,
#             'trailer_embed_url': trailer_embed_url
#         }
#     )

# def movie_detail(request, movie_id):
#     movie = get_object_or_404(Movie, id=movie_id)

#     # Store recently viewed movies
#     recently_viewed = request.session.get(
#         'recently_viewed_movies',
#         []
#     )

#     if movie_id in recently_viewed:
#         recently_viewed.remove(movie_id)

#     recently_viewed.insert(0, movie_id)

#     # Keep only last 5 recently viewed movies
#     recently_viewed = recently_viewed[:5]

#     request.session['recently_viewed_movies'] = recently_viewed

#     similar_movies = Movie.objects.filter(
#         Q(genre__in=movie.genre.all()) |
#         Q(language__in=movie.language.all())
#     ).exclude(
#         id=movie.id
#     ).distinct()[:4]

#     trending_movies = Movie.objects.annotate(
#         booking_count=Count('booking')
#     ).order_by('-booking_count')[:4]

#     recently_released = Movie.objects.filter(
#         release_date__isnull=False
#     ).exclude(
#         id=movie.id
#     ).order_by(
#         '-release_date'
#     )[:4]

#     trailer_embed_url = None

#     if movie.trailer_url:
#         url = movie.trailer_url

#         if "youtube.com/watch" in url:
#             video_id = parse_qs(
#                 urlparse(url).query
#             ).get('v')

#             if video_id:
#                 trailer_embed_url = (
#                     f"https://www.youtube-nocookie.com/embed/{video_id[0]}"
#                 )

#         elif "youtu.be/" in url:
#             video_id = url.split(
#                 "youtu.be/"
#             )[1].split("?")[0]

#             trailer_embed_url = (
#                 f"https://www.youtube-nocookie.com/embed/{video_id}"
#             )

#     review_form = None
#     can_review = False

#     if request.user.is_authenticated:

#         watched_movie = Booking.objects.filter(
#             user=request.user,
#             movie=movie,
#             theater__time__lte=timezone.now()
#         ).exists()

#         if watched_movie:
#             can_review = True
#             review_form = ReviewForm()

#             if request.method == 'POST':
#                 review_form = ReviewForm(request.POST)

#                 if review_form.is_valid():
#                     review = review_form.save(commit=False)
#                     review.movie = movie
#                     review.user = request.user
#                     review.is_verified_viewer = True
#                     review.save()

#                     average_rating = Review.objects.filter(
#                         movie=movie
#                     ).aggregate(
#                         Avg('rating')
#                     )['rating__avg']

#                     movie.rating = average_rating
#                     movie.save()

#                     return redirect(
#                         'movie_detail',
#                         movie_id=movie.id
#                     )

#     reviews = Review.objects.filter(
#         movie=movie
#     ).order_by('-created_at')

#     return render(
#         request,
#         'movies/movie_detail.html',
#         {
#             'movie': movie,
#             'trailer_embed_url': trailer_embed_url,
#             'review_form': review_form,
#             'reviews': reviews,
#             'can_review': can_review,
#             'similar_movies': similar_movies,
#             'trending_movies': trending_movies,
#             'recently_released': recently_released,
#         }
#     )

def movie_detail(request, movie_id):

    movie = get_object_or_404(
        Movie,
        id=movie_id
    )

    # ==========================================
    # STORE RECENTLY VIEWED MOVIES
    # ==========================================

    recently_viewed = request.session.get(
        'recently_viewed_movies',
        []
    )

    recently_viewed = [
        int(movie_id)
        for movie_id in recently_viewed
        if str(movie_id).isdigit()
    ]

    if movie_id in recently_viewed:

        recently_viewed.remove(
            movie_id
        )

    recently_viewed.insert(
        0,
        movie_id
    )

    recently_viewed = recently_viewed[:5]

    request.session[
        'recently_viewed_movies'
    ] = recently_viewed

    # ==========================================
    # SIMILAR MOVIES
    # ==========================================

    similar_movies = Movie.objects.filter(
        Q(
            genre__in=movie.genre.all()
        )
        |
        Q(
            language__in=movie.language.all()
        )
    ).exclude(
        id=movie.id
    ).distinct()[:4]

    # ==========================================
    # TRENDING MOVIES
    # ==========================================

    trending_movies = Movie.objects.annotate(
        booking_count=Count(
            'booking'
        )
    ).exclude(
        id=movie.id
    ).order_by(
        '-booking_count'
    )[:4]

    # ==========================================
    # RECENTLY RELEASED
    # ==========================================

    recently_released = Movie.objects.filter(
        release_date__isnull=False
    ).exclude(
        id=movie.id
    ).order_by(
        '-release_date'
    )[:4]

    # ==========================================
    # YOUTUBE TRAILER
    # ==========================================

    trailer_embed_url = None

    if movie.trailer_url:

        url = movie.trailer_url

        if "youtube.com/watch" in url:

            video_id = parse_qs(
                urlparse(url).query
            ).get('v')

            if video_id:

                trailer_embed_url = (
                    "https://www.youtube-nocookie.com/"
                    "embed/"
                    + video_id[0]
                )

        elif "youtu.be/" in url:

            video_id = url.split(
                "youtu.be/"
            )[1].split("?")[0]

            trailer_embed_url = (
                "https://www.youtube-nocookie.com/"
                "embed/"
                + video_id
            )

    # ==========================================
    # REVIEW
    # ==========================================

    review_form = None
    can_review = False

    if request.user.is_authenticated:

        watched_movie = Booking.objects.filter(
            user=request.user,
            movie=movie,
            theater__time__lte=timezone.now()
        ).exists()

        if watched_movie:

            can_review = True

            review_form = ReviewForm()

            if request.method == 'POST':

                review_form = ReviewForm(
                    request.POST
                )

                if review_form.is_valid():

                    review = review_form.save(
                        commit=False
                    )

                    review.movie = movie
                    review.user = request.user
                    review.is_verified_viewer = True

                    review.save()

                    average_rating = Review.objects.filter(
                        movie=movie
                    ).aggregate(
                        Avg('rating')
                    )['rating__avg']

                    movie.rating = average_rating
                    movie.save()

                    return redirect(
                        'movie_detail',
                        movie_id=movie.id
                    )

    reviews = Review.objects.filter(
        movie=movie
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'movies/movie_detail.html',
        {
            'movie': movie,

            'trailer_embed_url':
                trailer_embed_url,

            'review_form':
                review_form,

            'reviews':
                reviews,

            'can_review':
                can_review,

            'similar_movies':
                similar_movies,

            'trending_movies':
                trending_movies,

            'recently_released':
                recently_released,
        }
    )


@login_required(login_url='/login/')
def edit_review(request, review_id):

    review = get_object_or_404(
        Review,
        id=review_id,
        user=request.user
    )

    if request.method == 'POST':

        review_form = ReviewForm(
            request.POST,
            instance=review
        )

        if review_form.is_valid():

            review_form.save()

            # Update average movie rating
            average_rating = Review.objects.filter(
                movie=review.movie
            ).aggregate(
                Avg('rating')
            )['rating__avg']

            review.movie.rating = average_rating
            review.movie.save()

            return redirect(
                'movie_detail',
                movie_id=review.movie.id
            )

    else:

        review_form = ReviewForm(
            instance=review
        )

    return render(
        request,
        'movies/edit_review.html',
        {
            'review_form': review_form,
            'review': review
        }
    )

@login_required(login_url='/login/')
def edit_review(request, review_id):

    review = get_object_or_404(
        Review,
        id=review_id,
        user=request.user
    )

    if request.method == 'POST':

        review_form = ReviewForm(request.POST, instance=review)

        if review_form.is_valid():

            review_form.save()

            average_rating = Review.objects.filter(
                movie=review.movie
            ).aggregate(
                Avg('rating')
            )['rating__avg']

            review.movie.rating = average_rating
            review.movie.save()

            return redirect(
                'movie_detail',
                movie_id=review.movie.id
            )

    else:
        review_form = ReviewForm(instance=review)

    return render(
        request,
        'movies/edit_review.html',
        {
            'review_form': review_form,
            'review': review
        }
    )

# @login_required(login_url='/login/')
# def report_review(request, review_id):

#     review = get_object_or_404(Review, id=review_id)

#     if request.method == 'POST':

#         if review.user != request.user:
#             review.is_reported = True
#             review.save()

#     return redirect(
#         'movie_detail',
#         movie_id=review.movie.id
#     )

@login_required(login_url='/login/')
def report_review(request, review_id):

    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':

        if review.user != request.user:
            review.is_reported = True
            review.save()

            messages.success(
                request,
                "Review reported successfully."
            )

    return redirect(
        'movie_detail',
        movie_id=review.movie.id
    )

@login_required(login_url='/login/')
def payment_response(request):

    if request.method == 'POST':

        data = json.loads(request.body)

        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        try:

            # Verify Razorpay payment signature
            client.utility.verify_payment_signature({
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            })

            print("Payment signature verified successfully.")

            # Find payment record
            payment = Payment.objects.get(
                razorpay_order_id=order_id,
                user=request.user
            )

            # Get seats stored in Payment
            selected_seats = []

            if payment.reserved_seats:
                selected_seats = payment.reserved_seats.split(',')

            if not selected_seats:
                return JsonResponse({
                    'message': 'No reserved seats found.'
                }, status=400)

            theater = payment.theater

            with transaction.atomic():

                # Mark payment successful
                payment.status = 'success'
                payment.razorpay_payment_id = payment_id
                payment.transaction_id = payment_id
                payment.save()

                # Lock selected seats
                seats = Seat.objects.select_for_update().filter(
                    id__in=selected_seats,
                    theater=theater
                )

                for seat in seats:

                    # If seat is already booked
                    if seat.is_booked:

                        booking, created = Booking.objects.get_or_create(
                            user=request.user,
                            seat=seat,
                            movie=theater.movie,
                            theater=theater
                        )

                        if created:
                            transaction.on_commit(
                                lambda booking_id=booking.id:
                                generate_and_send_ticket.delay(
                                    booking_id
                                )
                            )

                        continue

                    # Check user's reservation
                    if (
                        seat.is_reserved
                        and seat.reserved_by == request.user
                    ):

                        # Confirm seat booking
                        seat.is_booked = True
                        seat.is_reserved = False
                        seat.reserved_by = None
                        seat.reserved_at = None
                        seat.save()

                        # Create booking
                        booking, created = Booking.objects.get_or_create(
                            user=request.user,
                            seat=seat,
                            movie=theater.movie,
                            theater=theater
                        )

                        # Generate ticket and send email
                        # after database transaction is committed
                        if created:
                            transaction.on_commit(
                                lambda booking_id=booking.id:
                                generate_and_send_ticket.delay(
                                    booking_id
                                )
                            )

            # Clear session after successful booking
            request.session.pop(
                'reserved_seats',
                None
            )

            request.session.pop(
                'reservation_theater_id',
                None
            )

            print(
                "Payment successful and booking confirmed."
            )

            return JsonResponse({
                'message':
                'Payment successful and booking confirmed.'
            })

        except razorpay.errors.SignatureVerificationError:

            print(
                "Payment signature verification failed."
            )

            return JsonResponse({
                'message':
                'Payment verification failed.'
            }, status=400)

        except Payment.DoesNotExist:

            return JsonResponse({
                'message':
                'Payment record not found.'
            }, status=400)

    return JsonResponse({
        'message':
        'Invalid request.'
    }, status=400)

@login_required(login_url='/login/')
def cancel_payment(request):

    if request.method == 'POST':

        selected_seats = request.session.get(
            'reserved_seats',
            []
        )

        theater_id = request.session.get(
            'reservation_theater_id'
        )

        if not selected_seats or not theater_id:
            return redirect('movie_list')

        theater = get_object_or_404(
            Theater,
            id=theater_id
        )

        payment = Payment.objects.filter(
            user=request.user,
            theater=theater,
            status='created'
        ).order_by('-created_at').first()

        if payment:

            with transaction.atomic():

                payment.status = 'cancelled'
                payment.save()

                Seat.objects.filter(
                    id__in=selected_seats,
                    theater=theater,
                    reserved_by=request.user,
                    is_reserved=True
                ).update(
                    is_reserved=False,
                    reserved_by=None,
                    reserved_at=None
                )

        request.session.pop(
            'reserved_seats',
            None
        )

        request.session.pop(
            'reservation_theater_id',
            None
        )

        return redirect('book_seats', theater_id=theater.id)

    return redirect('movie_list')

@login_required(login_url='/login/')
def failed_payment(request):
    if request.method == 'POST':

        data = json.loads(request.body)

        order_id = data.get('razorpay_order_id')

        payment = Payment.objects.filter(
            razorpay_order_id=order_id,
            user=request.user
        ).first()

        if payment:

            payment.status = 'failed'
            payment.save()

            selected_seats = request.session.get(
                'reserved_seats',
                []
            )

            theater_id = request.session.get(
                'reservation_theater_id'
            )

            if theater_id:

                Seat.objects.filter(
                    id__in=selected_seats,
                    theater_id=theater_id,
                    reserved_by=request.user,
                    is_reserved=True
                ).update(
                    is_reserved=False,
                    reserved_by=None,
                    reserved_at=None
                )

            request.session.pop(
                'reserved_seats',
                None
            )

            request.session.pop(
                'reservation_theater_id',
                None
            )

            return JsonResponse({
                'message': 'Payment failed. Your seats have been released.'
            })

        return JsonResponse({
            'message': 'Payment record not found.'
        }, status=400)

    return JsonResponse({
        'message': 'Invalid request.'
    }, status=400)




@login_required(login_url='/login/')
def booking_history(request):

    bookings = Booking.objects.filter(
        user=request.user
    ).select_related(
        'movie',
        'theater',
        'seat'
    ).order_by('-booked_at')

    payments = Payment.objects.filter(
        user=request.user
    ).select_related(
        'theater',
        'theater__movie'
    ).order_by('-created_at')

    return render(
        request,
        'movies/booking_history.html',
        {
            'bookings': bookings,
            'payments': payments
        }
    )

@csrf_exempt
def razorpay_webhook(request):

    if request.method != 'POST':
        return JsonResponse({
            'message': 'Invalid request.'
        }, status=400)

    webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET

    received_signature = request.headers.get(
        'X-Razorpay-Signature'
    )

    body = request.body

    expected_signature = hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(
        received_signature or '',
        expected_signature
    ):
        return JsonResponse({
            'message': 'Invalid webhook signature.'
        }, status=400)

    data = json.loads(body)

    event = data.get('event')

    print("Razorpay Webhook Event:", event)

    # ---------------------------------
    # PAYMENT CAPTURED
    # ---------------------------------

    if event == 'payment.captured':

        payment_data = data['payload']['payment']['entity']

        payment_id = payment_data['id']
        order_id = payment_data['order_id']

        payment = Payment.objects.filter(
            razorpay_order_id=order_id
        ).first()

        if payment:

            with transaction.atomic():

                payment.status = 'success'
                payment.razorpay_payment_id = payment_id
                payment.transaction_id = payment_id
                payment.save()

                if payment.reserved_seats:

                    seat_ids = payment.reserved_seats.split(',')

                    print(
                        "Seats from payment:",
                        seat_ids
                    )

                    seats = Seat.objects.select_for_update().filter(
                        id__in=seat_ids,
                        theater=payment.theater
                    )

                    for seat in seats:

                        print(
                            "Processing seat:",
                            seat.seat_number
                        )

                        if seat.is_booked:

                            Booking.objects.get_or_create(
                                user=payment.user,
                                seat=seat,
                                movie=payment.theater.movie,
                                theater=payment.theater
                            )

                            continue

                        seat.is_booked = True
                        seat.is_reserved = False
                        seat.reserved_by = None
                        seat.reserved_at = None
                        seat.save()

                        Booking.objects.get_or_create(
                            user=payment.user,
                            seat=seat,
                            movie=payment.theater.movie,
                            theater=payment.theater
                        )

            print(
                "Payment marked as success "
                "and booking confirmed."
            )

    # ---------------------------------
    # PAYMENT FAILED
    # ---------------------------------

    elif event == 'payment.failed':

        payment_data = data['payload']['payment']['entity']

        order_id = payment_data.get('order_id')

        payment = Payment.objects.filter(
            razorpay_order_id=order_id
        ).first()

        if payment:

            if payment.status == 'success':

                return JsonResponse({
                    'message': 'Payment already completed.'
                })

            with transaction.atomic():

                payment.status = 'failed'
                payment.save()

                if payment.reserved_seats:

                    seat_ids = payment.reserved_seats.split(',')

                    Seat.objects.filter(
                        id__in=seat_ids,
                        theater=payment.theater,
                        is_reserved=True,
                        reserved_by=payment.user
                    ).update(
                        is_reserved=False,
                        reserved_by=None,
                        reserved_at=None
                    )

            print(
                "Payment marked as failed "
                "and reserved seats released."
            )

    return JsonResponse({
        'message': 'Webhook received successfully.'
    })

def admin_check(user):
    return user.is_authenticated and user.is_staff


# @user_passes_test(admin_check, login_url='/login/')
# def admin_dashboard(request):

#     return render(
#         request,
#         'movies/admin_dashboard.html'
#     )

# @login_required(login_url='/login/')
# def admin_dashboard(request):

#     if not request.user.is_staff:
#         return redirect('movie_list')

#     total_revenue = Payment.objects.filter(
#         status='success'
#     ).aggregate(
#         total=Sum('amount')
#     )['total'] or 0

#     total_bookings = Booking.objects.count()

#     total_movies = Movie.objects.count()

#     total_users = User.objects.count()

#     total_theaters = Theater.objects.count()

#     context = {
#         'total_revenue': total_revenue,
#         'total_bookings': total_bookings,
#         'total_movies': total_movies,
#         'total_users': total_users,
#         'total_theaters': total_theaters,
#     }

#     return render(
#         request,
#         'movies/admin_dashboard.html',
#         context
#     )

@login_required(login_url='/login/')
def admin_dashboard(request):

    # Only staff/admin user can access dashboard
    if not request.user.is_staff:
        return redirect('movie_list')

    today = timezone.localdate()

    # ==================================================
    # DATE FILTER
    # ==================================================

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    # ==================================================
    # DAILY REVENUE AND BOOKINGS
    # ==================================================

    day_start = timezone.make_aware(
        datetime.combine(
            today,
            datetime.min.time()
        )
    )

    day_end = day_start + timedelta(days=1)

    daily_revenue = Payment.objects.filter(
        status='success',
        created_at__gte=day_start,
        created_at__lt=day_end
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    daily_bookings = Booking.objects.filter(
        booked_at__gte=day_start,
        booked_at__lt=day_end
    ).count()

    # ==================================================
    # WEEKLY REVENUE AND BOOKINGS
    # ==================================================

    week_start_date = today - timedelta(
        days=today.weekday()
    )

    week_start = timezone.make_aware(
        datetime.combine(
            week_start_date,
            datetime.min.time()
        )
    )

    week_end = week_start + timedelta(days=7)

    weekly_revenue = Payment.objects.filter(
        status='success',
        created_at__gte=week_start,
        created_at__lt=week_end
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    weekly_bookings = Booking.objects.filter(
        booked_at__gte=week_start,
        booked_at__lt=week_end
    ).count()

    # ==================================================
    # MONTHLY REVENUE AND BOOKINGS
    # ==================================================

    month_start = timezone.make_aware(
        datetime(
            today.year,
            today.month,
            1
        )
    )

    if today.month == 12:

        next_month = datetime(
            today.year + 1,
            1,
            1
        )

    else:

        next_month = datetime(
            today.year,
            today.month + 1,
            1
        )

    month_end = timezone.make_aware(next_month)

    monthly_revenue = Payment.objects.filter(
        status='success',
        created_at__gte=month_start,
        created_at__lt=month_end
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    monthly_bookings = Booking.objects.filter(
        booked_at__gte=month_start,
        booked_at__lt=month_end
    ).count()

    # ==================================================
    # YEARLY REVENUE AND BOOKINGS
    # ==================================================

    year_start = timezone.make_aware(
        datetime(
            today.year,
            1,
            1
        )
    )

    next_year = timezone.make_aware(
        datetime(
            today.year + 1,
            1,
            1
        )
    )

    yearly_revenue = Payment.objects.filter(
        status='success',
        created_at__gte=year_start,
        created_at__lt=next_year
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    yearly_bookings = Booking.objects.filter(
        booked_at__gte=year_start,
        booked_at__lt=next_year
    ).count()

    # ==================================================
    # CUSTOM DATE RANGE
    # ==================================================

    custom_revenue = None
    custom_bookings = None

    if from_date and to_date:

        try:

            start_date = datetime.strptime(
                from_date,
                '%Y-%m-%d'
            ).date()

            end_date = datetime.strptime(
                to_date,
                '%Y-%m-%d'
            ).date()

            custom_start = timezone.make_aware(
                datetime.combine(
                    start_date,
                    datetime.min.time()
                )
            )

            custom_end = timezone.make_aware(
                datetime.combine(
                    end_date + timedelta(days=1),
                    datetime.min.time()
                )
            )

            custom_revenue = Payment.objects.filter(
                status='success',
                created_at__gte=custom_start,
                created_at__lt=custom_end
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0

            custom_bookings = Booking.objects.filter(
                booked_at__gte=custom_start,
                booked_at__lt=custom_end
            ).count()

        except ValueError:

            custom_revenue = 0
            custom_bookings = 0

    # ==================================================
    # BOOKING TRENDS
    # ==================================================

    booking_trends = []

    if from_date and to_date:

        try:

            trend_start = datetime.strptime(
                from_date,
                '%Y-%m-%d'
            ).date()

            trend_end = datetime.strptime(
                to_date,
                '%Y-%m-%d'
            ).date()

            current_date = trend_start

            while current_date <= trend_end:

                booking_count = Booking.objects.filter(
                    booked_at__date=current_date
                ).count()

                booking_trends.append({
                    'date': current_date,
                    'count': booking_count
                })

                current_date += timedelta(days=1)

        except ValueError:

            booking_trends = []

    else:

        for i in range(6, -1, -1):

            trend_date = today - timedelta(days=i)

            booking_count = Booking.objects.filter(
                booked_at__date=trend_date
            ).count()

            booking_trends.append({
                'date': trend_date,
                'count': booking_count
            })

    # ==================================================
    # THEATER OCCUPANCY
    # ==================================================

    theater_occupancy = []

    theaters = Theater.objects.all()

    for theater in theaters:

        total_seats = Seat.objects.filter(
            theater=theater
        ).count()

        booked_seats = Seat.objects.filter(
            theater=theater,
            is_booked=True
        ).count()

        if total_seats > 0:

            occupancy = (
                booked_seats / total_seats
            ) * 100

        else:

            occupancy = 0

        theater_occupancy.append({
            'name': theater.name,
            'total_seats': total_seats,
            'booked_seats': booked_seats,
            'occupancy': round(occupancy, 2)
        })

    # ==================================================
    # MOST BOOKED MOVIES
    # ==================================================

    if from_date and to_date:

        most_booked_movies = Movie.objects.filter(
            booking__booked_at__gte=custom_start,
            booking__booked_at__lt=custom_end
        ).annotate(
            booking_count=Count('booking')
        ).order_by(
            '-booking_count'
        )[:10]

    else:

        most_booked_movies = Movie.objects.annotate(
            booking_count=Count('booking')
        ).order_by(
            '-booking_count'
        )[:10]

    # ==================================================
    # TOP PERFORMING THEATERS
    # ==================================================

    if from_date and to_date:

        top_theaters = Theater.objects.filter(
            booking__booked_at__gte=custom_start,
            booking__booked_at__lt=custom_end
        ).annotate(
            booking_count=Count('booking')
        ).order_by(
            '-booking_count'
        )[:10]

    else:

        top_theaters = Theater.objects.annotate(
            booking_count=Count('booking')
        ).order_by(
            '-booking_count'
        )[:10]

    # ==================================================
    # PEAK BOOKING HOURS
    # ==================================================

    peak_booking_hours = []

    if from_date and to_date:

        filtered_bookings = Booking.objects.filter(
            booked_at__gte=custom_start,
            booked_at__lt=custom_end
        )

    else:

        filtered_bookings = Booking.objects.filter(
            booked_at__gte=year_start,
            booked_at__lt=next_year
        )

    hour_counts = (
        filtered_bookings
        .annotate(
            booking_hour=ExtractHour('booked_at')
        )
        .values('booking_hour')
        .annotate(
            count=Count('id')
        )
        .order_by('-count')[:10]
    )

    for item in hour_counts:

        peak_booking_hours.append({
            'hour': item['booking_hour'],
            'count': item['count']
        })

    # ==================================================
    # CANCELLATION AND REFUND STATISTICS
    # ==================================================

    if from_date and to_date:

        cancellation_queryset = Payment.objects.filter(
            created_at__gte=custom_start,
            created_at__lt=custom_end
        )

    else:

        cancellation_queryset = Payment.objects.all()

    cancelled_payments = cancellation_queryset.filter(
        status='cancelled'
    ).count()

    failed_payments = cancellation_queryset.filter(
        status='failed'
    ).count()

    refunded_payments = cancellation_queryset.filter(
        status='refunded'
    ).count()

    refund_amount = cancellation_queryset.filter(
        status='refunded'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    # ==================================================
    # USER GROWTH
    # ==================================================

    user_growth = []

    if from_date and to_date:

        try:

            growth_start = datetime.strptime(
                from_date,
                '%Y-%m-%d'
            ).date()

            growth_end = datetime.strptime(
                to_date,
                '%Y-%m-%d'
            ).date()

            current_date = growth_start

            while current_date <= growth_end:

                new_users = User.objects.filter(
                    date_joined__date=current_date
                ).count()

                user_growth.append({
                    'date': current_date,
                    'count': new_users
                })

                current_date += timedelta(days=1)

        except ValueError:

            user_growth = []

    else:

        for i in range(6, -1, -1):

            growth_date = today - timedelta(days=i)

            new_users = User.objects.filter(
                date_joined__date=growth_date
            ).count()

            user_growth.append({
                'date': growth_date,
                'count': new_users
            })

    # ==================================================
    # OVERALL BUSINESS SUMMARY
    # ==================================================

    total_revenue = Payment.objects.filter(
        status='success'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_bookings = Booking.objects.count()

    total_movies = Movie.objects.count()

    total_users = User.objects.count()

    total_theaters = Theater.objects.count()

    # ==================================================
    # CONTEXT
    # ==================================================

    context = {

        'total_revenue': total_revenue,
        'total_bookings': total_bookings,
        'total_movies': total_movies,
        'total_users': total_users,
        'total_theaters': total_theaters,

        'daily_revenue': daily_revenue,
        'daily_bookings': daily_bookings,

        'weekly_revenue': weekly_revenue,
        'weekly_bookings': weekly_bookings,

        'monthly_revenue': monthly_revenue,
        'monthly_bookings': monthly_bookings,

        'yearly_revenue': yearly_revenue,
        'yearly_bookings': yearly_bookings,

        'custom_revenue': custom_revenue,
        'custom_bookings': custom_bookings,

        'from_date': from_date,
        'to_date': to_date,

        'booking_trends': booking_trends,

        'theater_occupancy': theater_occupancy,

        'most_booked_movies': most_booked_movies,

        'top_theaters': top_theaters,

        'peak_booking_hours': peak_booking_hours,

        'cancelled_payments': cancelled_payments,
        'failed_payments': failed_payments,
        'refunded_payments': refunded_payments,
        'refund_amount': refund_amount,

        'user_growth': user_growth,
    }

    return render(
        request,
        'movies/admin_dashboard.html',
        context
    )

@login_required(login_url='/login/')
def export_booking_report(request):

    if not request.user.is_staff:
        return redirect('movie_list')

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    bookings = Booking.objects.select_related(
        'user',
        'movie',
        'theater',
        'seat'
    ).order_by(
        '-booked_at'
    )

    if from_date and to_date:

        try:

            start_date = datetime.strptime(
                from_date,
                '%Y-%m-%d'
            ).date()

            end_date = datetime.strptime(
                to_date,
                '%Y-%m-%d'
            ).date()

            start_datetime = timezone.make_aware(
                datetime.combine(
                    start_date,
                    datetime.min.time()
                )
            )

            end_datetime = timezone.make_aware(
                datetime.combine(
                    end_date + timedelta(days=1),
                    datetime.min.time()
                )
            )

            bookings = bookings.filter(
                booked_at__gte=start_datetime,
                booked_at__lt=end_datetime
            )

        except ValueError:
            pass

    response = HttpResponse(
        content_type='text/csv'
    )

    response['Content-Disposition'] = (
        'attachment; filename="booking_report.csv"'
    )

    response.write(
        'User,Movie,Theater,Seat,Booking Date\n'
    )

    for booking in bookings.iterator():

        response.write(
            f'{booking.user.username},'
            f'{booking.movie.name},'
            f'{booking.theater.name},'
            f'{booking.seat.seat_number},'
            f'{booking.booked_at}\n'
        )

    return response

@login_required(login_url='/login/')
def download_ticket(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if not booking.ticket:
        return redirect('booking_history')

    response = FileResponse(
        booking.ticket.open('rb'),
        as_attachment=True,
        filename=f'ticket_{booking.id}.pdf'
    )

    return response

@login_required(login_url='/login/')
def verify_ticket(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    return render(
        request,
        'movies/verify_ticket.html',
        {
            'booking': booking
        }
    )