# Week 7: Secure Authetication System 
Student Name: Ariyanna Valentine Mendonca 
Student ID: M01091141
Course: CST1510 -CW2 - Multi-Domain Intelligence Platform 

## Project Description 

A command-line authentication system implementing secure password hashing. 
This system allows users to register accounts and log in with proper passwords.

## Features 

- Secure password hashing using bcrypt with automatic salt generation 
- User registration with duplicate username prevention 
- User login with password verification 
- Input validation for usernames and passwords 
- File-based user data persistence

## Technical Implementation 
- Hashing Algorithm: bcrypt with automatic salting 
- Data Storage: Plain text file ('users.txt') with comma-seperated values
- Password security : One-way hashing, no plaintext storage 
- Validation: Username (3-20 alphanumeric characters), Password(6-50 characters)