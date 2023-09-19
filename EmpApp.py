from flask import Flask, render_template, request,url_for,redirect, request, make_response
from datetime import datetime
from flask import flash
from flask import session
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import subprocess
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
# Add a WebHook
WEBHOOK_SECRET = 'WebHockServiceSecret'
GITHUB_REPO_PATH = '/home/ec2-user/Aws-Cloud'

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

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        subprocess.call(['sudo','git', 'pull'], cwd=GITHUB_REPO_PATH)
        subprocess.call(['sudo', 'systemctl', 'restart', 'myflaskapp'])
        print("Trying to fetch and pull new request from webhooks")
        # # Verify GitHub's request
        # payload = request.data
        # signature = 'sha1=' + hmac.new(WEBHOOK_SECRET.encode(), payload, digestmod='sha1').hexdigest()
        
        # if request.headers.get('X-Hub-Signature') != signature:
        #     abort(400)  # Request is not from GitHub. Abort!
        # If request is authenticated, pull latest changes and restart Flask
        #Sudo test 
    except Exception as e:
        # Log the exception
        app.logger.error('An exception occurred: %s', str(e))
        traceback.print_exc()
        abort(500)  # Return a 500 Internal Server Error
    
    return 'OK', 200

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('register_student.html')


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
    user_id = session.get('user_id')
    select_sql = "SELECT student_name, student_email FROM student WHERE student_id = %s"
    try:
        cursor.execute(select_sql, ( user_id,))
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
        user_id = session.get('user_id')
        Name = request.form.get('Name')
        Email = request.form.get('Email')

        # Perform the database update
        cursor = db_conn.cursor()
        update_sql = "UPDATE student SET student_name = %s, student_email = %s WHERE student_id = %s"
        values = (Name, Email,  user_id)
        try:
            cursor.execute(update_sql, values)
            db_conn.commit()
        except Exception as e:
            print(f"Error updating student data: {e}")
            db_conn.rollback()
        finally:
            cursor.close()

        return redirect(url_for('studentDetails', student_id=user_id ))

app.config['UPLOAD_FOLDER'] = "C:\\Users\\User\\Desktop"
@app.route('/studentUpload', methods=['POST'])
def upload_document():
    try:
        # Retrieve form data
        user_id = session.get('user_id')

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
                value = (str(object_url),user_id )
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
    user_id = session.get('user_id')
    select_sql = "SELECT internship_results, internship_comments,  student_name, student_email,student_cohort, student_programme, internship_position, internship_duration FROM student WHERE student_id = %s"
    try:
        cursor.execute(select_sql, (user_id, ))
        student_data = cursor.fetchone()  # Assuming you want to display data for one student
    except Exception as e:
        print(f"Error fetching student data: {e}")
    finally:
        cursor.close()

    # Pass the data to the HTML template
    return render_template('studentResults.html',  result_title =student_data[0], result_description =student_data[1], student_name = student_data[2],  student_email  = student_data[3], student_cohort  = student_data[4], student_programme  = student_data[5], internship_position  = student_data[6], internship_duration  = student_data[7])

