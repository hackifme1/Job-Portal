from turtle import fd
from flask import Flask, render_template, url_for, request, redirect, flash
from flask import session
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = "DBMS"

# Configure Database
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "enter_your_MYSQL_password_here"
app.config['MYSQL_DB'] = "jobportal"

mysql = MySQL(app)

#creating route for admin login
@app.route('/admin_login', methods = ['GET', 'POST'])
def admin_login():
    find = 0
    if request.method == 'POST':
        # retrieving the entries made in the admin login form
        admin_loginDetails = request.form
        admin_email = admin_loginDetails['email1']
        admin_password = admin_loginDetails['password1']
        cur = mysql.connection.cursor()
        # selecting email and password attributes from admin entity to check if the email and its password exists in the entity
        find = cur.execute("SELECT * FROM admin WHERE (email, password) = (%s, %s) ", (admin_email, admin_password))
        admin_details = cur.fetchall()
        cur.close()
        # login to admin home page if we find such an entry in the table or redirect to the same page
        if find != 0:
            admin_user = admin_details[0][0]
            session["admin_user"] = admin_user
            print(admin_user)
            return redirect('/admin_home')
        else: 
            if "admin_user" in session:
                return redirect(url_for("admin_home"))
            
            error_msg = "Wrong Credentials!!"
            flash(f'{error_msg}', category='danger')
            return render_template('admin_login.html', find = find)
    else:
        if "admin_user" in session:
            return redirect(url_for("admin_home"))
        
        return render_template('admin_login.html', find = find)


# creating route for applicants management
@app.route('/manage_applicants', methods = ['GET', 'POST'])
def manage_applicants():
    if "admin_user" in session:
        cur = mysql.connection.cursor()
        # retrieving all entries from jobseeker table to be shown on the page
        cur.execute("SELECT jobseeker_id, first_name, email, password, status FROM jobseeker")
        users_registered = cur.fetchall() 
        cur.close()
        return render_template('manage_applicants.html', users_registered = users_registered)
    else:
        return redirect(url_for('admin_login'))
    
# creating route for details of the jobseekrs
@app.route('/details/<int:id>', methods = ['GET', 'POST'])
def details(id):
    if "admin_user" in session:
        cur = mysql.connection.cursor()
        # displaying the details of a particular jobseeker
        cur.execute("SELECT first_name, last_name, phone_number, address, email, status, password FROM jobseeker WHERE jobseeker_id = {}".format(id))
        user_details = cur.fetchall() 
        if user_details:
            user_details = user_details[-1]
            
        cur.close()
        cur2 = mysql.connection.cursor()
        # selecting all the profile details of the user from profile table to display in details section
        cur2.execute("SELECT * FROM profile WHERE jobseeker_id = {}".format(id))
        profile_details = cur2.fetchall()
        if profile_details:
            profile_details = profile_details[-1]
        # selecting the resume details of the user from resume table
        cur2.execute("SELECT * FROM resume WHERE jobseeker_id = {}".format(id))
        resume_details = cur2.fetchall()
        if resume_details:
            resume_details = resume_details[-1]
        
        cur2.close()
        
        cur3 = mysql.connection.cursor()
        # displaying the job details and corresponding company details of the jobs the user has applied for by using INNER JOIN on 
        # job and company tables and using subquery for selecting jobs user has applied for from the apply table 
        cur3.execute("SELECT job.job_title, job.job_type, company.name, company.location, job.job_salary, \
        job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE job.job_id in (SELECT job_id FROM apply WHERE \
        jobseeker_id = {})".format(id))
        applied_jobs = cur3.fetchall()
        cur3.close()
        
        return render_template('details.html', applied_jobs = applied_jobs, user_details = user_details, profile_details = profile_details, resume_details = resume_details)
    else:
        return redirect(url_for('admin_login'))


