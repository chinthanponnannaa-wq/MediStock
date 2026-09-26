# MediStock

### Medical Inventory & Billing Management System

MediStock is a Django-based web application designed to simplify medical-store operations by bringing medicine management, inventory tracking, supplier management, billing, sales, and reporting into a single system.

> **Smart Medical Inventory. Simple Billing. Better Management.**

## Overview

MediStock helps medical-store staff manage day-to-day inventory and billing operations through a centralized web interface.

The system provides functionality for:

- Medicine management
- Inventory and stock tracking
- Low-stock monitoring
- Expiry tracking
- Supplier management
- Medicine sales and billing
- Transaction management
- Revenue reporting
- Inventory reports
- User authentication

## Features

### 📊 Dashboard

A centralized dashboard provides an overview of important store information, including inventory status, low-stock medicines, recent sales, and revenue information.

### 💊 Medicine Management

- Add and manage medicines
- Search medicine records
- Track medicine batches
- Monitor available quantities
- Track expiry dates

### 📦 Inventory Management

- Monitor stock quantities
- Identify low-stock medicines
- Track expired medicines
- Update inventory after sales
- Manage medicine batches

### 🧾 Billing & Sales

- Select medicines for sale
- Manage quantities
- Calculate transaction totals
- Generate billing receipts
- Maintain sales records
- Automatically update inventory after transactions

### 🏢 Supplier Management

- Add suppliers
- Maintain supplier information
- Record medicine supplies
- Manage supplied medicines

### 📈 Reports

MediStock provides reporting functionality for:

- Revenue
- Sales
- Inventory
- Expired medicines
- Low-stock medicines
- Transactions

### 🔐 Authentication

The application includes user registration, login, logout, and password-management functionality.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Django 6.1.1 | Web framework |
| SQLite | Database |
| HTML5 | Frontend structure |
| CSS3 | Styling |
| Bootstrap 4 | UI components |
| django-crispy-forms | Form rendering |
| crispy-bootstrap4 | Bootstrap form templates |
| python-dotenv | Environment configuration |
| Git & GitHub | Version control |

## Project Structure

```text
MediStock/
│
├── manage.py
├── requirements.txt
├── .gitignore
│
├── msa/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── shop/
    ├── migrations/
    ├── templates/
    ├── static/
    ├── templatetags/
    ├── models.py
    ├── views.py
    ├── forms.py
    ├── sell.py
    ├── supply.py
    ├── urls.py
    └── admin.py
