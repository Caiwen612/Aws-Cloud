from flask import Flask, render_template, request,url_for,redirect
# from pymysql import connections
import os
import boto3
from config import *
import mariadb
import sys

app = Flask(__name__)

bucket = custombucket
region = customregion

# Connect to Maria DB
try:
    db_conn = mariadb.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    print("Success connect the MariaDB Platform/")
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Disable Auto-Commit because mariadb default is auto commit
db_conn.autocommit = False


# output = {}
# table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.tarc.edu.my')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    #TODO: READ THE DATA FROM HTML, the 'emp_id' is refer to the name of the form
    # emp_id = request.form['emp_id']
    # first_name = request.form['first_name']
    # last_name = request.form['last_name']
    # pri_skill = request.form['pri_skill']
    # location = request.form['location']
    # emp_image_file = request.files['emp_image_file']
   
    cursor = db_conn.cursor()
    insert_sql = "INSERT INTO student (student_id,student_name,student_email,student_cohort,student_programme) VALUES (?,?,?,?,?)"
    #TODO: Replace the value with the above form 
    value = (None,"caiwen","cw@gmail.com","c","RSF") #Insert none is because it will auto generate

    try:
        cursor.execute(insert_sql, value)
        db_conn.commit()
        
    except mariadb.Error as e:
        print(f"Error insert student data: {e}")

    finally:
        cursor.close()

    #TODO: Pass back data to the html
    emp_name = str("test")
    print("The student data had added successfully")
    return render_template('AddEmpOutput.html', name=emp_name)




if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=80, debug=True) //Deployment
    app.run(debug=True)

