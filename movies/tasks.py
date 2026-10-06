import os
import qrcode

from io import BytesIO

from celery import shared_task

from django.conf import settings
from django.core.files import File
from django.core.mail import EmailMessage
from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .models import Booking


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3}
)
def generate_and_send_ticket(self, booking_id):

    booking = Booking.objects.select_related(
        'user',
        'movie',
        'theater',
        'seat'
    ).get(id=booking_id)

    # -----------------------------
    # Convert time to Indian time
    # -----------------------------

    show_time = timezone.localtime(booking.theater.time)
    booked_at = timezone.localtime(booking.booked_at)

    show_time_text = show_time.strftime("%d %b %Y, %I:%M %p")
    booked_at_text = booked_at.strftime("%d %b %Y, %I:%M %p")

    # -----------------------------
    # Generate QR Code
    # -----------------------------

    # qr_data = (
    #     f"Booking ID: {booking.id}\n"
    #     f"Username: {booking.user.username}\n"
    #     f"Movie: {booking.movie.name}\n"
    #     f"Theater: {booking.theater.name}\n"
    #     f"Screen: {booking.theater.screen}\n"
    #     f"Show Time: {show_time_text}\n"
    #     f"Seat: {booking.seat.seat_number}\n"
    #     f"Ticket Price: Rs. {booking.theater.ticket_price}\n"
    # )
    qr_data = f"http://127.0.0.1:8000/verify/{booking.id}/"

    qr = qrcode.make(qr_data)

    qr_buffer = BytesIO()
    qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    # -----------------------------
    # Generate PDF
    # -----------------------------

    pdf_buffer = BytesIO()

    pdf = canvas.Canvas(
        pdf_buffer,
        pagesize=A4
    )

    width, height = A4

    y = height - 60

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawCentredString(
        width / 2,
        y,
        "BOOKMYSHOW TICKET"
    )

    y -= 50

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        60,
        y,
        f"Booking ID: {booking.id}"
    )

    y -= 25

    pdf.drawString(
        60,
        y,
        f"Username: {booking.user.username}"
    )

    y -= 25

    pdf.drawString(
        60,
        y,
        f"Movie: {booking.movie.name}"
    )

    y -= 25

    pdf.drawString(
        60,
        y,
        f"Theater: {booking.theater.name}"
    )

    y -= 25

    pdf.drawString(
        60,
        y,
        f"Screen: {booking.theater.screen}"
    )

    y -= 25

    pdf.drawString(
        60,
        y,
        f"Show Time: {show_time_text}"
    )

    y -= 25

    pdf.drawString(
        60,
        y,
        f"Seat: {booking.seat.seat_number}"
    )

    y -= 25

    pdf.drawString(
        60,
        y,
        f"Ticket Price: Rs. {booking.theater.ticket_price}"
    )

    y -= 25

    pdf.drawString(
        60,
        y,
        f"Booked At: {booked_at_text}"
    )

    # -----------------------------
    # QR Code in PDF
    # -----------------------------

    qr_buffer.seek(0)

    qr_path = os.path.join(
        settings.MEDIA_ROOT,
        "temp_booking_qr.png"
    )

    with open(qr_path, "wb") as qr_file:
        qr_file.write(qr_buffer.read())

    pdf.drawImage(
        qr_path,
        width - 180,
        height - 300,
        width=110,
        height=110
    )

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        60,
        y - 50,
        "Ticket confirmed successfully."
    )

    pdf.save()

    pdf_buffer.seek(0)

    # -----------------------------
    # Save PDF in Booking.ticket
    # -----------------------------

    file_name = (
        f"ticket_{booking.id}.pdf"
    )

    booking.ticket.save(
        file_name,
        File(pdf_buffer),
        save=True
    )

    # -----------------------------
    # Send Email
    # -----------------------------

    if booking.user.email:

        email = EmailMessage(
            subject="Your BookMyShow Ticket",
            body=(
                f"Hello {booking.user.username},\n\n"
                f"Your booking has been confirmed.\n\n"
                f"Username: {booking.user.username}\n"
                f"Movie: {booking.movie.name}\n"
                f"Theater: {booking.theater.name}\n"
                f"Screen: {booking.theater.screen}\n"
                f"Show Time: {show_time_text}\n"
                f"Seat: {booking.seat.seat_number}\n"
                f"Ticket Price: Rs. {booking.theater.ticket_price}\n"
                f"Booking ID: {booking.id}\n"
                f"Booked At: {booked_at_text}\n\n"
                f"Your ticket is attached with this email.\n\n"
                f"Thank you for booking with BookMyShow."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.user.email]
        )

        email.attach_file(
            booking.ticket.path
        )

        email.send(
            fail_silently=False
        )

    # -----------------------------
    # Delete temporary QR image
    # -----------------------------

    if os.path.exists(qr_path):
        os.remove(qr_path)

    return f"Ticket generated for booking {booking.id}"