@app.route('/generate_pdf', methods=['GET'])
def generate_pdf():
 # Fetch student data from the database
    user_id = session.get('user_id')
    cursor = db_conn.cursor()
    select_sql =  "SELECT internship_results, internship_comments,  student_name, student_email,student_cohort, student_programme, internship_position, internship_duration FROM student WHERE student_id = %s"
    
    try:
        cursor.execute(select_sql, (  user_id,))
        student_data = cursor.fetchone()
    except Exception as e:
        print(f"Error fetching student data: {e}")
    finally:
        cursor.close()

    # # Fetch company data from the database (assuming you have a table for company details)
    # company_id = "XYZ123"
    # cursor = db_conn.cursor()
    # select_company_sql = "SELECT company_name, company_location FROM company WHERE company_id = %s"
    
    # try:
    #     cursor.execute(select_company_sql, (company_id,))
    #     company_data = cursor.fetchone()
    # except Exception as e:
    #     print(f"Error fetching company data: {e}")
    # finally:
    #     cursor.close()

    # Create a PDF buffer
    buffer = BytesIO()

    # Create the PDF object using the buffer
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Create a list of elements to add to the PDF
    elements = []

    # Define a title style using ReportLab's styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']

    # Add a title to the PDF
    elements.append(Paragraph("Student's Internship Results", title_style))

    # Create a table to display student and company data
    data = [
        ["Student Name", student_data[2]],
        ["Student Email", student_data[3]],
        ["Student Cohort", student_data[4]],
        ["Student Programme", student_data[5]],
        ["Internship Position", student_data[6]],
        ["Internship Duration", student_data[7]],
        ["Internship Results", student_data[0]],
        ["Supervisor's Comments", student_data[1]],
        # ["Company Name", company_data[0]],
        # ["Company Location", company_data[1]],
    ]

    # Define table styles
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), (0.92, 0.92, 0.92)),
        ('GRID', (0, 0), (-1, -1), 1, (0.7, 0.7, 0.7)),
    ])

    # Create the table and apply styles
    table = Table(data)
    table.setStyle(table_style)

    # Add the table to the PDF
    elements.append(table)

    # Build the PDF document
    doc.build(elements)

    # Move the buffer position to the beginning
    buffer.seek(0)

    # Create a response to send the PDF
    response = make_response(buffer.read())
    response.mimetype = 'application/pdf'
    filename = f"{student_data[2]}_Internship_Results.pdf"
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'

    return response


#Get company job listing details by job listing id
@app.route('/studentInternship/<int:listing_id>')
def intern_job_details(listing_id):
    try:
        cursor = db_conn.cursor()
        
        # Create a SQL query to retrieve job listing details by job_id
        query = "SELECT * FROM job_listings WHERE listing_id = %s"
        cursor.execute(query, (listing_id,))
        job_data = cursor.fetchone()

        if job_data:
            company_id = job_data[9]
            
            # Fetch company data using company_id
            query = "SELECT * FROM company WHERE company_id = %s"
            cursor.execute(query, (company_id,))
            company_data = cursor.fetchone()

            cursor.close()

            if company_data:
                return render_template('studentInternDetails.html', companyData=company_data, jobData=job_data)
            else:
                return "Company not found."
        else:
            return "Job listing not found."
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return "An error occurred while fetching data."

# Assuming you have a function to connect to the database called 'get_db_connection'
def get_unique_job_positions():
    cursor = db_conn.cursor()
    select_sql = "SELECT DISTINCT position FROM job_listings"
    cursor.execute(select_sql)
    job_positions = [row[0] for row in cursor.fetchall()]  # Extract the first column (position)
    cursor.close()
    return job_positions

@app.route('/studentInternship')
def show_all_jobs():
    try:
        cursor = db_conn.cursor()
        query = """
            SELECT job_listings.*, company.company_name AS company_name
            FROM job_listings
            JOIN company ON job_listings.company_id = company.company_id
        """
        cursor.execute(query)
        job_posting = cursor.fetchall()
        job_positions = get_unique_job_positions()
        cursor.close()

        return render_template('studentInternship.html', job_posting=job_posting, job_positions=job_positions)

    except Exception as e:
        print(f"Error fetching job postings: {e}")
        return "An error occurred while fetching job postings."


#----------------Company CRUD----------------

#Render company job listing page and display job postings
@app.route('/company')
def company():
    try:
        cursor = db_conn.cursor()

        user_id = session.get('user_id')

        # Fetch job postings from the database
        query = "SELECT listing_id, position, min_salary, max_salary, working_hours FROM job_listings WHERE company_id = %s"
        cursor.execute(query, (user_id,))
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

            user_id = session.get('user_id')

            # Fetch company details from the database
            query = "SELECT * FROM company WHERE company_id = %s"
            cursor.execute(query, (user_id,))
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
            cursor.execute(query, (position, min_salary, max_salary, working_hours, job_requirements, job_responsibilities, additional_description, posted_date, session.get('user_id')))
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

    company_id = session.get('user_id')

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

