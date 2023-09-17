from flask import Flask, render_template, request,url_for,redirect
from datetime import datetime
from flask import flash


# from pymysql import connections
import os
import boto3
from config import *
import mariadb
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a3c2b5f01d686ffe7ca287ff4e8d9f2d'
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


#----------------Student CRUD----------------

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

app.config['UPLOAD_FOLDER'] = "C:\\Users\\User\\Desktop"

@app.route('/studentUpload', methods=['POST'])
def upload_document():
    uploaded_file = request.files['document_file']

    if uploaded_file.filename != '':
        # Save the uploaded file to a designated folder
        return 'File uploaded successfully.'
    else:
        return 'No file selected.'
    
#----------------Company CRUD----------------

#Render company job listing page and display job postings
@app.route('/company')
def company():
    try:
        cursor = db_conn.cursor()
        # Fetch job postings from the database
        query = "SELECT listing_id, position, min_salary, max_salary, working_hours FROM job_listings"
        cursor.execute(query)
        job_postings = cursor.fetchall()
        cursor.close()

        return render_template('company.html', job_postings=job_postings)

    except mariadb.Error as e:
        print(f"Error fetching job postings: {e}")
        return "An error occurred while fetching job postings."

#Get company job listing details by job listing id
@app.route('/company/<int:job_id>')
def company_job_listing_details(job_id):
    try:
        cursor = db_conn.cursor()
        
        # Create a SQL query to retrieve job listing details by job_id
        query = "SELECT * FROM job_listings WHERE listing_id = ?"
        cursor.execute(query, (job_id,))
        job_data = cursor.fetchone()

        if job_data:
            company_id = job_data[9]
            
            # Fetch company data using company_id
            query = "SELECT * FROM company WHERE company_id = ?"
            cursor.execute(query, (company_id,))
            company_data = cursor.fetchone()

            cursor.close()

            if company_data:
                return render_template('companyJobDetails.html', companyData=company_data, jobData=job_data)
            else:
                return "Company not found."
        else:
            return "Job listing not found."
    
    except mariadb.Error as e:
        print(f"Error fetching data: {e}")
        return "An error occurred while fetching data."

#Render company create job listing page
@app.route('/company/create', methods=['GET'])
def render_company_create_job_listing():
    try:
        cursor = db_conn.cursor()

        # Fetch company details from the database
        query = "SELECT company_name, company_address, contact_name, contact_email, company_website, industry, company_type, description FROM company WHERE company_id = 1"
        cursor.execute(query)
        company_details = cursor.fetchone()
        cursor.close()

        # Check if all company details are filled
        details_filled = all(company_details)

        return render_template('companyJobListingForm.html', details_filled=details_filled)

    except mariadb.Error as e:
        print(f"Error fetching company details: {e}")
        return "An error occurred while fetching company details."
    
#Create company job listing
@app.route('/company/create', methods=['POST'])
def company_submit_job_listing():
    if request.method == 'POST':

        # get data from form
        position = request.form['position']
        min_salary = request.form['min_salary']
        max_salary = request.form['max_salary']
        working_hours = request.form['working_hours']
        job_requirements = request.form['job_requirements']
        job_responsibilities = request.form['job_responsibilities']
        additional_description = request.form['additional_description']

        posted_date = datetime.now().strftime('%Y-%m-%d')
        
        # insert data into database
        try:
            cursor = db_conn.cursor()
            query = """INSERT INTO job_listings(position, min_salary, max_salary, working_hours, requirements, responsibilities, descriptions, postedDate, company_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (position, min_salary, max_salary, working_hours, job_requirements, job_responsibilities, additional_description, posted_date, 1))
            db_conn.commit()  # Don't forget to commit to save changes to the database
            cursor.close()

            flash('Job listing successfully created!', 'success')  # Flash a success message
            return redirect(url_for('company_submit_job_listing'))

        except mariadb.Error as e:
            print(f"Error inserting job listing: {e}")
            flash('An error occurred while creating the job listing. Please try again.', 'error')
            return redirect(url_for('company_submit_job_listing'))
        
#Render company edit job listing page or handle edit job listing form submission
@app.route('/company/edit_job/<int:job_id>', methods=['GET', 'POST'])
def handle_edit_job_listing(job_id):
    if request.method == 'POST':
        # Handle the form submission
        
        # Extract data from the form
        position = request.form['position']
        min_salary = request.form['min_salary']
        max_salary = request.form['max_salary']
        working_hours = request.form['working_hours']
        job_requirements = request.form['job_requirements']
        job_responsibilities = request.form['job_responsibilities']
        additional_description = request.form['additional_description']
        
        # Update the database with the new data
        try:
            cursor = db_conn.cursor()
            
            query = """
            UPDATE job_listings
            SET position=?, min_salary=?, max_salary=?, working_hours=?, requirements=?, responsibilities=?, descriptions=?
            WHERE listing_id = ?
            """
            
            cursor.execute(query, (position, min_salary, max_salary, working_hours, job_requirements, job_responsibilities, additional_description, job_id))
            db_conn.commit()
            cursor.close()
            
            flash('Job listing successfully updated!', 'success')  # Flash a success message
            return redirect(url_for('handle_edit_job_listing', job_id=job_id))
        
        except mariadb.Error as e:
            print(f"Error inserting job listing: {e}")
            flash('An error occurred while creating the job listing. Please try again.', 'error')
            return redirect(url_for('handle_edit_job_listing', job_id=job_id))

    else:  # This is for the GET method
        try:
            cursor = db_conn.cursor()

            # Fetch job details from the database
            query = "SELECT listing_id, position, min_salary, max_salary, working_hours, requirements, responsibilities, descriptions FROM job_listings WHERE listing_id = ?"
            cursor.execute(query, (job_id,))
            job = cursor.fetchone()
            cursor.close()

            return render_template('companyJobListingForm.html', job=job)

        except mariadb.Error as e:
            print(f"Error fetching position details: {e}")
            return "An error occurred while fetching position details."

#Handle delete job listing
@app.route('/company/delete_job/<int:job_id>', methods=['GET'])
def handle_delete_job_listing(job_id):
    try:
        cursor = db_conn.cursor()

        # Delete the job listing from the database
        query = "DELETE FROM job_listings WHERE listing_id = ?"
        cursor.execute(query, (job_id,))
        db_conn.commit()

        cursor.close()

        flash('Job listing successfully deleted!', 'success')  # Flash a success message
        return redirect(url_for('company'))  # Redirect to your job listing page

    except mariadb.Error as e:
        print(f"Error deleting job listing: {e}")
        flash('An error occurred while deleting the job listing. Please try again.', 'error')
        return redirect(url_for('company'))  # Redirect to your job listing page



#Render company profile page
@app.route('/companyProfile')
def companyProfile():
    try:
        cursor = db_conn.cursor()

        # Fetch company details from the database
        query = "SELECT company_name, company_address, contact_name, contact_email, company_website, industry, company_type, description FROM company WHERE company_id = 1"
        cursor.execute(query)
        company_details = cursor.fetchone()
        cursor.close()

        return render_template('companyProfile.html', company=company_details)

    except mariadb.Error as e:
        print(f"Error fetching company details: {e}")
        return "An error occurred while fetching company details."



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

    
