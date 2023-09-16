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
    return render_template('register.html')


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

@app.route("/studentDetails", methods=['GET'])
def displayStudentData():
    # Query the database to retrieve student data
    cursor = db_conn.cursor()
    select_sql = "SELECT student_name, student_email FROM student WHERE student_id = ?"
    student_id = "21WMR02952" 

    try:
        cursor.execute(select_sql, (student_id,))
        student_data = cursor.fetchone()  # Assuming you want to display data for one student
    except mariadb.Error as e:
        print(f"Error fetching student data: {e}")
    finally:
        cursor.close()

    # Pass the data to the HTML template
    return render_template('studentDetails.html', student_name=student_data[0], student_email=student_data[1])


@app.route("/studentDetails", methods=['POST'])
def updateStudentData():
    if request.method == 'POST':
        # Retrieve form data
        student_id = "21WMR02952"
        Name = request.form.get('Name')
        Email = request.form.get('Email')

        # Perform the database update
        cursor = db_conn.cursor()
        update_sql = "UPDATE student SET student_name = %s, student_email = %s WHERE student_id = %s"
        values = (Name, Email, student_id)
        try:
            cursor.execute(update_sql, values)
            db_conn.commit()
        except mariadb.Error as e:
            print(f"Error updating student data: {e}")
            db_conn.rollback()
        finally:
            cursor.close()

        return redirect(url_for('studentDetails', student_id=student_id))


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

@app.route('/studentInternship')
def studentInternship():
    return render_template('studentInternship.html')

@app.route('/studentUpload')
def studentUpload():
    return render_template('studentUpload.html')

@app.route('/studentApplication')
def studentApplication():
    return render_template('studentApplication.html')

@app.route('/studentDetails')
def studentDetails():
    return render_template('studentDetails.html')

@app.route('/studentResults')
def studentResults():
    return render_template('studentResults.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')




if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=80, debug=True) //Deployment
    app.run(debug=True)

    
