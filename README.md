<h1 align="center">UrbanKart</h1>

UrbanKart is a full-fledged e-commerce platform built with Django, featuring product management, cart functionality, payment integration, user authentication, and deployment on AWS Elastic Beanstalk.

---

## Introduction

UrbanKart is designed to provide a smooth online shopping experience with features like dynamic product variations, cart management, PayPal integration, user authentication, and more.

---

## Installation and Setup

1. **Install Git and Atom.**  
2. **Set up a virtual environment:**  
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Linux/Mac
    venv\Scripts\activate    # For Windows
    ```
3. **Install Django and dependencies:**  
    ```bash
    pip install -r requirements.txt
    ```
4. **Configure your environment variables and database.**  
5. **Run migrations:**  
    ```bash
    python manage.py migrate
    ```
6. **Create a superuser:**  
    ```bash
    python manage.py createsuperuser
    ```
7. **Run the server:**  
    ```bash
    python manage.py runserver
    ```
---

## Project Structure

```plaintext
UrbanKart/
├── manage.py
├── db.sqlite3
├── products/
├── carts/
├── orders/
└── templates/
```

---

## Core Features

- Product management with categories and dynamic variations.  
- Cart functionality with increment, decrement, and remove options.  
- Tax and total calculation.  
- Search functionality.  
- Product reviews and ratings.  
- User dashboard with order history and profile management.  
- Secure authentication and password reset.  
- Admin panel enhancements.  

---

## Payment Integration

- Integrated PayPal payment gateway.  
- Order processing with email notifications.  
- Dynamic cart handling for logged-in users.  

---

## User Authentication

- Custom user model.  
- Email verification.  
- Password reset and change password functionality.  
- Automatic logout after inactivity.  

---

## Deployment on AWS

1. **Create an AWS account.**  
2. **Set up IAM user and budget.**  
3. **Configure Django for Elastic Beanstalk.**  
4. **Deploy:**  
    ```bash
    eb init
    eb create UrbanKart-env
    ```
5. **Set up a custom domain and SSL certificate.**  

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---

**Happy coding! 🚀**
