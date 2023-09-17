from flask import Flask, render_template, request,url_for,redirect, request, make_response
from datetime import datetime
from flask import flash
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

from pymysql import connections

# from pymysql import connections
import os
import boto3
from config import *
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a3c2b5f01d686ffe7ca287ff4e8d9f2d'
bucket = custombucket
region = customregion

# Connect to Maria DB
try:
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    print("Success connect the MariaDB Platform/")
except Exception as e:
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
        
    except Exception as e:
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
    except Exception as e:
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
    except Exception as e:
        print(f"Error delete student data: {e}")

    emp_name = str("test delete")
    print("The student data had delete successfully")
    return render_template('AddEmpOutput.html',name=emp_name)


#----------------Student CRUD----------------

@app.route("/studentDetails", methods=['GET'])
def displayStudentData():
    # Query the database to retrieve student data
    cursor = db_conn.cursor()
    select_sql = "SELECT student_name, student_email FROM student WHERE student_id = %s"
    student_id = "21WMR02952" 

    try:
        cursor.execute(select_sql, (student_id,))
        student_data = cursor.fetchone()  # Assuming you want to display data for one student
    except Exception as e:
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
        except Exception as e:
            print(f"Error updating student data: {e}")
            db_conn.rollback()
        finally:
            cursor.close()

        return redirect(url_for('studentDetails', student_id=student_id))

app.config['UPLOAD_FOLDER'] = "C:\\Users\\User\\Desktop"


@app.route('/studentUpload', methods=['POST'])
def upload_document():
    try:
        # Retrieve form data
        student_id = "21WMR02952"

        # Retrieve the uploaded file
        uploaded_file = request.files['document_file']
        file_extension = os.path.splitext(uploaded_file.filename)[1]
        student_file_name_in_s3 = "student_Test" + file_extension
        # print("FILE=" ,str(uploaded_file.filename))

        #SQL
        cursor = db_conn.cursor()
        
        #Make connection with S3
        s3 = boto3.resource('s3',region_name=customregion)
        print("uploading files to S3...")

        try:
            # Upload the file to S3
            s3.Bucket(custombucket).put_object(Key=student_file_name_in_s3, Body=uploaded_file)

            # Generate the object URL
            object_url = "https://{0}.s3.amazonaws.com/{1}".format(custombucket,student_file_name_in_s3)
            print("object url:", str(object_url))

            #Insert url to mariadb
            try:
                update_sql = "UPDATE student SET acceptance_letter = %s WHERE student_id = %s"
                value = (str(object_url),student_id)
                # value = ("TESSTTTTTT",student_id)
                cursor.execute(update_sql,value)
                db_conn.commit()
                print("Success insert data to mariadb")
            except Exception as e:
                print(f"Error update student Image: {e}")
            finally: 
                cursor.close()
                
            return "File uploaded successfully."
        except Exception as e:
            print("Error during file upload: ", str(e))
            return str(e)
        
    except Exception as e:
        print("Error occurred: ", str(e))
        return str(e)
    

@app.route('/studentResults', methods=['GET'])
def display_results():
    cursor = db_conn.cursor()
    # Fetch data from your database or any other source
    student_id = "21WMR02952"
    select_sql = "SELECT internship_results, internship_comments,  student_name, student_email,student_cohort, student_programme, internship_position, internship_duration FROM student WHERE student_id = %s"
    try:
        cursor.execute(select_sql, (student_id,))
        student_data = cursor.fetchone()  # Assuming you want to display data for one student
    except Exception as e:
        print(f"Error fetching student data: {e}")
    finally:
        cursor.close()

    # Pass the data to the HTML template
    return render_template('studentResults.html',  result_title =student_data[0], result_description =student_data[1], student_name = student_data[2],  student_email  = student_data[3], student_cohort  = student_data[4], student_programme  = student_data[5], internship_position  = student_data[6], internship_duration  = student_data[7])

@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    # Create a PDF buffer
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file"
    p = canvas.Canvas(buffer, pagesize=letter)

    # Your code to add content to the PDF goes here
    # You can use p.drawString(), p.drawImage(), etc. to add text and images

    # Save the PDF to the buffer
    p.save()

    # Move the buffer position to the beginning
    buffer.seek(0)

    # Create a response to send the PDF
    response = make_response(buffer.read())
    response.mimetype = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=student_results.pdf'

    return response
    
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

    except Exception as e:
        print(f"Error fetching job postings: {e}")
        return "An error occurred while fetching job postings."

