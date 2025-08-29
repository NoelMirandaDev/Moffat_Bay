<p align="center">
  <img src="https://content.presspage.com/uploads/2543/1920_purple-seal-unstoppable-bkg-1800x1200.png?10000" alt="Purple Seal Unstoppable" width="400"/>
</p>

# Moffat Bay Lodge Reservation System
*CSD460-A311 Capstone in Software Development*  
<sub>Bellevue University 9-week project-based course</sub>
---

## Introduction
Welcome to the Moffat Bay Lodge Reservation System, a full-stack Python web application designed for the fictional Joviedsa Island Resort in Washington State’s San Juan Islands. This project simulates a real-world development scenario where our team was tasked with creating a secure, user-friendly, and visually appealing website for a newly built resort and marina.

The application allows visitors to explore the lodge, learn about island attractions, and make reservations through a streamlined booking process. Customers can browse all public pages without logging in, but must register for a free account to confirm a booking. The system securely stores user credentials and reservation details in a MySQL database, applying modern best practices for password validation and encryption.

## Key Features
- **Landing Page** – Modern marketing design to welcome guests.
- **About Us, Contact Us & Attractions** – Static HTML/CSS pages highlighting the lodge and island activities.
- **User Registration & Login** – Email-based authentication, password rules, and secure storage using hashing.
- **Vacation Booking** – Select room size, guest count, and check-in/check-out dates.
- **Reservation Summary & Confirmation** – Review and confirm bookings, with cancellation and submission options.
- **Reservation Lookup** – Search previous reservations by ID or email.

---

## Getting Started (set up for local development)  

Follow the steps below to set up and run the project locally.

### Prerequisites
- Python 3.10 or newer
- Git
- MySQL

### 1. Clone the Repository  
``git clone https://github.com/<your-username>/Moffat_Bay.git``  

``cd Moffat_Bay``

### 2. Create a Virtual Environment (keeps project dependencies separate from your global Python installation)  
``python3 -m venv venv``  

or 

``python -m venv venv`` (older python versions & windows)

Note: This step only needs to be done once. The virtual environment folder venv will store all Python packages locally for this project.

### 3. Activate the Virtual Environment (After activation, all Python commands and installed packages are isolated to this project.)  
- Mac/Linux: ``source venv/bin/activate``
- Windows: ``venv\Scripts\activate``

### 4.a Install Dependencies (This installs Flask and any other required packages.)  
``pip install -r requirements.txt``  

Note: This step only needs to be done once. Dependencies only need to be installed once per virtual environment.

### 4.b Create .env file (This file is for your MySQL database credentials)  

- ``cp .env.example .env``
- Change placeholders to your MySQL credentials

Note: This step only needs to be done once. Do not worry of credentials being uploaded to GitHub, it is accounted for in the .gitignore file.

### 5. Run the Flask Application (Make sure your virtual environment is activated before attempting to run)  
``cd src``  

``python3 app.py``

### 6. Stop the Server
**Press CTRL + C in the terminal.**

### 7. Deactivate the Virtual Environment
``deactivate``  

Note: This turns off the virtual environment and returns you to your system Python. The installed packages remain in the venv folder and do not need to be reinstalled.

---

## Database Setup (MySQL)

To **set up the schema locally**, follow these steps:

1. Make sure MySQL is installed and running on your machine.  

2. From the project root directory (`Moffat_Bay`), run the following command in your terminal (NOTE this will DROP the old moffat_bay database if it exists.):  
``mysql -u root -p < db/schema.sql``  

To **populate the database**, follow these steps (**Not yet included in this repo, WIP**):

1. From the project root directory (`Moffat_Bay`), run the following command in your terminal:
``mysql -u root -p moffat_bay < db/data.sql``


---

## Contributors
| Role              | Name           |
|-------------------|----------------|
| **Team Leader/Developer** | Noel Miranda  |
| **Developer**     | Kyle Marlia-Conner |
| **Developer**     | Steve Stylin |
| **Developer**     | Riese Bohnak |
| **Developer**     | Amit Rizal |

## Professor
| Role       | Name            |
|------------|-----------------|
| **Stakeholder** | Adam Bailey |

---
