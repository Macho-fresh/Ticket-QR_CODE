# Ticket QR Code API

A backend API for managing events, ticket purchases, payments, QR-code ticket generation, attendee management, and event check-ins.

The project is built with Django and Django REST Framework and provides a complete event ticketing workflow. Event staff can create and manage events, users can purchase tickets, payments can be verified, unique tickets can be generated, and attendees can be checked in using QR tokens.

## Table of Contents

* [Features](#features)
* [Tech Stack](#tech-stack)
* [Project Workflow](#project-workflow)
* [Installation](#installation)
* [Environment Variables](#environment-variables)
* [Database Setup](#database-setup)
* [Running the Application](#running-the-application)
* [API Endpoints](#api-endpoints)

  * [Create Event](#1-create-event)
  * [View Events](#2-view-events)
  * [Edit Event](#3-edit-event)
  * [Delete Event](#4-delete-event)
  * [Create Ticket](#5-create-ticket)
  * [View Tickets](#6-view-tickets)
  * [View One Ticket](#7-view-one-ticket)
  * [Get Attendees](#8-get-attendees)
  * [Export Attendees as CSV](#9-export-attendees-as-csv)
  * [Check In Attendee](#10-check-in-attendee)
  * [Payment](#11-payment)
* [Authentication](#authentication)
* [Celery and Redis](#celery-and-redis)
* [Running Tests](#running-tests)
* [Load Testing](#load-testing)
* [Continuous Integration](#continuous-integration)
* [Docker](#docker)
* [Project Structure](#project-structure)
* [Future Improvements](#future-improvements)
* [Author](#author)

---

# Features

* User authentication
* Event creation and management
* Event editing and deletion
* Event listing
* Ticket creation
* Payment processing and verification
* Unique QR tokens for tickets
* Ticket retrieval
* Individual ticket viewing
* Attendee management
* Attendee CSV export
* QR-based event check-in
* Duplicate check-in prevention
* Celery background tasks
* Redis integration
* PostgreSQL database
* Automated API testing
* GitHub Actions CI
* Docker support
* Load testing with Locust

# Tech Stack

* Python
* Django
* Django REST Framework
* PostgreSQL
* Redis
* Celery
* JWT Authentication
* Docker
* GitHub Actions
* Locust

# Project Workflow

```text
User
  |
  v
View Available Events
  |
  v
Select Event
  |
  v
Make Payment
  |
  v
Payment Verification
  |
  v
Ticket Generated
  |
  v
Unique QR Token Created
  |
  v
Attend Event
  |
  v
QR Token Scanned
  |
  v
Ticket Validated
  |
  v
Attendee Checked In
```

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/Macho-fresh/Ticket-QR_CODE.git
cd Ticket-QR_CODE
```

## 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it.

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

# Environment Variables

Create a `.env` file in the project root.

Example:

```env
DJANGO_SECRET_KEY=your_django_secret_key
DEBUG=True

POSTGRES_DB=ticket_qr_code
POSTGRES_USER=ticket_user
POSTGRES_PASSWORD=your_database_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_app_password

SECRET_KEY=your_payment_secret_key
```

Do not commit real environment variables or secrets to GitHub.

# Database Setup

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create a superuser if needed:

```bash
python manage.py createsuperuser
```

# Running the Application

Start the development server:

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

# API Endpoints

The API provides endpoints for managing the complete event lifecycle, from creating an event to generating tickets and checking attendees into an event.

The base URL for the endpoints is:

```text
/api/
```

---

## 1. Create Event

### Endpoint

```http
POST /api/create-event/
```

Creates a new event.

The event creator provides details such as:

* Event title
* Description
* Location
* Start date and time
* End date and time
* Capacity
* Ticket price

The authenticated user creating the event becomes the event owner or creator.

Example request body:

```json
{
    "title": "Tech Fest 042",
    "description": "The biggest Tech Fest in 042",
    "location": "Enugu",
    "start_at": "2026-08-15T09:00:00Z",
    "end_at": "2026-08-16T15:00:00Z",
    "capacity": 100,
    "price": 10.00
}
```

---

## 2. View Events

### Endpoint

```http
GET /api/view-events/
```

Returns the available events in the system.

This endpoint can be used to display events to users before they decide which event they want to attend or purchase a ticket for.

Example response:

```json
[
    {
        "id": 1,
        "title": "Tech Fest 042",
        "description": "The biggest Tech Fest in 042",
        "location": "Enugu",
        "capacity": 100,
        "price": "10.00"
    }
]
```

This endpoint was also used during load testing with Locust.

---

## 3. Edit Event

### Endpoint

```http
PUT /api/edit-events/<id>/
```

Updates an existing event.

The event ID is passed through the URL.

Example:

```text
/api/edit-events/1/
```

The event owner can update event details such as:

* Title
* Description
* Location
* Start time
* End time
* Capacity
* Price

Example request body:

```json
{
    "title": "Tech Fest 2026",
    "description": "Updated event description",
    "location": "Lagos",
    "capacity": 200,
    "price": 20.00
}
```

---

## 4. Delete Event

### Endpoint

```http
DELETE /api/delete-event/<id>/
```

Deletes an event.

The event ID identifies the event that should be removed.

Example:

```text
/api/delete-event/1/
```

This allows an event creator or authorized user to remove an event from the system.

---

## 5. Create Ticket

### Endpoint

```http
GET /api/create-ticket/?reference=<payment_reference>
```

Creates a ticket after payment verification.

The payment reference is passed as a query parameter.

Example:

```text
/api/create-ticket/?reference=test_reference_123
```

The system uses the payment reference to verify the payment and determine whether a valid ticket should be created.

Once the payment is successfully verified, the system can:

1. Confirm the payment.
2. Identify the associated event.
3. Create a ticket for the user.
4. Generate a unique QR token.
5. Associate the ticket with the event and ticket owner.

The QR token is later used during event check-in.

---

## 6. View Tickets

### Endpoint

```http
GET /api/view-tickets/
```

Returns the tickets belonging to the authenticated user.

This allows a user to view the tickets they have purchased or generated.

A ticket is associated with:

* The event
* The ticket owner
* A unique QR token
* Its check-in status

Example ticket information may include:

```json
{
    "id": 1,
    "event": 1,
    "owner": "username",
    "qr_token": "unique-ticket-token",
    "checked_in": false
}
```

---

## 7. View One Ticket

### Endpoint

```http
GET /api/view-one-ticket/<id>/
```

Returns information about a specific ticket or event-related ticket resource identified by its ID.

Example:

```text
/api/view-one-ticket/1/
```

This endpoint allows an authenticated user to retrieve detailed information instead of retrieving their entire ticket collection.

Access is restricted so that users should not be able to access tickets that do not belong to them.

---

## 8. Get Attendees

### Endpoint

```http
GET /api/get-attendees/<id>/
```

Returns the attendees associated with a specific event.

The event ID is passed through the URL.

Example:

```text
/api/get-attendees/1/
```

This allows event organizers or event staff to retrieve attendee information for an event.

The information can be useful for:

* Viewing registered attendees
* Managing attendance
* Checking ticket ownership
* Event reporting

---

## 9. Export Attendees as CSV

### Endpoint

```http
GET /api/get-attendees-csv/<id>/
```

Exports attendee information for a specific event as a CSV file.

Example:

```text
/api/get-attendees-csv/1/
```

The CSV export can be useful for:

* Attendance records
* Event reporting
* Spreadsheet analysis
* External record keeping

The endpoint allows event-related attendee data to be downloaded instead of only being returned as JSON.

---

## 10. Check In Attendee

### Endpoint

```http
POST /api/check-in/<token>/
```

Checks an attendee into an event using their unique QR token.

Example:

```text
/api/check-in/your_unique_qr_token/
```

The check-in process works as follows:

```text
QR Token
   |
   v
Find Ticket
   |
   v
Validate Ticket
   |
   v
Check Event Status
   |
   +---- Invalid/Ended/Already Checked In
   |              |
   |              v
   |           Reject
   |
   v
Mark Ticket as Checked In
   |
   v
Return Successful Response
```

The endpoint prevents invalid check-ins such as:

* Using an invalid QR token
* Checking in a ticket that has already been checked in
* Checking into an event that has ended

The ticket's `checked_in` status is updated after a successful check-in.

---

## 11. Payment

### Endpoint

```http
POST /api/payment/
```

Handles the payment process for event tickets.

The payment endpoint is responsible for initiating or processing payment-related operations before a ticket is generated.

The payment workflow is connected to the ticket generation process:

```text
User
  |
  v
Select Event
  |
  v
Payment Request
  |
  v
Payment Reference Created
  |
  v
Payment Completed
  |
  v
Payment Verified
  |
  v
Ticket Created
```

A payment record can store information such as:

* Payment reference
* User
* Event
* Amount
* Payment status

The payment reference is then used when creating the ticket.

# Authentication

The API uses JWT authentication.

Authenticated requests include a token in the request header:

```http
Authorization: Bearer <access_token>
```

Example:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Authentication is required for protected operations such as:

* Creating events
* Editing events
* Deleting events
* Viewing user tickets
* Creating tickets
* Checking attendees into events
* Accessing event management resources

# Celery and Redis

Celery is used to handle background tasks.

Redis acts as the message broker and result backend.

For example, asynchronous tasks can be used for operations such as sending emails without forcing the API request to wait for the email process to complete.

The workflow looks like:

```text
Django API
    |
    v
Celery Task
    |
    v
Redis
    |
    v
Celery Worker
    |
    v
Background Task Completed
```

Start Redis:

```bash
redis-server
```

Start the Celery worker:

```bash
celery -A <project_name> worker --loglevel=info
```

Replace `<project_name>` with the name of the Django project containing your Celery configuration.

# Running Tests

The project contains automated tests for its API functionality.

Run all tests using:

```bash
python manage.py test
```

The test suite covers different areas of the application, including functionality such as:

* Event creation
* Ticket capacity handling
* Payment verification
* Ticket access
* Attendee check-in
* Event status validation
* CSV attendee export

Django automatically creates a separate test database while running the tests.

# Load Testing

The project uses Locust to test API performance under concurrent traffic.

Install Locust:

```bash
pip install locust
```

Run Locust:

```bash
locust
```

Then open:

```text
http://localhost:8089
```

One of the endpoints tested is:

```text
GET /api/view-events/
```

Locust can simulate multiple concurrent users and provide metrics such as:

* Total requests
* Failed requests
* Requests per second
* Average response time
* Minimum response time
* Maximum response time
* Response time percentiles

A typical load-testing process is:

```text
10 Users
   |
   v
Measure Performance
   |
   v
50 Users
   |
   v
Measure Performance
   |
   v
100 Users
   |
   v
Identify Bottlenecks
   |
   v
Optimize
   |
   v
Test Again
```

Load testing helps identify problems such as:

* Slow database queries
* Server overload
* Connection resets
* High response times
* Failed requests
* Infrastructure bottlenecks

# Continuous Integration

The project uses GitHub Actions for Continuous Integration.

When code is pushed to the main branch or a pull request is created, the CI pipeline can automatically:

1. Check out the repository.
2. Set up Python.
3. Install project dependencies.
4. Start required services.
5. Configure environment variables.
6. Run the automated test suite.

The workflow helps catch errors before changes are merged or deployed.

Example CI flow:

```text
Developer Pushes Code
        |
        v
GitHub Actions
        |
        v
Install Dependencies
        |
        v
Start PostgreSQL/Redis
        |
        v
Run Tests
        |
        +------ Tests Pass ------> CI Successful
        |
        +------ Tests Fail ------> CI Failed
```

# Docker

The project includes Docker configuration for containerized development and deployment.

Build and start the services with:

```bash
docker compose up --build
```

Docker can be used to run the application alongside supporting services such as:

* PostgreSQL
* Redis
* Django application

# Project Structure

```text
Ticket-QR_CODE/
│
├── .github/
│   └── workflows/
│       └── CI configuration
│
├── app/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── tasks.py
│   └── tests.py
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
│
├── project/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── other configuration
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
├── locustfile.py
└── README.md
```

# Future Improvements

Potential improvements include:

* API rate limiting
* Database indexing
* Query optimization
* Redis caching
* Gunicorn deployment
* Multiple application workers
* Reverse proxy configuration
* Load balancing
* Monitoring and metrics
* Structured logging
* API documentation with Swagger or OpenAPI
* Background task monitoring
* Production deployment
* Distributed caching

# Author

Macho Michael

GitHub: https://github.com/Macho-fresh

# License

This project is available for educational and portfolio purposes.
