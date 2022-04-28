import pymysql
from pymysql import cursors
from flask import Flask, render_template, request, session, url_for, redirect
import search
import hashlib

app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='AirSystem',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

app.secret_key = "secret"

@app.route('/')
def landing():
    filtered_data = search.getPublicData()
    if filtered_data:
        no_search = False
    else:
        no_search = True

    return render_template('landing_page.html', flights=filtered_data, err=no_search)


@app.route('/psearch/<prev_page>', methods=['POST'])
def psearch(prev_page):
    cursor = conn.cursor()
    search_tags = request.form['psearchf']
    if search_tags:
        query = 'SELECT * FROM flight WHERE airline_name = %s OR departure_airport_code = %s OR arrival_airport_code = %s ' \
                'OR departure_date_time = %s OR arrival_date_time = %s'
        cursor.execute(query, (search_tags, search_tags, search_tags, search_tags, search_tags))
        data = cursor.fetchall()


        filtered_data = []
        for elem in data:
            filtered_data.append([elem['airline_name'], elem['flight_number'],
                                  elem['departure_date_time'][0:10], elem['arrival_date_time'][0:10]])


        cursor.close()
        return render_template(prev_page, field=search_tags, data=filtered_data)
    else:
        filtered_data = search.getPublicData()
        return render_template('landing_page.html', flights=filtered_data, err = True)


@app.route('/chome')
def chome():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s'
    print(username)
    cursor.execute(query, username)

    # public flight data
    full_info = cursor.fetchone()
    name = full_info['first_name'] + " " + full_info['last_name']

    filtered_public_data = search.getPublicData()


    # customer's flight data
    query = 'SELECT * FROM flight WHERE flight_number IN ' \
            '(SELECT flight_number FROM ticket WHERE customer_email = %s)'

    cursor.execute(query, username)

    future_customer_flights = cursor.fetchall()
    filtered_customer_flights = []
    if(future_customer_flights):
        for elem in future_customer_flights:
            filtered_customer_flights.append([elem['airline_name'], elem['flight_number'],
                                  elem['departure_date_time'][0:10], elem['arrival_date_time'][0:10]])

    cursor.close()

    return render_template('chome.html', username=name, public_flights=filtered_public_data,
                           cust_flights=filtered_customer_flights)

@app.route('/shome')
def shome():
    username = session['username']
    cursor = conn.cursor()
    # public flight data

    filtered_public_data = search.getPublicData()

    return render_template('shome.html', username=username, public_flights=filtered_public_data)

@app.route('/create_new_flight')
def create_new_flight():
    return render_template('create_flight.html')

@app.route("/newFlight", methods=['post'])
def newFlight():

    cursor = conn.cursor()
    flight_no = request.form['flight_number']
    flight_status = request.form['flight_status']
    dept_date = request.form['departure_date']
    arri_date = request.form['arrival_date']
    airline = request.form['airline']
    airplane = request.form['airplane_id']
    dept_code = request.form['dept_code']
    arriv_code = request.form['arriv_code']
    base_price = request.form['base_price']

    # checks if duplicate flight number
    query = 'SELECT * FROM flight WHERE flight_number = %s'
    cursor.execute(query, flight_no)
    dup_flight = cursor.fetchone()
    if (dup_flight):
        return render_template('create_flight.html', error="Duplicate flight number")
    else:
        query = 'INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (flight_no, flight_status, dept_date, airline,
                               airplane, dept_code, arriv_code, arri_date, base_price))
        return render_template('create_flight.html', success="Flight" + flight_no + "created!")


@app.route('/logout')
def logout():
    session.pop('username')
    return render_template('customerlogin.html')

@app.route('/loginRedirect/<acc_type>')
def loginRedirect(acc_type):

    if (acc_type == "customer"):
        return(render_template('customerlogin.html'))
    elif(acc_type == "staff"):
        return (render_template('stafflogin.html'))
    else:
        redirect(url_for('landing'))

@app.route('/registerRedirect/<acc_type>')
def registerRedirect(acc_type):
    if (acc_type == "customer"):
        return(render_template('customerregister.html'))
    elif(acc_type == "staff"):
        return (render_template('staffregister.html'))
    else:
        redirect(url_for('landing'))

#Authenticates the login
@app.route('/sloginAuth', methods=['GET', 'POST'])
def sloginAuth():
    #grabs information from the forms
    username = request.form['susername']
    password = request.form['spassword']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s and md5(s_password) = %s'
    cursor.execute(query, (username, hashlib.md5(password.encode()).hexdigest()))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('shome'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('stafflogin.html', error=error)

@app.route('/cloginAuth', methods=['GET', 'POST'])
def cloginAuth():
    #grabs information from the forms
    email = request.form['email']
    password = request.form['cpassword']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM customer WHERE email = %s and md5(c_password) = %s'
    cursor.execute(query, (email, (hashlib.md5(password.encode())).hexdigest()))
    #stores the results in a variable
    data = cursor.fetchone()

    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        # the username of customers is the email
        # it's possible we have 2 customers with the same name!!
        session['username'] = email
        return redirect(url_for('chome'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or email'
        return render_template('customerlogin.html', error=error)


#Authenticates the register
@app.route('/cregisterAuth', methods=['GET', 'POST'])
def cregisterAuth():
    #grabs information from the forms
    email = request.form['email']
    fname = request.form['fname']
    lname = request.form['lname']
    password = request.form['password']
    state = request.form['state']
    city = request.form['city']
    street = request.form['street']
    building = request.form['building']
    phone = request.form['phone']
    passnum = request.form['passnum']
    passexpi = request.form['passexpi']
    passcountry = request.form['passcountry']
    dob = request.form['dob']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM user WHERE username = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('customerregister.html', error = error)
    else:
        ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, fname, lname, password, state, city, street, building, phone, passnum,
                             passexpi, passcountry, dob))
        conn.commit()
        cursor.close()
        return render_template('index.html')

@app.route('/sregisterAuth', methods=['GET', 'POST'])
def sregisterAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    airline_name = request.form['airline_name']
    fname = request.form['fname']
    lname = request.form['lname']
    dob = request.form['dob']
    phone = request.form['phone']


    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('staffregister.html', error = error)
    else:
        ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, airline_name, fname, lname, dob))
        ins2 = 'INSERT INTO airline_staff_phone_number VALUES(%s, %s)'
        for each in phone:
            cursor.execute(ins2, (username, each))
        conn.commit()
        cursor.close()
        return render_template('index.html')

@app.route('/add_airline', methods=['GET','POST'])
def add_airline():
    username = session['username']
    cursor = conn.cursor();
    name = request.form['airlines']
    query = 'INSERT INTO airline (airline_name) VALUES (%s)'
    cursor.execute(query, (name))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))




if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)