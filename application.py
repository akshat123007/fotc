import os
from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_session import Session 
import re
import logging
from csv import DictWriter
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from forms import LoginForm, RegistrationForm_po, ContactForm, RegistrationForm
import db_handler
from helpers import login_required 

# configure application
app = Flask(__name__)

# ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
  
# configure session to use filesystem instead of signed cookies
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
  
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    """Show homepage"""

    return render_template("/index.html")
    

@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """update the profile of the user"""

    if request.method == 'POST':
        uid = session["user_id"]

        if 'nameCh' in request.form:
            nname = request.form.get("nname")
            if not nname:
                    flash("You must enter a name!", 'danger')
                    return redirect('/update')

            # get confirmed name from user
            confirmName = request.form.get("confirmName")
            if not confirmName or confirmName != nname:
                    flash("Names do not match!", 'danger')
                    return redirect('/update')
            
            conn = db_handler.fypDB_Connect()
            db_handler.execute(conn=conn, query=f"UPDATE public.users SET fullname = '{nname}' "
                                                f"WHERE id = {uid};")
            db_handler.close(conn=conn)
            flash("Name updated successfully!", "success")
            return redirect("/")
                  
        if 'mailCh' in request.form:
            # get new mail id from user
            nmail=request.form.get("nmail") 
            if not nmail:
                flash("you must enter email!", 'danger')
                return redirect('/update')

            # get confirmed mail id from user
            confirmMail=request.form.get("confirmMail")
            if not confirmMail or confirmMail != nmail:
                flash("email ids do not match!", 'danger')
                return redirect('/update')

            conn = db_handler.fypDB_Connect()
            db_handler.execute(conn=conn, query=f"UPDATE public.users SET email = '{nmail}' "
                                                f"WHERE id = {uid};")
            db_handler.close(conn=conn)
            flash("Email updated successfully!", "success")
            return redirect("/")

    # user reached via GET method
    else:
        return render_template('/update.html')


@app.route("/register_po", methods=["GET", "POST"])
def register_po():
    """register new property owners"""
    
    conn = db_handler.fypDB_Connect()
    form = RegistrationForm_po()

    if request.method == 'POST':
        fullname = form.fullname.data
        username = form.username.data
        phone = form.phone.data
        email = form.email.data
        password = form.password.data
        cpass = form.confirm_password.data

        if password != cpass:
            flash("Passwords do not match", "danger")
            return redirect("/register_po")
        hashed_pass = generate_password_hash(password=password)

        acc = db_handler.fetch(conn=conn, query=f"SELECT * FROM public.users WHERE username = '{username}'")
        if acc:
            flash(f"Account already exists for {username}!", "danger")
            return redirect("/register_po")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!', 'danger')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email or not fullname:
            flash('Please fill the form!', 'info')
        else:
            db_handler.execute(conn=conn,
                                query=f"INSERT INTO public.users (fullname, username, "
                                f"phone, email, userpass) VALUES ('{fullname}', '{username}', "
                                f"'{phone}', '{email}', '{hashed_pass}');")
            flash("Account creation successfull!", "success")
            db_handler.close(conn=conn)
            flash("Please login to continue as a proprietor.", 'info')
            return redirect("/")

    else:
        return render_template('register_po.html', title='Register_po', form=form)

    