#Get company job listing details by job listing id
@app.route('/company/<int:job_id>')
def company_job_listing_details(job_id):
    try:
        cursor = db_conn.cursor()
        
        # Create a SQL query to retrieve job listing details by job_id
        query = "SELECT * FROM job_listings WHERE listing_id = %s"
        cursor.execute(query, (job_id,))
        job_data = cursor.fetchone()

        if job_data:
            company_id = job_data[9]
            
            # Fetch company data using company_id
            query = "SELECT * FROM company WHERE company_id = %s"
            cursor.execute(query, (company_id,))
            company_data = cursor.fetchone()

            cursor.close()

            if company_data:
                return render_template('companyJobDetails.html', companyData=company_data, jobData=job_data)
            else:
                return "Company not found."
        else:
            return "Job listing not found."
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return "An error occurred while fetching data."

@app.route('/company/create', methods=['GET', 'POST'])
def handle_create_job_listing():
    if request.method == 'GET':
        try:
            cursor = db_conn.cursor()

            # Fetch company details from the database
            query = "SELECT * FROM company WHERE company_id = 1"
            cursor.execute(query)
            company_details = cursor.fetchone()
            cursor.close()

            # Check if all company details are filled
            details_filled = all(company_details)

            return render_template('companyJobListingForm.html', details_filled=details_filled)

        except Exception as e:
            print(f"Error fetching company details: {e}")
            return "An error occurred while fetching company details."

    elif request.method == 'POST':
        # This section handles the submission of the job listing form

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
            db_conn.commit()
            cursor.close()

            flash('Job listing successfully created!', 'success')  # Flash a success message
            return redirect(url_for('handle_create_job_listing'))

        except Exception as e:
            print(f"Error inserting job listing: {e}")
            flash('An error occurred while creating the job listing. Please try again.', 'error')
            return redirect(url_for('handle_create_job_listing'))

        
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
            SET position=%s, min_salary=%s, max_salary=%s, working_hours=%s, requirements=%s, responsibilities=%s, descriptions=%s
            WHERE listing_id = %s
            """
            cursor.execute(query, (position, min_salary, max_salary, working_hours, job_requirements, job_responsibilities, additional_description, job_id))
            db_conn.commit()
            cursor.close()
            
            flash('Job listing successfully updated!', 'success')  # Flash a success message
            return redirect(url_for('handle_edit_job_listing', job_id=job_id))
        
        except Exception as e:
            print(f"Error inserting job listing: {e}")
            flash('An error occurred while creating the job listing. Please try again.', 'error')
            return redirect(url_for('handle_edit_job_listing', job_id=job_id))

    else:  # This is for the GET method
        try:
            cursor = db_conn.cursor()

            # Fetch job details from the database
            query = "SELECT listing_id, position, min_salary, max_salary, working_hours, requirements, responsibilities, descriptions FROM job_listings WHERE listing_id = %s"
            cursor.execute(query, (job_id,))
            job = cursor.fetchone()
            cursor.close()

            return render_template('companyJobListingForm.html', job=job)

        except Exception as e:
            print(f"Error fetching position details: {e}")
            return "An error occurred while fetching position details."

#Handle delete job listing
@app.route('/company/delete_job/<int:job_id>', methods=['GET'])
def handle_delete_job_listing(job_id):
    try:
        cursor = db_conn.cursor()

        # Delete the job listing from the database
        query = "DELETE FROM job_listings WHERE listing_id = %s"
        cursor.execute(query, (job_id,))
        db_conn.commit()

        cursor.close()

        flash('Job listing successfully deleted!', 'success')  # Flash a success message
        return redirect(url_for('company'))  # Redirect to your job listing page

    except Exception as e:
        print(f"Error deleting job listing: {e}")
        flash('An error occurred while deleting the job listing. Please try again.', 'error')
        return redirect(url_for('company'))  # Redirect to your job listing page



#Render company profile page or handle company profile form submission
# @app.route('/companyProfile/<int:company_id>', methods=['POST', 'GET'])
@app.route('/companyProfile', methods=['POST', 'GET'])
def handle_company_profile():

    company_id = 1  # This is just a placeholder for now. We will change this later.

    if request.method == 'POST':
        # Handle the form submission
        
        # Extract data from the form
        company_name = request.form['company_name']
        company_street_address = request.form['company_street_address']
        company_city = request.form['company_city']
        company_postcode = request.form['company_postcode']
        company_state = request.form['company_state']
        contact_name = request.form['contact_name']
        contact_email = request.form['contact_email']
        company_website = request.form['company_website']
        industry = request.form['industry']
        company_type = request.form['company_type']
        description = request.form['description']



        # Update the database with the new data
        try:
            cursor = db_conn.cursor()
            
            query = """
            UPDATE company
            SET company_name=%s, street_address=%s, city=%s, postcode=%s, state=%s, contact_name=%s, contact_email=%s, company_website=%s, industry=%s, company_type=%s, description=%s
            WHERE company_id = %s
            """
            cursor.execute(query, (company_name, company_street_address, company_city, company_postcode, company_state, contact_name, contact_email, company_website, industry, company_type, description, company_id))
            db_conn.commit()
            cursor.close()
            
            flash('Company profile successfully updated!', 'success')  # Flash a success message
            return redirect(url_for('handle_company_profile'))
        
        except Exception as e:
            print(f"Error updating company profile: {e}")
            flash('An error occurred while updating the company profile. Please try again.', 'error')
            return redirect(url_for('handle_company_profile'))
    else:
        try:
            cursor = db_conn.cursor()

            # Fetch company details from the database
            query = "SELECT * FROM company WHERE company_id = %s"
            cursor.execute(query, (company_id,))
            company_details = cursor.fetchone()
            cursor.close()

            return render_template('companyProfile.html', company=company_details)

        except Exception as e:
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_messages = {}  # Dictionary to store error message

    if request.method == 'GET':
        # Render the registration page
        return render_template('register.html')
    
    if request.method == 'POST':
        role = request.form.get('role')

        print(f"Role: {role}")

        print(f"Form data: {request.form}")

        try:
            cursor = db_conn.cursor()

            if role == "student":
                # Fetch Student data
                educationLevel = request.form.get('educationLevel')
                cohort = request.form.get('cohort')
                programme = request.form.get('programme')
                tutorialGroup = request.form.get('tutorialGroup')
                studentID = request.form.get('studentID')
                studentEmail = request.form.get('studentEmail')
                supervisorName = request.form.get('supervisorName')
                supervisorEmail = request.form.get('supervisorEmail')
                programmingKnowledge = request.form.get('programmingKnowledge')
                databaseKnowledge = request.form.get('databaseKnowledge')
                networkingKnowledge = request.form.get('networkingKnowledge')
                studentPassword = request.form.get('studentPassword')
                studentConfirmedPassword = request.form.get('studentConfirmedPassword')

                supervisor_id = 1  # This is just a placeholder for now. We will change this later.

                user_id = 1  # This is just a placeholder for now. We will change this later.

                #Check if all fields are filled
                if not all([educationLevel, cohort, programme, tutorialGroup, studentID, studentEmail, supervisorName, supervisorEmail, programmingKnowledge, databaseKnowledge, networkingKnowledge, studentPassword, studentConfirmedPassword]):
                    error_messages['all_fields'] = 'Error! Please fill in all fields.'

                # Check if password and confirmed password match
                if studentPassword != studentConfirmedPassword:
                    error_messages['studentPassword'] = 'Password and confirmed password do not match.'

                # Check for other validation rules and add error messages as needed

                if error_messages:
                    return render_template('register.html', error_messages=error_messages, form_data=request.form)

                
                # Insert into student table
                query = """INSERT INTO student 
                        (student_name, student_email, student_cohort, student_programme, student_level, student_tutgrp, student_pk, student_dk, student_nk, supervisor_id, student_password,user_id) 
                        VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, SHA2(%s, 256), %s)"""
                cursor.execute(query, (studentID, studentEmail, cohort, programme, educationLevel, tutorialGroup, programmingKnowledge, databaseKnowledge, networkingKnowledge, supervisor_id, studentPassword, user_id))
                db_conn.commit()

            elif role == "company":
                # Fetch Company data
                companyName = request.form.get('companyName')
                industry = request.form.get('industry')
                contactName = request.form.get('contactName')
                contactEmail = request.form.get('contactEmail')
                userEmail = request.form.get('userEmail')
                userPassword = request.form.get('userPassword')
                companyConfirmedPassword = request.form.get('companyConfirmedPassword')

                user_id = 1  # This is just a placeholder for now. We will change this later.
                
                #Check if all fields are filled
                if not all([companyName, industry, contactName, contactEmail, userEmail, userPassword, companyConfirmedPassword]):
                    error_messages['all_fields'] = 'Error! Please fill in all fields.'

                # Check if password and confirmed password match
                if userPassword != companyConfirmedPassword:
                    error_messages['companyPassword'] = 'Password and confirmed password do not match.'

                # Check for other validation rules and add error messages as needed

                if error_messages:
                    return render_template('register.html', error_messages=error_messages, form_data=request.form)
                
                # Insert into company table
                query = """INSERT INTO company 
                        (company_name, industry, contact_name, contact_email, user_id) 
                        VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(query, (companyName, industry, contactName, contactEmail, user_id))
                db_conn.commit()

            cursor.close()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))  # Redirect to the login page

        except Exception as e:
            print(f"Error during registration: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('register'))  # Redirect to the registration page





if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=80, debug=True) //Deployment
    app.run(debug=True)

    