# creating route for updating details of applicants
@app.route('/update_details/<int:id>', methods = ['GET', 'POST'])
def update_details(id):
    if "admin_user" in session:
        cur = mysql.connection.cursor()
        # selecting all profile details for the specified user
        exist = cur.execute("SELECT * FROM profile WHERE jobseeker_id = {}".format(id))
        profile_data = cur.fetchall()
        cur.close()
        
        cur1 = mysql.connection.cursor()
        # selecting all basic details for the specified user
        exist = cur1.execute("SELECT * FROM jobseeker WHERE jobseeker_id = {}".format(id))
        jobseeker_data = cur.fetchall()
        cur1.close()
        
        if request.method == 'POST':
            profile = request.form
            firstname = profile['ufname']
            lastname = profile['ulname']
            phnum = profile['uphoneno']
            addrs = profile['uaddress']
            eml = profile['uemail']
            paswrd = profile['upasswrd']
            college = profile['college']
            dept = profile['dept']
            education = profile['education']
            filename = profile['resume']
            
            cur1 = mysql.connection.cursor()
            # selecting all profile details for the logged in user
            exist = cur1.execute("SELECT * FROM jobseeker WHERE jobseeker_id = {}".format(id))
            if exist > 0:
                # If the profile entry for user exists, then update the profile details in the profile table for that entry using UPDATE clause
                cur1.execute("UPDATE jobseeker SET first_name = (%s), last_name = (%s), phone_number = (%s), address = (%s), email = (%s), password = (%s) WHERE jobseeker_id = (%s)", (firstname, lastname, phnum, addrs, eml, paswrd, id))
                mysql.connection.commit()
            else:
                # If the profile entry for that user doesnt exist in the profile table, then insert a record for profile details of that user
                cur1.execute("INSERT INTO jobseeker(first_name, last_name, phone_number, address, email, password, jobseeker_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (firstname, lastname, phnum, addrs, eml, paswrd, id, "1"))
                mysql.connection.commit()
            cur1.close()
            
            cur = mysql.connection.cursor()
            # selecting all profile details for the logged in user
            exist = cur.execute("SELECT * FROM profile WHERE jobseeker_id = {}".format(id))
            if exist > 0:
                # If the profile entry for user exists, then update the profile details in the profile table for that entry using UPDATE clause
                cur.execute("UPDATE profile SET college = (%s), department = (%s), education = (%s) WHERE jobseeker_id = (%s)", (college, dept, education, id))
                mysql.connection.commit()
            else:
                # If the profile entry for that user doesnt exist in the profile table, then insert a record for profile details of that user
                cur.execute("INSERT INTO profile(college, department, education, jobseeker_id) VALUES (%s, %s, %s, %s)", (college, dept, education, id))
                mysql.connection.commit()
            cur.close()

            cur2 = mysql.connection.cursor()
            # selecting resume details of the user that is logged in
            res = cur2.execute("SELECT * FROM resume WHERE resume_id = {}".format(id))
            if res > 0:
                # if the resume entry exists for that user, then update the resume filename for the entry
                cur2.execute("UPDATE resume SET filename = (%s) WHERE resume_id = (%s)", (filename, id))
                mysql.connection.commit()
            else:
                # if the resume entry doesnt exist, then insert a new entry in resume table for that user with the filename
                cur2.execute("INSERT INTO resume(filename, jobseeker_id) VALUES (%s, %s)", (filename, id))
                mysql.connection.commit()
            cur2.close()
            sccss_msg = "Details successfully updated!!"
            flash(f'{sccss_msg}', category='success')
            return redirect(url_for('manage_applicants'))
        
        return render_template('update_details.html', id = id, profile_data = profile_data, jobseeker_data = jobseeker_data)
    else:
        return redirect(url_for('admin_login'))
    
    
# creating route for deleting applicants account
@app.route('/delete_user/<int:id>')
def delete_user(id):
    if "admin_user" in session:
        cur = mysql.connection.cursor()
        # selecting jobseeker details to display the name of the specific jobseeker
        res = cur.execute("SELECT * FROM jobseeker WHERE jobseeker_id = {}".format(id))    
        # usr= cur.fetchall()
        
        if res > 0:
            # if the user entry exists for that user, then delete the user from the database
            cur.execute("DELETE FROM jobseeker WHERE jobseeker_id={}".format(id))
            mysql.connection.commit()
            cur.close()
        else:
            # if the user entry doesnt exist, then stay on the same by doing nothing
            return redirect(url_for('manage_applicants'))
            
        return redirect(url_for('manage_applicants'))
    else:
        return redirect(url_for('admin_login'))

# creating route for blocking or unblocking an applicant from using the web portal
@app.route('/blockorunblock_user/<int:id>')
def blockorunblock_user(id):
    if "admin_user" in session:
        cur = mysql.connection.cursor()
        # selecting jobseeker details to display the name of the jobseeker specified
        res = cur.execute("SELECT status FROM jobseeker WHERE jobseeker_id = {}".format(id))    
        usrid = cur.fetchall()
        
        if res > 0:
            # if the user entry exists for that user, then update the state of that user accordingly
            if usrid[0][0] == "1":
                cur.execute("UPDATE jobseeker SET status = (%s) WHERE jobseeker_id = (%s)", ("0", id))
                mysql.connection.commit()
            else:
                cur.execute("UPDATE jobseeker SET status = (%s) WHERE jobseeker_id = (%s)", ("1", id))
                mysql.connection.commit()
                
            cur.close()    
        else:
            # if the user entry doesnt exist, then stay on the same by doing nothing
            return redirect(url_for('manage_applicants'))
            
        return redirect(url_for('manage_applicants'))
    else:
        return redirect(url_for('admin_login'))


# creating route for managing companies
@app.route('/manage_company', methods = ['GET', 'POST'])
def manage_company():
    if "admin_user" in session:
        cur = mysql.connection.cursor()
        # displaying company details 
        cur.execute("SELECT * FROM company")
        cmpny = cur.fetchall() 
        cur.close()
        return render_template('manage_company.html', cmpny = cmpny)
    else:
        return redirect(url_for('admin_login'))


# creating route for editing companies details
@app.route('/editcomp_details/<int:id>', methods = ['GET', 'POST'])
def editcomp_details(id):
    if "admin_user" in session:
        cur = mysql.connection.cursor()
        # retrieving specified company details
        exist = cur.execute("SELECT * FROM company WHERE company_id = {}".format(id))
        company_data = cur.fetchall()
        cur.close()
        
        if request.method == 'POST':
            company_det = request.form
            comp_name = company_det['cname']
            comp_location = company_det['clocn']
            
            cur1 = mysql.connection.cursor()
            # selecting all details for the specified company
            exist = cur1.execute("SELECT * FROM company WHERE company_id = {}".format(id))
            if exist > 0:
                # If the company entry exists, then update the company details in the company table for that entry using UPDATE clause
                cur1.execute("UPDATE company SET name = (%s), location = (%s) WHERE company_id = (%s)", (comp_name, comp_location, id))
                mysql.connection.commit()
            else:
                # If the company doesnt exist in the profile table, then insert a record for company details
                cur1.execute("INSERT INTO company(name, location, company_id) VALUES (%s, %s, %s)", (comp_name, comp_location, id))
                mysql.connection.commit()
            cur1.close()
            
            sccss_msg = "Details successfully updated!!"
            flash(f'{sccss_msg}', category='success')
            return redirect(url_for('manage_company'))
        
        return render_template('editcomp_details.html', id = id, company_data = company_data)
    else:
        return redirect(url_for('admin_login'))
    
    
# creating route for adding company
@app.route('/add_company', methods = ['GET', 'POST'])
def add_company():
    if "admin_user" in session:
        cur = mysql.connection.cursor()
        # selecting all company details for the specified company
        exist = cur.execute("SELECT * FROM company")
        company_data = cur.fetchall()
        cur.close()
        
        if request.method == 'POST':
            # retrieving the entries made in the company form
            cmpnyDetails = request.form
            cmpnames = cmpnyDetails['cmpname']
            cmplocns = cmpnyDetails['cmplocn']
        
           
            cur = mysql.connection.cursor()
            # for checking if same company exists or not 
            exist1 = cur.execute("SELECT * FROM company WHERE name = '{}' AND location = '{}'".format(cmpnames, cmplocns))
            
            if exist1 == 0:
                cur.execute("INSERT INTO company(name, location) VALUES (%s, %s)", (cmpnames, cmplocns))
                mysql.connection.commit()
                cur.close()
                    # go to login page on submit
                succs_msg = "Company added successfully!!"
                flash(f'{succs_msg}', category='success')
            else:
                err_msg = "Company already exists!!"
                flash(f'{err_msg}', category='danger')
                
            return redirect(url_for('manage_company'))
        else:
            return render_template('add_company.html')
    
    return render_template(url_for('admin_login'))


# creating route for managing job
@app.route('/manage_job', methods = ['GET', 'POST'])
def manage_job():
    if "admin_user" in session:
        if request.method == 'POST':
            searchjob = request.form
            keyword = searchjob['keyword']
            location = searchjob['location']
            cur = mysql.connection.cursor() 
            # if only keyword is entered in the job search, then select those jobs where the keyword matches the job details
            # by using LIKE clause and inner join on jobs and corresponding companies 
            if keyword and (not location):
                count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')".format(keyword, keyword, keyword))
            # if only location is entered in the job search, then select those jobs where the keyword matches the company location
            # by using LIKE clause and inner join on jobs and corresponding companies
            elif location and (not keyword):
                count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (company.location LIKE '%{}%')".format(location))
            # if keyword and location are entered in the job search, then select those jobs where the keyword matches the job details
            # and company location by using LIKE clause and inner join on jobs and corresponding companies
            elif location and keyword:
                count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE ((job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')) AND (company.location LIKE '%{}%')".format(keyword, keyword, keyword, location))
            else:
                count_search = 0

            jobsearch = cur.fetchall()
            cur.close()
            return render_template('admin_jobsearch.html', jobsearch = jobsearch)

        cur = mysql.connection.cursor()
        # display all jobs and their details by selecting all jobs of companies using inner join on job and company
        count_jobs = cur.execute("SELECT job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id")
        # count_location = cur.execute("SELECT company.location FROM job INNER JOIN company ON job.company_id = company.company_id")

        alljobs = cur.fetchall()
        cur.close()
        return render_template('manage_job.html', alljobs = alljobs)
    else:
        return redirect(url_for('admin_login'))


# creating route for adding job
@app.route('/add_job', methods = ['GET', 'POST'])
def add_job():
    if "admin_user" in session:        
        if request.method == 'POST':
            # retrieving the entries made in the job form
            jobdetails = request.form
            cmpnyid = jobdetails['cmpid']
            jobtitle = jobdetails['jbtitle']
            jobtype = jobdetails['jbtype']
            jobdescrptn = jobdetails['jbdescr']
            jobsalary = jobdetails['jbsalary']
            
            cur = mysql.connection.cursor()
            exist = cur.execute("SELECT * from company WHERE company_id = {}".format(cmpnyid))
            
            if exist > 0:
                cur.execute("INSERT INTO job(company_id, job_title, job_type, job_description, job_salary) VALUES (%s, %s, %s, %s, %s)", (cmpnyid, jobtitle, jobtype, jobdescrptn, jobsalary))
                mysql.connection.commit()
                cur.close()
                succs_msg = "Job added successfully!!"
                flash(f'{succs_msg}', category='success')
            else:
                err_msg = "There is no company registered with input id!!"
                flash(f'{err_msg}', category='danger')
                
                return redirect(url_for('add_job'))

            return redirect(url_for('manage_job'))
        else:
            return render_template('add_job.html')
    
    return render_template(url_for('admin_login'))


# creating route for admin jobsearch
@app.route('/admin_jobsearch')
def admin_jobsearch():
    if "admin_user" in session:
        return render_template('admin_jobsearch.html')
    else:
        return redirect(url_for('admin_login'))
    

# creating route for viewing job details
@app.route('/job_detail/<frm>/<id>', methods = ['GET', 'POST'])
def job_detail(frm,id):
    if "admin_user" in session:        
        idact = id[1::]
        
        if request.method == 'POST':
            searchjob = request.form
            keyword = searchjob['keyword']
            location = searchjob['location']
            cur = mysql.connection.cursor() 
            # if only keyword is entered in the job search, then select those jobs where the keyword matches the job details
            # by using LIKE clause and inner join on jobs and corresponding companies 
            if keyword and (not location):
                if id[0] == 'l':
                    count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE ((job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')) AND (company.location LIKE '{}')".format(keyword, keyword, keyword, idact))
                elif id[0] == 't':
                    count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE ((job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')) AND (job.job_title LIKE '{}')".format(keyword, keyword, keyword, idact))
                elif id[0] == 'g':
                    count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE ((job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')) AND (job.job_type LIKE '{}')".format(keyword, keyword, keyword, idact))
                elif id[0] == 'c':
                    count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE ((job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')) AND (company.name LIKE '{}')".format(keyword, keyword, keyword, idact))           
            # if only location is entered in the job search, then select those jobs where the keyword matches the company location
            # by using LIKE clause and inner join on jobs and corresponding companies
            elif location and (not keyword):
                if id[0] == 'l':
                    count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (company.location LIKE '%{}%') AND (company.location LIKE '{}')".format(location, idact))
                elif id[0] == 't':
                    count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (company.location LIKE '%{}%') AND (job.job_title LIKE '{}')".format(location, idact))
                elif id[0] == 'g':
                    count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (company.location LIKE '%{}%') AND (job.job_type LIKE '{}')".format(location, idact))
                elif id[0] == 'c':
                    count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (company.location LIKE '%{}%') AND (company.name LIKE '{}')".format(location, idact))          
            # if keyword and location are entered in the job search, then select those jobs where the keyword matches the job details
            # and company location by using LIKE clause and inner join on jobs and corresponding companies
            elif location and keyword:
                if id[0] == 'l':
                    count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (((job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')) AND (company.location LIKE '%{}%')) AND (company.location LIKE '{}')".format(keyword, keyword, keyword, location, idact))
                elif id[0] == 't':
                    count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (((job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')) AND (company.location LIKE '%{}%')) AND (job.job_title LIKE '{}')".format(keyword, keyword, keyword, location, idact))
                elif id[0] == 'g':
                    count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (((job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')) AND (company.location LIKE '%{}%')) AND (job.job_type LIKE '{}')".format(keyword, keyword, keyword, location, idact))
                elif id[0] == 'c':
                    count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (((job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')) AND (company.location LIKE '%{}%')) AND (company.name LIKE '{}')".format(keyword, keyword, keyword, location, idact))
            else:
                count_search = 0

            jobsearch = cur.fetchall()
            return render_template('admin_jobsearch.html', jobsearch = jobsearch)

        
        # displaying the job details and corresponding company details of the jobs the user has applied for by using INNER JOIN on 
        # job and company tables and using subquery for selecting jobs user has applied for from the apply table for categorised search
        if id[0] == 'l':
            cur = mysql.connection.cursor()
            exists = cur.execute("SELECT job.job_id, job.job_title, job.job_type, job.job_description, job.job_salary, company.name, company.location FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (company.location LIKE '%{}%')".format(idact))
            
            addnltpl = cur.fetchall()             
              
            cur.close()
            if exists > 0:
                return render_template('job_detail.html', idact = idact, addnltpl = addnltpl)      
            else:
                err_msg = "No job with the specified location is found!!"
                flash(f'{err_msg}', category='danger')
                if(frm == "mainpge"):
                    return redirect(url_for('manage_job'))  
                else:
                    return redirect(url_for('viewmore',id="location"))  
        elif id[0] == 't':
            cur = mysql.connection.cursor()
            exists = cur.execute("SELECT job.job_id, job.job_title, job.job_type, job.job_description, job.job_salary, company.name, company.location FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (job.job_title LIKE '%{}%')".format(idact))
            
            addnltpl = cur.fetchall()             
              
            cur.close()
            if exists > 0:
                return render_template('job_detail.html', idact = idact, addnltpl = addnltpl)      
            else:
                err_msg = "No job with the specified title found!!"
                flash(f'{err_msg}', category='danger')
                if(frm == "mainpge"):
                    return redirect(url_for('manage_job'))  
                else:
                    return redirect(url_for('viewmore',id="title")) 
        elif id[0] == 'g':
            cur = mysql.connection.cursor()
            exists = cur.execute("SELECT job.job_id, job.job_title, job.job_type, job.job_description, job.job_salary, company.name, company.location FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (job.job_type LIKE '%{}%')".format(idact))
            
            addnltpl = cur.fetchall()             
              
            cur.close()
            if exists > 0:
                return render_template('job_detail.html', idact = idact, addnltpl = addnltpl)      
            else:
                err_msg = "No job with the specified category found!!"
                flash(f'{err_msg}', category='danger')
                if(frm == "mainpge"):
                    return redirect(url_for('manage_job'))  
                else:
                    return redirect(url_for('viewmore',id="category"))
        elif id[0] == 'c':
            cur = mysql.connection.cursor()
            exists = cur.execute("SELECT job.job_id, job.job_title, job.job_type, job.job_description, job.job_salary, company.name, company.location FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (company.name LIKE '%{}%')".format(idact))
            
            addnltpl = cur.fetchall()             
              
            cur.close()
            if exists > 0:
                return render_template('job_detail.html', idact = idact, addnltpl = addnltpl)      
            else:
                err_msg = "No job with the specified company found!!"
                flash(f'{err_msg}', category='danger')
                if(frm == "mainpge"):
                    return redirect(url_for('manage_job'))  
                else:
                    return redirect(url_for('viewmore',id="company"))
              
        redirect(url_for('manage_job'))                 
    else:
        return redirect(url_for('admin_login'))
    

# creating route for viewmore items in different categories
@app.route('/viewmore/<id>', methods = ['GET', 'POST'])
def viewmore(id):
    if "admin_user" in session:
        if request.method == 'POST':
            searchjob = request.form
            keyword = searchjob['keyword']
            location = searchjob['location']
            cur = mysql.connection.cursor() 
            # if only keyword is entered in the job search, then select those jobs where the keyword matches the job details
            # by using LIKE clause and inner join on jobs and corresponding companies 
            if keyword and (not location):
                count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')".format(keyword, keyword, keyword))
            # if only location is entered in the job search, then select those jobs where the keyword matches the company location
            # by using LIKE clause and inner join on jobs and corresponding companies
            elif location and (not keyword):
                count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (company.location LIKE '{}')".format(location))
            # if keyword and location are entered in the job search, then select those jobs where the keyword matches the job details
            # and company location by using LIKE clause and inner join on jobs and corresponding companies
            elif location and keyword:
                count_search = cur.execute("SELECT job.job_id, job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE ((job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')) AND (company.location LIKE '{}')".format(keyword, keyword, keyword, location))
            else:
                count_search = 0

            jobsearch = cur.fetchall()
            return render_template('admin_jobsearch.html', jobsearch = jobsearch)
        
        return render_template('viewmore.html', id = id)
    else:
        return redirect(url_for('admin_login'))


# creating route for editing or updating job details
@app.route('/editjob/<int:id>', methods = ['GET', 'POST'])
def editjob(id):
    if "admin_user" in session:
        cur = mysql.connection.cursor()
        # selecting all job details for the specified job
        exist = cur.execute("SELECT * FROM job WHERE job_id = {}".format(id))
        job_data = cur.fetchall()
        cur.close()
        
        if request.method == 'POST':
            job_det = request.form
            job_titl = job_det['jtitle']
            job_ctgry = job_det['jtype']
            job_descr = job_det['jdescrpn']
            job_slry = job_det['jsalary']
            cur1 = mysql.connection.cursor()
            # selecting all job details for the specified job
            exist = cur1.execute("SELECT * FROM job WHERE job_id = {}".format(id))
            if exist > 0:
                # If the job entry for job exists, then update the job details in the job table for that entry using UPDATE clause
                cur1.execute("UPDATE job SET job_title = (%s), job_type = (%s), job_description = (%s), job_salary = (%s) WHERE job_id = (%s)", (job_titl, job_ctgry, job_descr, job_slry, id))
                mysql.connection.commit()
            else:
                # If the job entry for that job doesnt exist in the job table, then insert a record for job details of that job
                cur1.execute("INSERT INTO job(job_title, job_type, job_description, job_salary) VALUES (%s, %s, %s, %s)", (job_titl, job_ctgry, job_descr, job_slry))
                mysql.connection.commit()
            cur1.close()
            
            sccss_msg = "Details successfully updated!!"
            flash(f'{sccss_msg}', category='success')
            return redirect(url_for('manage_job'))
        
        return render_template('editjob.html', id = id, job_data = job_data)
    else:
        return redirect(url_for('admin_login'))


# creating route for deleting a job
@app.route('/delete_job/<int:id>')
def delete_job(id):
    if "admin_user" in session:
        cur = mysql.connection.cursor()
        # selecting job details for a specified job
        res = cur.execute("SELECT * FROM job WHERE job_id = {}".format(id))    
        # usr= cur.fetchall()
        
        if res > 0:
            # if the job entry exists for that job, then delete the job from the database
            cur.execute("DELETE FROM job WHERE job_id = {}".format(id))
            mysql.connection.commit()
            cur.close()
        else:
            # if the job entry doesnt exist, then stay on the same by doing nothing
            return redirect(url_for('manage_job'))
            
        return redirect(url_for('manage_job'))
    else:
        return redirect(url_for('admin_login'))


# creating route for scheduling interview
@app.route('/schedule_interview/<int:id>', methods = ['GET', 'POST'])
def schedule_interview(id):
    if "admin_user" in session:
        if request.method == 'POST':
            intrvw_detls = request.form
            cndt_id = intrvw_detls['ijobsekrid']
            intrvw_date = intrvw_detls['idate']
            intrvw_time = intrvw_detls['itime']
            cur1 = mysql.connection.cursor()
            # selecting all jobseeker details for the specified id
            # tackling different cases like if user has not applied then he or she wont be in apply table or if they have got result 
            # for that job then also they wont be in apply table
            exist = cur1.execute("SELECT * FROM jobseeker WHERE jobseeker_id = {}".format(cndt_id))
            if exist > 0:
                exist2 = cur1.execute("SELECT * FROM apply WHERE (jobseeker_id = {}) AND (job_id = {})".format(cndt_id, id))
                
                if exist2 > 0:
                    exist3 = cur1.execute("SELECT * FROM interview WHERE (jobseeker_id = {}) AND (job_id = {})".format(cndt_id, id))
                    if exist3 == 0:
                        exist4 = cur1.execute("SELECT * FROM result WHERE jobseeker_id = {} AND job_id = {}".format(cndt_id, id))      
                        if exist4 > 0:
                            err_msg = "Candidate specified result has already been declared for this job!!"
                            flash(f'{err_msg}', category='warning')    
                        else:              
                            cur1.execute("INSERT INTO interview(job_id, date, time, jobseeker_id) VALUES (%s, %s, %s, %s)", (id, intrvw_date, intrvw_time, cndt_id))
                            mysql.connection.commit()
                            cur1.close()
                    else:
                        wrng = "Candidate specified interview has already been scheduled for this job!!"
                        flash(f'{wrng}', category='warning') 

                    return redirect(url_for('manage_job'))
                else:
                    err_msg = "Candidate specified hasn't applied for this job!!"
                    flash(f'{err_msg}', category='danger')
                    return render_template('schedule_interview.html',id=id)                
            else:
                err_msg = "Candidate not found in database!!"
                flash(f'{err_msg}', category='danger')
                return render_template('schedule_interview.html',id=id)
        else:
            return render_template('schedule_interview.html', id=id)
    else:
        return redirect(url_for('admin_login'))
    
    
# creating route for declaring result
@app.route('/declare_result/<int:id>', methods = ['GET', 'POST'])
def declare_result(id):
    if "admin_user" in session:        
        if request.method == 'POST':
            res = request.form
            cndt_id = res['rjobsekrid']
            vrdct = res['rvrdct']
            cur1 = mysql.connection.cursor()
            
            # before declaring result checking if that user exists or not and if that user exists then checking if his or her interview
            # is scheduled or not, if scheduled then declare result and delete the entry from interview as well
            # if not in scheduled then chk if declared already or not, if yes then showing the same else showing not scheduled
            exist = cur1.execute("SELECT * FROM jobseeker WHERE jobseeker_id = {}".format(cndt_id))
            if exist > 0:
                exist2 = cur1.execute("SELECT * FROM apply WHERE jobseeker_id = {} AND job_id = {}".format(cndt_id, id))
                
                if exist2 > 0:
                    exist3 = cur1.execute("SELECT * FROM interview WHERE jobseeker_id = {} AND job_id = {}".format(cndt_id, id))
                    
                    if exist3 > 0:
                        cur1.execute("INSERT INTO result(jobseeker_id, job_id, status) VALUES (%s, %s, %s)", (cndt_id, id, vrdct))
                        mysql.connection.commit()
                        cur1.execute("DELETE FROM interview WHERE jobseeker_id = {} AND job_id = {}".format(cndt_id, id))
                        mysql.connection.commit()
                    else:
                        exist4 = cur1.execute("SELECT * FROM result WHERE jobseeker_id = {} AND job_id = {}".format(cndt_id, id))
                        cur1.close()
                        if exist4 > 0:
                            err_msg = "Candidate specified result has already been declared for this job!!"
                            flash(f'{err_msg}', category='danger')
                        else:
                            err_msg = "Candidate specified interview has not been scheduled yet for this job!!"
                            flash(f'{err_msg}', category='warning')
                        
                    return redirect(url_for('manage_job'))
                else:
                    err_msg = "Candidate specified hasn't applied for this job!!"
                    flash(f'{err_msg}', category='danger')
                    return render_template('declare_result.html', id=id)
                
            else:
                err_msg = "Candidate not found in database!!"
                flash(f'{err_msg}', category='danger')
                return render_template('declare_result.html', id=id)
        else:
            return render_template('declare_result.html', id=id)
    else:
        return redirect(url_for('admin_login'))
    
    
# creating route for home
@app.route('/', methods = ['GET', 'POST'])
def login():
    find = 0
    if request.method == 'POST':
        # retrieving the entries made in the login form
        loginDetails = request.form
        email = loginDetails['email']
        password = loginDetails['password']
        cur = mysql.connection.cursor()
        # selecting email and password attributes from jobseeker entity to check if the email and its password exists in the entity
        find = cur.execute("SELECT * FROM jobseeker WHERE (email, password) = (%s, %s) ", (email, password))
        details = cur.fetchall()
        cur.close()
    # login to home page if we find such an entry in the table or redirect to the same page
        if find != 0:
            user = details[0][0]
            
            if details[0][7] == "1":
                session["user"] = user
                print(user)
                return redirect('/home')
            else:
                err_msg = "You are temporarily blocked by the admin!!"
                flash(f'{err_msg}', category='danger')
                return render_template('login.html', find = find)
        else: 
            if "user" in session:
                return redirect(url_for("home"))
                        
            error_msg = "User not registered!!"
            flash(f'{error_msg}', category='danger')
            return render_template('login.html', find = find)
    else:
        if "user" in session:
            return redirect(url_for("home"))
        
        return render_template('login.html', find = find)


# creating route for signup of user
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # retrieving the entries made in the signup form
        userDetails = request.form
        fname = userDetails['fname']
        lname = userDetails['lname']
        phone_num = userDetails['phone_num']
        address = userDetails['address']
        email = userDetails['email']
        password = userDetails['password']
        cpassword = userDetails['cpassword']
        # checking if the password entered in both the fields are same
        if password == cpassword:
            cur = mysql.connection.cursor()
            # creating a record by inserting the jobseeker details in jobseeker entity
            cur.execute("INSERT INTO jobseeker(first_name, last_name, phone_number, address, email, password, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (fname, lname, phone_num, address, email, password, "1"))
            mysql.connection.commit()
            cur.close()
            # go to login page on submit
            succs_msg = "Registration successfully done!!"
            flash(f'{succs_msg}', category='success')
            return redirect('/')
        else:
            err_msg = "Registration failed due to password mismatch!!"
            flash(f'{err_msg}', category='danger')
            return redirect('signup')
    return render_template('signup.html')


# creating route for admin home
@app.route('/admin_home', methods = ['GET', 'POST'])
def admin_home():
    if "admin_user" in session:
        admin_user = session["admin_user"]
        cur = mysql.connection.cursor()
        # selecting admin details to display the name of the admin on the home page who is currently logged in
        cur.execute("SELECT * FROM admin WHERE admin_id = {}".format(admin_user))
        admin_userdet = cur.fetchall()
        admin_name = admin_userdet[0][1]
        return render_template('admin_home.html', name = admin_name)
    else:
        return redirect(url_for('admin_login'))
    
    
# creating route for user home
@app.route('/home', methods = ['GET', 'POST'])
def home():
    if "user" in session:
        user = session["user"]
        cur = mysql.connection.cursor()
        # selecting jobseeker details to display the name of the jobseeker on the home page who is currently logged in
        cur.execute("SELECT * FROM jobseeker WHERE jobseeker_id = {}".format(user))
        userdet = cur.fetchall()
        name = userdet[0][1]  
        return render_template('home.html', name = name)
    else:
        return redirect(url_for('login'))


# creating route for user profile
@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    if "user" in session:
        user = session['user']
        cur = mysql.connection.cursor()
        # displaying the job details and corresponding company details of the jobs the user has applied for by using INNER JOIN on 
        # job and company tables and using subquery for selecting jobs user has applied for from the apply table 
        cur.execute("SELECT job.job_title, job.job_type, company.name, company.location, job.job_salary, \
        job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE job.job_id in (SELECT job_id FROM apply WHERE \
        jobseeker_id = {})".format(user))
        applied_jobs = cur.fetchall()
        cur.close()
        cur2 = mysql.connection.cursor()
        # selecting all the profile details of the user from profile table to display in the My Profile section
        cur2.execute("SELECT * FROM profile WHERE jobseeker_id = {}".format(user))
        profile_details = cur2.fetchall()
        if profile_details:
            profile_details = profile_details[-1]
        # selecting the resume details of the user from resume table
        cur2.execute("SELECT * FROM resume WHERE jobseeker_id = {}".format(user))
        resume_details = cur2.fetchall()
        if resume_details:
            resume_details = resume_details[-1]
        cur2.close()
        return render_template('profile.html', applied_jobs = applied_jobs, profile_details = profile_details, resume_details = resume_details)
    else:
        return redirect(url_for('login'))


# creating route for user manage profile
@app.route('/manageprofile', methods = ['GET', 'POST'])
def manageprofile():
    if "user" in session:
        user = session['user']

        cur = mysql.connection.cursor()
        # selecting all profile details for the logged in user
        exist = cur.execute("SELECT * FROM profile WHERE jobseeker_id = {}".format(user))
        profile_data = cur.fetchall()
        cur.close()
        if request.method == 'POST':
            profile = request.form
            college = profile['college']
            dept = profile['dept']
            education = profile['education']
            filename = profile['resume']
            cur = mysql.connection.cursor()
            # selecting all profile details for the logged in user
            exist = cur.execute("SELECT * FROM profile WHERE jobseeker_id = {}".format(user))
            if exist > 0:
                # If the profile entry for user exists, then update the profile details in the profile table for that entry using UPDATE clause
                cur.execute("UPDATE profile SET college = (%s), department = (%s), education = (%s) WHERE jobseeker_id = (%s)", (college, dept, education, user))
                mysql.connection.commit()
            else:
                # If the profile entry for that user doesnt exist in the profile table, then insert a record for profile details of that user
                cur.execute("INSERT INTO profile(college, department, education, jobseeker_id) VALUES (%s, %s, %s, %s)", (college, dept, education, user))
                mysql.connection.commit()
            cur.close()

            cur2 = mysql.connection.cursor()
            # selecting resume details of the user that is logged in
            res = cur2.execute("SELECT * FROM resume WHERE resume_id = {}".format(user))
            if res > 0:
                # if the resume entry exists for that user, then update the resume filename for the entry
                cur2.execute("UPDATE resume SET filename = (%s) WHERE resume_id = (%s)", (filename, user))
                mysql.connection.commit()
            else:
                # if the resume entry doesnt exist, then insert a new entry in resume table for that user with the filename
                cur2.execute("INSERT INTO resume(filename, jobseeker_id) VALUES (%s, %s)", (filename, user))
                mysql.connection.commit()
            cur2.close()
            return redirect(url_for('profile'))
        
        return render_template('manageprofile.html', profile_data = profile_data)
    else:
        return redirect(url_for('login'))


# creating route for jobs shown to user
@app.route('/jobs', methods = ['GET', 'POST'])
def jobs():
    if "user" in session:
        if request.method == 'POST':
            searchjob = request.form
            keyword = searchjob['keyword']
            location = searchjob['location']
            cur = mysql.connection.cursor() 
            # if only keyword is entered in the job search, then select those jobs where the keyword matches the job details
            # by using LIKE clause and inner join on jobs and corresponding companies 
            if keyword and (not location):
                count_search = cur.execute("SELECT job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')".format(keyword, keyword, keyword))
            # if only location is entered in the job search, then select those jobs where the keyword matches the company location
            # by using LIKE clause and inner join on jobs and corresponding companies
            elif location and (not keyword):
                count_search = cur.execute("SELECT job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE (company.location LIKE '%{}%')".format(location))
            # if keyword and location are entered in the job search, then select those jobs where the keyword matches the job details
            # and company location by using LIKE clause and inner join on jobs and corresponding companies
            elif location and keyword:
                count_search = cur.execute("SELECT job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id WHERE ((job.job_title LIKE '%{}%') OR (job.job_type LIKE '%{}%') OR (job.job_description LIKE '%{}%')) AND (company.location LIKE '%{}%')".format(keyword, keyword, keyword, location))
            else:
                count_search = 0

            jobsearch = cur.fetchall()
            return render_template('jobsearch.html', jobsearch = jobsearch)

        cur = mysql.connection.cursor()
        # display all jobs and their details by selecting all jobs of companies using inner join on job and company
        count_jobs = cur.execute("SELECT job.job_title, job.job_type, company.name, company.location, job.job_salary, job.job_description, job.job_id FROM job INNER JOIN company ON job.company_id = company.company_id")
       
        alljobs = cur.fetchall()
        return render_template('jobs.html', alljobs = alljobs)
    else:
        return redirect(url_for('login'))


# creating route for user jobsearch
@app.route('/jobsearch')
def jobsearch():
    if "user" in session:
        return render_template('jobsearch.html')
    else:
        return redirect(url_for('login'))


# creating route for applying to a job
@app.route('/apply', methods = ['GET', 'POST'])
def apply():
    if "user" in session:
        user = session['user']
        if request.method == 'POST':
            apply = request.form
            jobid = apply['j_id']
            cur = mysql.connection.cursor()
            # select all the jobs the user has applied by using the apply relation table
            applied = cur.execute("SELECT * FROM apply WHERE (jobseeker_id, job_id) = ({}, {})".format(user, jobid))
            if applied == 0:
                # if the user has not applied for that job, then insert a record for the user in the apply table for that job
                cur.execute("INSERT INTO apply VALUES ({}, {})".format(user, jobid))
                mysql.connection.commit()
            else:
                isres = cur.execute("SELECT * FROM result WHERE (jobseeker_id, job_id) = ({}, {})".format(user, jobid))
                if isres == 0:
                    warnig = "You have already applied for this job!!"
                    flash(f'{warnig}', category='warning')
                else:
                    warnig = "Your result has already been declared for this job!!"
                    flash(f'{warnig}', category='warning')
        return redirect(url_for('jobs'))       
    else:
        return redirect(url_for('login'))


# creating route for showing interviews scheduled for a user
@app.route('/interviews')
def interviews():   
    if "user" in session:
        user = session['user']
        cur = mysql.connection.cursor()
        # select all the interview details for those jobs that the user has applied for by using inner join on apply and interview's job_id
        check_apply = cur.execute('SELECT * FROM apply INNER JOIN interview ON (apply.jobseeker_id, apply.job_id) = (interview.jobseeker_id, interview.job_id) WHERE interview.jobseeker_id = {};'.format(user))
        if check_apply > 0:
            # select the interview details, its corresponding job and company details by using inner join on job, company and interview
            # and using subquery to show interview schedules for only those jobs that the jobseeker has applied for
            interview = cur.execute("SELECT interview.jobseeker_id, job.job_title, company.name, interview.date, interview.time FROM \
            job INNER JOIN company ON job.company_id = company.company_id INNER JOIN interview ON interview.job_id = job.job_id WHERE interview.jobseeker_id = {} AND \
            interview.job_id IN (SELECT apply.job_id FROM apply INNER JOIN interview ON (apply.jobseeker_id, apply.job_id) = (interview.jobseeker_id, interview.job_id) WHERE interview.jobseeker_id = {});".format(user, user))
            if interview > 0:
                schedule = cur.fetchall()
            else:
                schedule = None
        else:
            schedule = None
        return render_template('interview.html', schedule=schedule)
    else:
        return redirect(url_for('login'))


# creating route for showing results of a user for jobs he or she interviewed
@app.route('/results')
def results():
    if "user" in session:
        user = session['user']
        cur = mysql.connection.cursor()
        # select all the results for those jobs that the user has applied for by using inner join on apply and result's job_id
        chk_apply = cur.execute('SELECT * FROM apply INNER JOIN result ON (apply.jobseeker_id, apply.job_id) = (result.jobseeker_id, result.job_id) WHERE result.jobseeker_id = {};'.format(user))
        if chk_apply > 0:
            # select the result status of the job of a company  by using inner join on job, company and result
            # and using subquery to show results for only those jobs that the jobseeker has applied for 
            r = cur.execute("SELECT result.jobseeker_id, job.job_title, company.name, company.location, result.status FROM \
            job INNER JOIN company ON job.company_id = company.company_id INNER JOIN result ON result.job_id = job.job_id WHERE result.jobseeker_id = {} AND \
            result.job_id IN (SELECT apply.job_id FROM apply INNER JOIN result ON (apply.jobseeker_id, apply.job_id) = (result.jobseeker_id, result.job_id) WHERE result.jobseeker_id = {});".format(user, user))
            if r > 0:   
                res = cur.fetchall()
            else:
                res = None
        else:
            res = None
        return render_template('results.html', res = res)
    else:
        return redirect(url_for('login'))     


# creating route for account summary of a user
@app.route('/account')
def account():
    if "user" in session:
        user = session["user"]
        cur = mysql.connection.cursor()
        # displaying all jobseeker details by selecting it from jobseeker table
        cur.execute('SELECT * FROM jobseeker WHERE jobseeker.jobseeker_id = {}'.format(user))
        acc = cur.fetchall()
        # displaying the number of jobs the jobseeker has applied for by using GROUP BY and HAVING clause 
        # along with aggregate function count()
        a = cur.execute('SELECT count(job_id) FROM apply GROUP BY jobseeker_id HAVING jobseeker_id  = {};'.format(user))
        if a > 0:
            apply = cur.fetchall()
            apply = apply[0][0]
        else:
            apply = 0
        # displaying the number of results declared for jobs that the jobseeker has applied for by using GROUP BY and HAVING clause 
        # along with aggregate function count()
        r = cur.execute('SELECT count(job_id) FROM result GROUP BY jobseeker_id HAVING jobseeker_id = {};'.format(user))
        if r > 0:
            res = cur.fetchall()
            res = res[0][0]
        else:
            res = 0
        # displaying the number of interviews scheduled for jobs that the jobseeker has applied for by using GROUP BY and HAVING clause 
        # along with aggregate function count()
        i = cur.execute('SELECT count(job_id) FROM interview GROUP BY jobseeker_id HAVING jobseeker_id = {};'.format(user))
        if i > 0:
            interview = cur.fetchall()
            interview = interview[0][0]
        else:
            interview = 0
        return render_template('account.html', acc = acc, apply = apply, res = res, interview = interview)
    else:
        return redirect(url_for("login"))


# creating route for logging out user
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# creating route for logging out admin
@app.route('/admin_logout')
def admin_logout():
    session.pop("admin_user", None)
    return redirect(url_for("admin_login"))



if __name__ == "__main__":
    app.run(debug = True)
