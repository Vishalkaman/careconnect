from flask import Flask, render_template, request, redirect, url_for, session, send_file
from datetime import date
from datetime import datetime
import mysql.connector
from credentials import mysql_host, mysql_user, mysql_password
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from generate_bill import generate_receipt


app = Flask(__name__)

isLoggedIn = False
g_username = ''
backup_file = 'db.sql'


database_name = 'careconnect'

def get_number_of_entries(table):
    query = f"SELECT COUNT(*) FROM {table}"
    cursor.execute(query)
    count = cursor.fetchone()[0]
    return count

def get_user(username):
    if username:
        query = "SELECT p_id FROM person WHERE p_name = %s;"
        cursor = mysql.cursor()
        cursor.execute(query, (username,))
        p_id = cursor.fetchone()  # Use fetchone to get a single result
        return p_id[0] if p_id else None 
    return None

def get_carehome_by_id(c_id):
    query = "select c_name from orphanage_oldagehome where c_id = %s"
    cursor = mysql.cursor()
    cursor.execute(query, (c_id,))
    p_id = cursor.fetchone()  # Use fetchone to get a single result
    return p_id[0] if p_id else None 

# MySQL Configuration
app.config['MYSQL_HOST'] = mysql_host
app.config['MYSQL_USER'] = mysql_user
app.config['MYSQL_PASSWORD'] = mysql_password

mysql = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
)

try:
    cursor = mysql.cursor(buffered=True)
    cursor.execute("SHOW DATABASES LIKE '{}'".format(database_name))
    database_exists = cursor.fetchone()
    rows = cursor.fetchall()

    if database_exists:
        mysql.database = database_name

    else:
        cursor.execute("CREATE DATABASE {}".format(database_name))

        cursor.execute("USE {}".format(database_name))

        with open(backup_file, 'r') as backup:
            sql_statements = backup.read()
            cursor.execute(sql_statements, multi=True)

        mysql.database = database_name
        mysql.commit(database_name)


except Exception as e:
    print(e)

#=============== ROUTES ==========================
@app.route('/')
def home():
    # Sample query to fetch data from a table
    return render_template('index.html', isLoggedIn=isLoggedIn, username=g_username)


@app.route('/index.html')
def index():
    # Sample query to fetch data from a table
    return render_template('index.html', isLoggedIn=isLoggedIn, username=g_username)

@app.route('/aboutus.html')
def aboutus():
    # Sample query to fetch data from a table
    return render_template('aboutus.html')

@app.route('/community.html')
def community():
    # Sample query to fetch data from a table
        cursor = mysql.cursor()
        query = "SELECT c_id, c_name FROM orphanage_oldagehome"
        cursor.execute(query)
        carehomes = cursor.fetchall()


        if isLoggedIn:
            return render_template('community.html', username=session['username'], carehomes=carehomes)
        else:
            return render_template('community.html', carehomes=carehomes)

@app.route('/volunteer.html')
def volunteer():
    # Sample query to fetch data from a table
    return render_template('volunteer.html')

@app.route('/donate.html')
def donate():
    # Check if the user is logged in before allowing access to the donate page

        cursor = mysql.cursor()
        query = "SELECT c_id, c_name FROM orphanage_oldagehome"
        cursor.execute(query)
        carehomes = cursor.fetchall()


        if isLoggedIn:
            return render_template('donate.html', username=session['username'], carehomes=carehomes)
        else:
            return render_template('user reg form.html', carehomes=carehomes)

@app.route('/calendar.html')
def calendar():
    # Sample query to fetch data from a table
    return render_template('calendar.html')

@app.route('/register_login')
def register_login():
    # Sample query to fetch data from a table
    return render_template('user reg form.html')

@app.route('/donationcomplete')
def donationcomplete():
    # Sample query to fetch data from a table
    return render_template('donationcomplete.html')

