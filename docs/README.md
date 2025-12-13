# Multi Domain Intelligence Platform
Student Name: Ariyanna Valentine Mendonca 
Student ID: M01091141
Course: Cybersecurity and Digital Forensics CST1510 Coursework 2

## Project Description 

A command-line authentication system implementing secure password hashing. 
This system allows users to register accounts and log in with proper passwords.
Streamlit shows dashboards containing databases with CRUD functions, graphs and a chatbot

## Features 

- Secure password hashing using bcrypt with automatic salt generation 
- User registration with duplicate username prevention 
- User login with password verification 
- Input validation for usernames and passwords 
- File-based user data persistence

## Technical Implementation 
- Hashing Algorithm: bcrypt with automatic salting 
- Data Storage: Plain text file ('users.txt') with comma-separated values
- Password security : One-way hashing, no plaintext storage 
- Validation: Username (3-20 alphanumeric characters), Password(6-50 characters)