#---------------- Eugene ----------------
@app.route('/supervisorStudentDetails')
def supervisorStudentDetails():
    try:
        cursor = db_conn.cursor()

        user_id = session.get('user_id')

        # Fetch student list from the database with the supervisor id
        query = "SELECT * FROM student WHERE supervisor_id = %s"
        cursor.execute(query, (user_id,))
        student_list = cursor.fetchall()
        cursor.close()

        return render_template('supervisorStudentDetails.html', student_list=student_list)

    except Exception as e:
        print(f"Error fetching job postings: {e}")
        return "An error occurred while fetching student list."
    
@app.route('/supervisorStudentDetails/<student_id>')
def supervisorStudentDetails_student(student_id):
    try:
        cursor = db_conn.cursor()

        # Fetch student details from the database
        query = "SELECT * FROM student WHERE student_id = %s"
        cursor.execute(query, (student_id,))
        student_details = cursor.fetchone()
        cursor.close()

        return render_template('supervisorStudentDetails_student.html', studentDetails=student_details)

    except Exception as e:
        print(f"Error fetching student details: {e}")
        return "An error occurred while fetching student details."
    
@app.route('/supervisorStudentDetails/evaluate/<student_id>', methods=['GET', 'POST'])
def supervisorStudentDetails_student_evaluate(student_id):
    if request.method == 'POST':
        # Handle the form submission

        # Extract data from the form
        programming_knowledge = request.form['programming_knowledge']
        database_knowledge = request.form['database_knowledge']
        debugging_knowledge = request.form['debugging_knowledge']
        teamwork_skills = request.form['teamwork_skills']
        evaluation_date = request.form['evaluation_date']
        evaluation_comment = request.form['evaluation_comment']

        # You can now use these variables to update your database or perform any other actions as needed.
        # Update the database with the new data
        try:
            cursor = db_conn.cursor()
            
            query = """
            UPDATE student
            SET ev_pk=%s, ev_db=%s, ev_dek=%s, ev_tk=%s, ev_date=%s, ev_comment=%s
            WHERE student_id = %s
            """
            cursor.execute(query, (programming_knowledge, database_knowledge, debugging_knowledge, teamwork_skills, evaluation_date, evaluation_comment, student_id))
            db_conn.commit()
            cursor.close()
            
            flash('Evaluation submitted successfully!', 'success')  # Flash a success message
            return redirect(url_for('supervisorStudentDetails_student_evaluate', student_id=student_id))
        
        except Exception as e:
            print(f"Error inserting job listing: {e}")
            flash('An error occurred while submitting the evaluation. Please try again.', 'error')
            return redirect(url_for('supervisorStudentDetails_student_evaluate', student_id=student_id))

    else:  # This is for the GET method
        try:
            cursor = db_conn.cursor()

            # Fetch student details from the database
            query = "SELECT * FROM student WHERE student_id = %s"
            cursor.execute(query, (student_id,))
            student_details = cursor.fetchone()
            cursor.close()

            return render_template('supervisorEvaluationForm.html', studentDetails=student_details)

        except Exception as e:
            print(f"Error fetching student details: {e}")
            return "An error occurred while fetching student details."

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