@app.route('/bill.html')
def bill():
    pdf_path = 'bill.pdf'
    
    # Specify the filename for the downloaded file
    filename = 'bill.pdf'
    
    # Set response headers to indicate a file download
    return send_file(pdf_path, as_attachment=False)

@app.route('/contactus.html')
def contactus():
    # Sample query to fetch data from a table
    return render_template('contactus.html')

@app.route('/carehomes')
def carehomes():
        cursor = mysql.cursor()
        query = "SELECT c_name, c_location FROM orphanage_oldagehome"
        cursor.execute(query)
        rows = cursor.fetchall()
        return render_template('carehomes.html', data=rows)

@app.route('/donations')
def donations():
        cursor = mysql.cursor()
        query = "SELECT p_name, d_date, d_type, d_category, d_amount FROM person_donations d JOIN person p ON p.p_id = d.p_id; "
        cursor.execute(query)
        donations = cursor.fetchall()
        return render_template('donations.html', donations=donations)

@app.route('/volunteers_list.html')
def volunteers():
        cursor = mysql.cursor()
        query = "SELECT v_id, doj, visit_number, p_name, activity FROM volunteer v JOIN person p ON p.p_id = v.p_id; "
        cursor.execute(query)
        volunteers = cursor.fetchall()
        return render_template('volunteers_list.html', volunteers=volunteers)

@app.route('/initialize-database')
def initialize_database():
    try:
        # Check if the database already exists
        cursor = mysql.cursor(buffered=True)
        cursor.execute("SHOW DATABASES LIKE '{}'".format('careconnect'))
        database_exists = cursor.fetchone()
        rows = cursor.fetchall()

        if database_exists:
            return render_template('result.html', status="Error", message="Database already exists.")

        # Create the database
        cursor.execute("CREATE DATABASE {}".format('careconnect'))
        rows = cursor.fetchall()

        # Use the created database
        cursor.execute("USE {}".format('careconnect'))
        rows = cursor.fetchall()

        # Read the SQL statements from the backup file and execute them
        with open(backup_file, 'r') as backup:
            sql_statements = backup.read()
            cursor.execute(sql_statements, multi=True)

        mysql.commit()


        return render_template('result.html', status="Success", message="Database initialized successfully.")
    except Exception as e:
        return render_template('result.html', status="Error", message=str(e))

    


#=============== ROUTES ==========================



#=============== REGISTRATION ==========================


def add_user_to_database(p_id, p_name,p_age, password, confirm_password, address, contact):
    if password != confirm_password:
        return False, "Passwords do not match"

    user_data = (p_id, p_name,p_age,contact, address, password)
    insert_query = "INSERT INTO person (p_id, p_name, p_age,p_contact,p_address, password) VALUES (%s, %s, %s, %s, %s, %s)"

    cursor = mysql.cursor()
    cursor.execute(insert_query, user_data)
    mysql.commit()

    return True, None

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        p_id = request.form['p_id']
        p_name = request.form['p_name']
        p_age = request.form['p_age']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        address = request.form['address']
        contact = request.form['contact']

        success, error_message = add_user_to_database(p_id, p_name, p_age, password, confirm_password, address, contact)

        return render_template('index.html', success=success, error_message=error_message)


#=============== REGISTRATION ==========================


#=============== LOGIN ==========================

app.secret_key = 'your_secret_key'  # Change this to a secret and unique value


def authenticate_user(username, password):
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM person WHERE p_name=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    if user:
        return True
    else:
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    global isLoggedIn
    global g_username

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate_user(username, password):
            # If authentication is successful, store the user in the session
            isLoggedIn = True
            g_username = username

            session['username'] = username
            return redirect(url_for('index'))
        else:
            error_message = "Invalid username or password"
            return render_template('user reg form.html', error_message=error_message)

    return render_template('login.html')




#=============== LOGIN ==========================


#=============== MONETARY DONATION ==========================