@app.route("/upload", methods=["GET", "POST"])
@login_required
def register():
    """upload features & images for accessibility"""
    
    conn = db_handler.fypDB_Connect()
    form = RegistrationForm()

    if request.method == 'POST':
        address = request.form.get('searchBox')
        lat = form.lat.data
        lon = form.lon.data
        Fullname = form.Fullname.data
        Featurename = form.Featurename.data
        if not address or not lat or not lon or not Fullname or not Featurename:
            flash("Missing information! Please complete the form", 'danger')
            return redirect('/upload')
        file = form.File.data
        if file.filename == '':
            flash('No image selected for uploading', 'danger')
            return redirect('/upload')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            u_id = session["user_id"]
            if not u_id:
                flash("User has not been logged in!", "danger")
                return redirect("/login")

            db_handler.executeDictCursor(conn=conn,
                                        query="INSERT INTO public.features (property, latitude, longitude, fullname, featurename, images, u_id)"
                                        f"VALUES ('{address}', '{lat}', '{lon}', '{Fullname}', '{Featurename}', '{filename}', '{u_id}');")
            db_handler.close(conn)
            flash("Property features registered successfully!", 'success')
            return redirect('/')
            
        else:
            flash("Allowed image types are PNG, JPEG, JPG only!", 'danger')
            return redirect("/upload")

    else:
        return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log in user"""
    session.clear()
    
    form = LoginForm()
    conn = db_handler.fypDB_Connect()
    if request.method == 'POST':
        
        # Ensure username was submitted
        username = form.username.data
        if not username:
            flash("You must provide username!", 'danger')
            return redirect("/login")

        # Ensure password was submitted
        password = form.password.data
        if not password:
            flash("You must provide password!", 'danger')
            return redirect("/login")

        # Query database for username, return list of tuples
        rows = db_handler.fetch(conn=conn, query="SELECT * FROM public.users WHERE "
                                                f"username = '{username}';")
        
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][3], password): #userpass
            flash("Invalid username and/or password!", "danger")
            return redirect("/login")

        # Create session data for user
        session["logged_in"] = True
        session["user_id"] = rows[0][0] #id
        session["username"] = rows[0][2]  #username 

        # Redirect user to home page
        flash(f"Successfully logged in as {session['username']}!", 'success')
        return redirect("/")

    else:
        return render_template('login.html', form=form)



@app.route("/contact", methods=["GET", "POST"])
def contact():
    """contact form"""
    
    # init contact form
    form = ContactForm()

    # user reaches by post method
    if request.method == 'POST':
        name =  request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        # validating variables
        if not name or not email or not subject or not message:
            flash("Please fill the form!", "danger")
            return redirect("/contact")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!', 'danger')
            return redirect('/contact')

        # res stores the details of the contact form in a list
        field_names = ['NAME', 'EMAIL', 'SUBJECT', 'MESSAGE']
        res = {'NAME' : name, 'EMAIL': email, 'SUBJECT' : subject, 'MESSAGE': message}

        # write the list in a csv file
        with open('contactusMessages.csv', 'a') as f_in:
            dictwriter_object = DictWriter(f_in, fieldnames=field_names)
            dictwriter_object.writerow(res)
            f_in.close()
        logging.info("contactusMessages.csv updated")
        flash("Your request has been recieved. We will reach out to you soon.", "success")

        # redirect user to home
        return redirect('/')
    
    # user reaches via get method
    else:
        return render_template('contact.html', title='Contact us', form=form)


@app.route("/about")
def about():
    """diplay FoTc portfolio"""
    return render_template("/about.html")


@app.route("/logout")
@login_required
def logout():
    """Log out user"""
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('username', None)
    flash("You have logged out successfully!", "success")
    return redirect(url_for('index'))

@app.route("/account", methods=['POST', 'GET'])
@login_required
def account():
    """user profile actions"""

    if request.form == "POST":
        pass

    else:
        conn = db_handler.fypDB_Connect()
        o_id = session["user_id"]
        owner = db_handler.fetch(conn=conn,
                                query="SELECT fullname, email, phone FROM public.users"
                                      f" WHERE id = {o_id};")
        return render_template('account.html', owner=owner[0])


@app.route("/view_map")
def view_map():
    """view accessible maps for location"""

    return render_template('/view_map.html')

@app.route('/access', methods=['POST', 'GET'])
def access():
    conn = db_handler.fypDB_Connect()

    if request.method == 'POST':
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        if not lat or not lon:
            flash("Missing place!", "danger")
            return render_template('/access.html', msg="Invalid or missing place!")

        rows = db_handler.fetch(conn=conn,
                                query=f"SELECT * FROM public.features WHERE latitude = '{lat}'"
                                      f"AND longitude = '{lon}';")
        if not rows:
            flash("Missing place!", "danger")
            return render_template('/access.html', msg="We currently don't have records for this place. Sorry for the inconvenience!")
        
        name = rows[0][4]
        address = rows[0][1]
        features = []
        for row in rows:
            item = []
            item.append(row[5])
            item.append(row[6])
            features.append(item)
        
        o_id = rows[0][7]
        owner = db_handler.fetch(conn=conn,
                                query="SELECT fullname, email, phone FROM public.users"
                                      f" WHERE id = {o_id};")
        
        db_handler.close(conn=conn)
        if not owner:
            flash("Insufficient business details!", "danger")
            return redirect("/access")

        return render_template("/access.html", msg="", name=name, address=address, features=features, owner=owner[0])

    else:
        return render_template('/access.html', msg="Search for a place to check its accessiblity features.")

@app.route('/display/<filename>')
def display_image(filename):
    
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route("/directions")
def get_dir():
    """get the directions from one location to another"""
    
    return render_template("/directions.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html", message=e)

for code in default_exceptions:
    app.errorhandler(code)(errorhandler)