@app.route('/login' , methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        try:
            cursor = db_conn.cursor()

            # Get the form data
            email = request.form.get('email')
            password = request.form.get('password')

            # Check if email exists
            query = "SELECT * FROM user WHERE email = %s"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()
            if not user_data:
                flash('Email does not exist.', 'error')
                return render_template('login.html', form_data=request.form)
            
            # Check if password is correct
            query = "SELECT * FROM user WHERE email = %s AND password = %s"
            cursor.execute(query, (email, password))
            user_data = cursor.fetchone()
            if not user_data:
                flash('Incorrect password.', 'error')
                return render_template('login.html', form_data=request.form)
            

            # Check if user is a student
            query = "SELECT * FROM user WHERE email = %s AND role = 'student'"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()
            if user_data:

                # Get the student_id
                query = "SELECT student_id FROM student WHERE student_email = %s"
                cursor.execute(query, (email,))
                student_id = cursor.fetchone()[0]

                # Store the student_id in the session
                session['user_id'] = student_id
                session['role'] = 'student' # Store the role in the session

                cursor.close()
                return redirect(url_for('studentDetails', student_id=student_id)) # Redirect to the student details page
            
            # Check if user is a company
            query = "SELECT * FROM user WHERE email = %s AND role = 'company'"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()
            if user_data:
                    
                    # Get the company_id
                    query = "SELECT company_id FROM company WHERE user_id = %s"
                    cursor.execute(query, (user_data[0],))
                    company_id = cursor.fetchone()[0]

                    # Store the company_id in the session
                    session['user_id'] = company_id
                    session['role'] = 'company' # Store the role in the session
    
                    cursor.close()
                    return redirect(url_for('company', company_id=company_id)) # Redirect to the company page
            
            # Check if user is a supervisor
            query = "SELECT * FROM user WHERE email = %s AND role = 'supervisor'"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()
            if user_data:

                    # Get the supervisor_id
                    query = "SELECT supervisor_id FROM supervisor WHERE supervisor_email = %s"
                    cursor.execute(query, (email,))
                    supervisor_id = cursor.fetchone()[0]

                    # Store the supervisor_id in the session
                    session['user_id'] = supervisor_id
                    session['role'] = 'supervisor' # Store the role in the session

                    cursor.close()
                    return redirect(url_for('supervisorStudentDetails', supervisor_id=supervisor_id)) # Redirect to the supervisor page
            
            # Check if user is an admin
            query = "SELECT * FROM user WHERE email = %s AND role = 'admin'"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()
            if user_data:

                # Get the admin_id
                # TODO: Add admin_id to the database


                cursor.close()
                return redirect(url_for('admin'))
            
            # If user is not a student, company, supervisor or admin, then something is wrong
            flash('An error occurred. Please try again.', 'error')
            return render_template('login.html', form_data=request.form)
        
        except Exception as e:
            print(f"Error during login: {e}")
            flash('An error occurred. Please try again.', 'error')
            return render_template('login.html', form_data=request.form)
        
        finally:
            cursor.close()    

@app.route('/register_company', methods=['GET', 'POST'])
def register_company():
    error_messages = {}

    if request.method == 'GET':
        return render_template('register_company.html')
    
    if request.method == 'POST':

        print(f"Form data: {request.form}")

        try:
            cursor = db_conn.cursor()
            # Fetch Company data
            companyName = request.form.get('companyName')
            industry = request.form.get('industry')
            contactName = request.form.get('contactName')
            contactEmail = request.form.get('contactEmail')
            userEmail = request.form.get('userEmail')
            userPassword = request.form.get('userPassword')
            companyConfirmedPassword = request.form.get('companyConfirmedPassword')

            
            #Check if all fields are filled
            if not all([companyName, industry, contactName, contactEmail, userEmail, userPassword, companyConfirmedPassword]):
                error_messages['all_fields'] = 'Error! Please fill in all fields.'

            # Check if password and confirmed password match
            if userPassword != companyConfirmedPassword:
                error_messages['companyPassword'] = 'Password and confirmed password do not match.'

            # Check if email already exists
            query = "SELECT * FROM user WHERE email = %s"
            cursor.execute(query, (userEmail,))
            user_data = cursor.fetchone()
            if user_data:
                error_messages['userEmail'] = 'Email already exists.'


            if error_messages:
                return render_template('register_company.html', error_messages=error_messages, form_data=request.form)
            
            # Insert into user table
            query = """INSERT INTO user
                    (email, password, role)
                    VALUES (%s, %s, 'company')"""
            cursor.execute(query, (userEmail, userPassword))
            db_conn.commit()

            # Get the user_id of the newly inserted user
            query = "SELECT id FROM user WHERE email = %s"
            cursor.execute(query, (userEmail,))
            user_id = cursor.fetchone()[0]


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
            return redirect(url_for('register_company'))  # Redirect to the registration page



@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    error_messages = {}  # Dictionary to store error message

    if request.method == 'GET':
        return render_template('register_student.html')  # default to student form

    if request.method == 'POST':
        print(f"Form data: {request.form}")

        try:
            cursor = db_conn.cursor()

            # Fetch Student data
            educationLevel = request.form.get('educationLevel')
            cohort = request.form.get('cohort')
            programme = request.form.get('programme')
            tutorialGroup = request.form.get('tutorialGroup')
            studentName = request.form.get('studentName')
            studentID = request.form.get('studentID')
            studentEmail = request.form.get('studentEmail')
            supervisorName = request.form.get('supervisorName')
            supervisorEmail = request.form.get('supervisorEmail')
            programmingKnowledge = request.form.get('programmingKnowledge')
            databaseKnowledge = request.form.get('databaseKnowledge')
            networkingKnowledge = request.form.get('networkingKnowledge')
            studentPassword = request.form.get('studentPassword')
            studentConfirmedPassword = request.form.get('studentConfirmedPassword')

            supervisor_id = 1

            #Check if all fields are filled
            if not all([educationLevel, cohort, programme, tutorialGroup, studentID, studentEmail, supervisorName, supervisorEmail, programmingKnowledge, databaseKnowledge, networkingKnowledge, studentPassword, studentConfirmedPassword]):
                error_messages['all_fields'] = 'Error! Please fill in all fields.'

            # Check if password and confirmed password match
            if studentPassword != studentConfirmedPassword:
                error_messages['studentPassword'] = 'Password and confirmed password do not match.'

            # Check if email already exists
            query = "SELECT * FROM user WHERE email = %s"
            cursor.execute(query, (studentEmail,))
            student_data = cursor.fetchone()

            if student_data :
                error_messages['studentEmail'] = 'Email already exists.'

            # Check if student ID already exists
            query = "SELECT * FROM user WHERE studentId = %s"
            cursor.execute(query, (studentID,))
            student_data = cursor.fetchone()
            if student_data:
                error_messages['studentID'] = 'Student ID already exists.'

            


       # Check if the supervisor name not found
            query = "SELECT * FROM supervisor WHERE supervisor_name = %s"
            cursor.execute(query, (supervisorName,))
            supervisor_name= cursor.fetchone()
             # Check if supervisor name matches
            if not  supervisor_name:  # Assuming supervisor name is in the second column
                error_messages['supervisorName'] = 'Supervisor name does not match the database.'

            # Check if supervisor email not found
            query = "SELECT * FROM supervisor WHERE supervisor_email = %s"
            cursor.execute(query, (supervisorEmail,))
            supervisor_data = cursor.fetchone()
            if not supervisor_data:
                error_messages['supervisorEmail'] = 'Supervisor email not found.'
            else:
                supervisor_id = supervisor_data[0]
                
            if error_messages:
                return render_template('register_student.html', error_messages=error_messages, form_data=request.form)

            # Insert into user table
            query = """INSERT INTO user
                    (email, password, role)
                    VALUES (%s, %s, 'student')"""
            cursor.execute(query, (studentEmail, studentPassword))
            db_conn.commit()

            # Get the user_id of the newly inserted user
            query = "SELECT id FROM user WHERE email = %s"
            cursor.execute(query, (studentEmail,))
            user_id = cursor.fetchone()[0]

            # Update the student table
            query = """UPDATE student 
                    SET 
                        user_id = %s
                    WHERE student_id = %s"""

            # Provide the values for the update
            cursor.execute(query, (user_id, studentID ))
            db_conn.commit()
            cursor.close()


            flash('Registration successful!', 'success')
            return redirect(url_for('login'))  # Redirect to the login page

        except Exception as e:
            print(f"Error during registration: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('register_student'))  # Redirect to the registration page


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') == 'production':
        print("PRODUCTION ENVIRONMENT")
        app.run(host='0.0.0.0', port=80)
    else:
        print("DEVELOPMENT ENVIRONMENT")
        app.run(debug=True)

    
