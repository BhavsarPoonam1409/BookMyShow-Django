from django.urls import path
from . import views
urlpatterns=[
    path('',views.movie_list,name='movie_list'),
    path('<int:movie_id>/theaters',views.theater_list,name='theater_list'),
    path('theater/<int:theater_id>/seats/book/',views.book_seats,name='book_seats'),
    path('<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/report/', views.report_review, name='report_review'),
    path('reservation/', views.reservation, name='reservation'),
    path('payment-response/', views.payment_response, name='payment_response'),
    path('cancel-payment/', views.cancel_payment, name='cancel_payment'),
    path('payment-failed/', views.failed_payment, name='failed_payment'),
    path('razorpay-webhook/', views.razorpay_webhook, name='razorpay_webhook'),
    path('booking-history/', views.booking_history, name='booking_history'),
    path('admin-dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('admin-dashboard/export/',views.export_booking_report,name='export_booking_report'),
    path('booking/<int:booking_id>/ticket/',views.download_ticket,name='download_ticket'),
    path('verify/<int:booking_id>/',views.verify_ticket,name='verify_ticket'
),
]