Flask Blog Website

Flask Blog Website is a web application built using Flask,a Python web framework.This project provides a platform for managing blog posts,integrating several key features:

CRUD Functionality: The website allows users to Create,Read,Update,and Delete blog posts,providing complete control over content management.

Database Integration: Flask-SQLAlchemy is employed to connect and interact with a MySQL database, ensuring secure and efficient data storage and retrieval.

User registration: Integrated user registration using the singup decorator to allow new user to singup.

User Authentication: Integrated user authentication using the login decorator to protect routes accessible only to authenticated user.

Slug for SEO: The website utilizes slugs for SEO optimization,ensuring clean and meaningful URLs for blog posts.

File Uploads: A file uploader is integrated,enabling users to upload files securely, also a function is implemented to check allowed Extension with size.

Contact Form: A contact form is provided,enabling visitors to send messages.The data from this form is stored in the database for reference.

JSON Configuration: A JSON configuration file (config.json) is used to manage various parameters and settings of the website.

Flash Messages: Flash messages are implemented to provide feedback on the status of operations,ensuring a user-friendly experience.

Routing and HTTP Methods: The project leverages Flask's routing mechanisms,including redirect,request,and url_for,and handles different HTTP methods (GET and POST) for distinct functionalities.

CSRF tokens: Used to prevent Cross-site request forgery

Password-hashing: Bcrypt is used for password hashing to prevent theft.Hashed passwords are stored in the database.

