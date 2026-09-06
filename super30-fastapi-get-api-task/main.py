from fastapi import FastAPI

app= FastAPI()

@app.get("/")

def homeapi():
    return {"message": "Welcome to Super30 FastAPI"}

@app.get("/student")

def student():
    return {"name": "Anant","batch": "Super30","role": "Student"}

@app.get("/course")

def course():
    return {
        "course_name": "Backend Development with FastAPI",
        "mentor": "Sudhanshu",
        "duration": "8 Weeks",
        "topics": ["Python","FastAPI","REST API","Database","Deployment"]
    }

@app.get("/skills")
def skills():
    return{

        "skills": ["Python","FastAPI","SQL","Docker","AWS"]
    }

@app.get("/add/{a}/{b}")

def add(a: int,b:int):
    return {"a":a,
            "b":b,
            "result": a+b
            }

@app.get("/multiply/{a}/{b}")

def multiplication(a: int,b:int):
    return {"a":a,
            "b":b,
            "result": a*b
            }

@app.get("/square/{a}")

def Square(a: int):
    return {"a":a,
            "result": a**2
            }

@app.get("/even_odd/{a}")

def even_odd(a:int):
    if a%2==0:
        message="Even Number"
    else:
        message="Odd Number"
    return{"a":a,
           "message": message
           }

@app.get("/age/{age}")

def age_check(age: int):
    if age < 0:
        message = "Invalid age"
    elif age<13:
        message = "Child"
    elif age<20:
        message = "Teenager"
    elif age<60:
        message = "Adult"
    else:   
        message = "Senior Citizen"

    return{"age": age, "message": message}


@app.get("/table/{a}")

def table(a:int):
    table_list=[]
    for i in range(1,11):
        table_list.append(f"{a} X{i}= {a*i}")
    return {"table":table_list}


@app.get("/profile/{name}/{age}")

def profile(name: str, age: int):
    return {"name": name,
            "age":age}

@app.get("/number/{num1}")

def number(num1: int):
    return{
        "number": num1,
        "sqaure": num1**2,
        "cube": num1**3,
        "even": num1%2==0
    }