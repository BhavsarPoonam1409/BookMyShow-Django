from io import BytesIO

import qrcode

from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


def generate_ticket(booking, payment):

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    width, height = A4

    # -----------------------------
    # Convert time to Indian time
    # -----------------------------

    show_time = timezone.localtime(
        booking.theater.time
    )

    booked_at = timezone.localtime(
        booking.booked_at
    )

    show_time_text = show_time.strftime(
        "%d %b %Y, %I:%M %p"
    )

    booked_at_text = booked_at.strftime(
        "%d %b %Y, %I:%M %p"
    )

    # -----------------------------
    # Ticket heading
    # -----------------------------

    pdf.setFont(
        "Helvetica-Bold",
        22
    )

    pdf.drawString(
        50,
        height - 60,
        "BOOKMYSHOW"
    )

    pdf.setFont(
        "Helvetica-Bold",
        16
    )

    pdf.drawString(
        50,
        height - 95,
        "Movie Ticket"
    )

    # -----------------------------
    # Movie details
    # -----------------------------

    pdf.setFont(
        "Helvetica",
        11
    )

    y = height - 140

    pdf.drawString(
        50,
        y,
        f"Username: {booking.user.username}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Movie: {booking.movie.name}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Theater: {booking.theater.name}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"City: {booking.theater.city}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Screen: {booking.theater.screen}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Show Time: {show_time_text}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Seat: {booking.seat.seat_number}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Ticket Price: Rs. {booking.theater.ticket_price}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Booking ID: {booking.id}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Booked At: {booked_at_text}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Payment Reference: {payment.razorpay_payment_id}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Amount: Rs. {payment.amount}"
    )

    # -----------------------------
    # QR Code data
    # -----------------------------

    qr_data = (
        f"Booking ID: {booking.id}\n"
        f"Username: {booking.user.username}\n"
        f"Movie: {booking.movie.name}\n"
        f"Theater: {booking.theater.name}\n"
        f"Screen: {booking.theater.screen}\n"
        f"Show Time: {show_time_text}\n"
        f"Seat: {booking.seat.seat_number}\n"
        f"Ticket Price: Rs. {booking.theater.ticket_price}\n"
        f"Payment: {payment.razorpay_payment_id}"
    )

    qr = qrcode.make(
        qr_data
    )

    qr_buffer = BytesIO()

    qr.save(
        qr_buffer,
        format="PNG"
    )

    qr_buffer.seek(0)

    from reportlab.lib.utils import ImageReader

    qr_image = ImageReader(
        qr_buffer
    )

    pdf.drawImage(
        qr_image,
        width - 180,
        100,
        width=100,
        height=100
    )

    # -----------------------------
    # Footer
    # -----------------------------

    pdf.setFont(
        "Helvetica-Bold",
        10
    )

    pdf.drawString(
        50,
        70,
        "Ticket confirmed successfully."
    )

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawString(
        50,
        55,
        "Please carry this ticket for verification."
    )

    pdf.drawString(
        50,
        40,
        "Thank you for booking with BookMyShow."
    )

    pdf.showPage()

    pdf.save()

    buffer.seek(0)

    return buffer