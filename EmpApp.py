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
    return render_template('index.html')


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
    emp_name = str("test add")
    print("The student data had added successfully")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/updateemp", methods=['POST'])
def updateEmp():
    #TODO: READ THE DATA FROM HTML

    cursor = db_conn.cursor()
    update_sql = "UPDATE student SET student_name = %s, student_email = %s, student_cohort = %s, student_programme = %s WHERE student_id = %s"
    #TODO: Replace the value with the above form 
    value = ("zdf","zdf@gmail.com","c","RSF",3) 
    
    try:
        cursor.execute(update_sql, value)
        db_conn.commit()
    except mariadb.Error as e:
        print(f"Error update student data: {e}")

    finally:
        cursor.close()

    emp_name = str("test update")
    print("The student data had update successfully")
    return render_template('AddEmpOutput.html',name=emp_name)

@app.route("/deleteemp", methods=['POST'])
def deleteEmp():
    #TODO: READ THE DATA FROM HTML
     
    cursor = db_conn.cursor()
    delete_sql = "DELETE FROM student WHERE student_id = %s"
    #TODO: Replace the value with the above form 
    value = (11,)

    try:
        cursor.execute(delete_sql,value)
        db_conn.commit()
    except mariadb.Error as e:
        print(f"Error delete student data: {e}")

    emp_name = str("test delete")
    print("The student data had delete successfully")
    return render_template('AddEmpOutput.html',name=emp_name)


#-----------------ROUTING-----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/job_listing')
def job_listing():
    return render_template('job_listing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/single_blog')
def single_blog():
    return render_template('single-blog.html')

@app.route('/elements')
def elements():
    return render_template('elements.html')

@app.route('/job_details')
def job_details():
    return render_template('job_details.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')




if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=80, debug=True) //Deployment
    app.run(debug=True)

    
