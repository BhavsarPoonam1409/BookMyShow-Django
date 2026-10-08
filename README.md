# BookMyShow - Django Movie Ticket Booking System

This is a movie ticket booking web application developed using Django as part of my Full Stack Web Development internship.

The project allows users to browse movies, select a theater and show, choose seats, make a payment, and get their booking details.

## Live Project

The project is deployed and can be accessed here:

**Live Website:**
https://bookmyshow-django-faaq.onrender.com/

You can open the website directly and test the movie booking flow.

## Features

* User registration and login
* Movie listing and movie details
* Theater and show selection
* Seat selection
* Movie reviews and ratings
* Razorpay payment integration
* Booking history
* Ticket PDF generation
* Email ticket
* Booking timer
* Responsive design for mobile and tablet
* Django admin panel for managing data

## Technologies Used

* Python
* Django
* HTML
* CSS
* JavaScript
* Bootstrap
* Sqlite3 / PostgreSQL
* Razorpay
* Celery
* Redis
* ReportLab

## Project Structure

```text
BookMyShow/
│
├── BookMyShow/
├── movies/
├── booking/
├── seat/
├── theater/
├── templates/
├── static/
├── manage.py
└── requirements.txt
```

## How to Run the Project

Clone the repository and open the project folder.

```bash
git clone https://github.com/BhavsarPoonam1409/BookMyShow-Django.git
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Start the Django server:

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## Admin Panel

The project also includes a Django admin panel for managing movies, theaters, shows, bookings and other project data.

Admin credentials are provided separately in the internship project report for evaluation.

## Internship Project

This project was developed as part of the **Full Stack Web Development Internship at ElevanceSkills**.

The project was built by adding the required internship tasks and features to the training project.

## Author

**Poonam Bhavsar**

M.Sc. IT (Software Development)
Gujarat University