def add_dontation(d_id, d_date, d_type, d_cat, d_amount, p_id, c_id):

    donation_data = (d_id, d_date, d_type, d_cat, d_amount, p_id, c_id)
    insert_query = "INSERT INTO person_donations (d_id, d_date, d_type, d_category, d_amount, p_id, c_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"

    cursor = mysql.cursor()
    cursor.execute(insert_query, donation_data)
    mysql.commit()

    c_name = get_carehome_by_id(c_id)
    generate_receipt(g_username, d_date, c_name, d_amount,  d_cat, "bill.pdf")

    return True, None



def get_donation_type(d_type):
    if d_type == "1":
        return "Education Support"
    elif d_type  == "2":
        return  "Food and Supplies"
    elif d_type  == "3":
        return  "Medical Support"
    elif d_type  == "4":
        return  "Clothing and Blankets"
    elif d_type  == "5":
        return  "Toys and Games"
    elif d_type  == "6":
        return  "Healthcare Support"


@app.route('/monetarydonation', methods=['POST'])
def monetarydonation():
    global g_username
    if request.method == 'POST':
        d_id = get_number_of_entries(f'person_donations') + 1
        d_date = datetime.date.today()
        d_type = "Monetary"
        d_cat = get_donation_type(request.form['d_cat'])
        d_amount = request.form['amount']
        p_id = get_user(g_username)
        c_id = request.form['carehome']

        success, error_message = add_dontation(d_id, str(d_date),d_type,  d_cat, float(d_amount), p_id, c_id)

        return render_template('dummypg.html', success=success, error_message=error_message)



#=============== MONETARY DONATION ==========================

#===============  FEEDBACK ==========================
def add_feedback(review_id, comment, orphanage_id, date):
    review_data = (review_id, comment, orphanage_id, date)
    insert_query = "INSERT INTO feedback (review_id, commentt, orphanage_id, review_date) VALUES (%s, %s, %s, %s)"

    cursor = mysql.cursor()
    cursor.execute(insert_query, review_data)
    mysql.commit()

    return True, None

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if request.method == 'POST':
        review_id = get_number_of_entries(f'feedback') + 1
        comment = request.form['comment']
        orphanage_id = request.form['carehome']

        success, error_message = add_feedback(review_id, comment, orphanage_id, datetime.date.today())
    
        return render_template('index.html', success=success, error_message=error_message)
#===============  FEEDBACK ==========================

#===============  VOLUNTEER ==========================
def get_activity(activity):
    if activity == "1":
        return "Painting"
    elif activity == "2":
        return "Teaching"
    elif activity == "3":
        return "Emotional Support"
    elif activity == "4":
        return "Games and Activities"
    elif activity == "5":
        return "Reading Sessions"
    elif activity == "6":
        return "Health Checkups"
    elif activity == "7":
        return "Arts and Crafts"

def add_volunteer_entry(v_id, DOJ, visit_number, p_id, activity):
    volunteer_data = (v_id, DOJ, visit_number, p_id, activity)
    insert_query = "INSERT INTO volunteer (v_id, DOJ, visit_number, p_id, activity) VALUES (%s, %s, %s, %s, %s)"

    cursor = mysql.cursor()
    cursor.execute(insert_query, volunteer_data)
    mysql.commit()

    return True, None

@app.route('/volunteer_submission', methods=['POST'])
def volunteer_submission():
    if request.method == 'POST':
        v_id = get_number_of_entries('volunteer') + 1
        DOJ = datetime.date.today()
        visit_number = request.form['visit_number']
        if get_user(g_username):
            p_id = get_user(g_username)
        else:
            return render_template('success_v.html', success=False, error_message=None)
        activity = get_activity(request.form['activity'])

        success, error_message = add_volunteer_entry(v_id, DOJ, visit_number, p_id, activity)

        if success:
            return render_template('success_v.html', success=True, error_message=None)
        else:
            return render_template('success_v.html', success=False, error_message=error_message)

#===============  VOLUNTEER ==========================


if __name__ == '__main__':
    app.run(debug=True)

#Extra line
# Change from moon