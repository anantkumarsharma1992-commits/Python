SUPER30 FASTAPI - GET API TASK
================================

PROJECT OBJECTIVE
------------------
Build a FastAPI application with multiple GET endpoints, covering static
routes, dynamic path parameters, type hints, and JSON responses.


INSTALLATION STEPS
-------------------
1. Clone this repository

     git clone: https://github.com/anantkumarsharma1992-commits/Python/upload/main/super30-fastapi-get-api-task
     cd super30-fastapi-get-api-task

2. (Optional but recommended) Create and activate a virtual environment

     python -m venv venv
     venv\Scripts\activate      (Windows)
     source venv/bin/activate   (macOS/Linux)

3. Install dependencies

     pip install -r requirements.txt


HOW TO RUN THE SERVER
-----------------------
     uvicorn main:app --reload

The API will be available at:
     http://127.0.0.1:8000


AVAILABLE API ENDPOINTS
-------------------------
METHOD   ENDPOINT                        DESCRIPTION
GET      /                               Welcome message
GET      /student                        Student information
GET      /course                         Course details
GET      /skills                         List of technical skills
GET      /add/{num1}/{num2}              Adds two numbers
GET      /multiply/{num1}/{num2}         Multiplies two numbers
GET      /square/{number}                Returns the square of a number
GET      /check/{number}                 Returns whether a number is even or odd
GET      /age/{age}                      Returns an age-based message
GET      /table/{number}                 Returns the multiplication table
GET      /profile/{name}/{age}           Returns a simple profile
GET      /number/{number}                Returns square, cube, and even/odd status


EXAMPLE URLS
-------------
http://127.0.0.1:8000/add/10/20
http://127.0.0.1:8000/multiply/5/8
http://127.0.0.1:8000/table/7
http://127.0.0.1:8000/profile/Anant/37
http://127.0.0.1:8000/number/10


DOCUMENTATION
--------------
Swagger UI:  http://127.0.0.1:8000/docs
ReDoc:       http://127.0.0.1:8000/redoc


AUTHOR / STUDENT NAME
-----------------------
Anant Sharma - Super30



