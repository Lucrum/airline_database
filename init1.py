
import random

import pymysql
import werkzeug.exceptions
from pymysql import cursors
from flask import Flask, render_template, request, session, url_for, redirect
import search
import hashlib
import datetime
from datetime import datetime

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

# HOMEPAGES

@app.route('/chome')
def chome():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s'
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

    query = 'SELECT * FROM ticket WHERE customer_email = %s'
    cursor.execute(query, username)
    future_customer_tickets = cursor.fetchall()

    if (future_customer_tickets):
        for ticket in future_customer_tickets:
            to_append = [ticket['ticket_id'], ticket['flight_number']]

            today = datetime.today()

            flight_info = []

            flight_status = "Unknown"

            for flight in future_customer_flights:
                if (flight['flight_number'] == ticket['flight_number']):
                    flight_info += [flight['departure_airport_code'],
                                  flight['departure_date_time'][0:10],
                                  flight['arrival_airport_code'],
                                  flight['arrival_date_time'][0:10]]
                    flight_status = flight['flight_status']


            arrive_day = datetime.strptime(flight_info[3], '%Y-%m-%d')

            if today > arrive_day:
                flight_status = "Complete"

            to_append.append(flight_status)
            to_append += flight_info


            to_append += [ticket['airline_name'], ticket['travel_class'],
                          "$"+str(ticket['sold_price'])]


            filtered_customer_flights.append(to_append)


    # spending data




    cursor.close()

    # check for errors
    try:
        fail_to_cancel = request.args['cancel_error']
    except werkzeug.exceptions.BadRequestKeyError:
        fail_to_cancel = None

    try:
        cancel_success = request.args['cancel_success']
    except werkzeug.exceptions.BadRequestKeyError:
        cancel_success = None

    return render_template('chome.html', username=name, public_flights=filtered_public_data,
                           cust_flights=filtered_customer_flights, fail_cancel=fail_to_cancel,
                           cancel_success=cancel_success)

@app.route('/shome')
def shome():
    username = session['username']
    # public flight data

    filtered_public_data = search.getPublicData()

    return render_template('shome.html', username=username, public_flights=filtered_public_data)


# BOOKING/CANCELING TICKETS

@app.route('/buy_ticket_redirect')
def buy_ticket_redirect():
    step = request.args.get('step')
    if (step == "listings"):
        future_flights = search.getAllFutureFlights()


        # packaged and formatted (in this order)
        packaged_data = []
        for flight in future_flights:

            flight_no = flight[0]
            flight_stat = flight[1]
            dept_date = flight[2][0:10]
            arr_date = flight[7][0:10]
            airline_name = flight[3]
            dept_code = flight[5]
            arr_code = flight[6]
            price = flight[8]

            packaged_data.append([flight_no, flight_stat, dept_date, arr_date,
                                  airline_name, dept_code, arr_code, price])

        return render_template('flight_listings.html', data=packaged_data)

    else:
        flight_info = request.args.getlist('flight_info')
        flight_number = flight_info[0]
        price = flight_info[7]
        dept = flight_info[5]
        arr = flight_info[6]


        return render_template('book_ticket_form.html', flight_number=flight_number, price=price,
                               departure=dept, arrival=arr)


@app.route('/buy_ticket', methods=['post'])
def buy_ticket():
    username = session['username']
    cursor = conn.cursor()

    flight_number = request.args.get('flight_number')
    price = request.args.get('price')

    # get departure date
    query = 'SELECT departure_date_time FROM flight WHERE flight_number = %s'
    cursor.execute(query, flight_number)
    departure = cursor.fetchone()['departure_date_time']

    # get airline hosting the flight
    query = 'SELECT airline_name FROM flight WHERE flight_number = %s'
    cursor.execute(query, flight_number)
    airline_name = cursor.fetchone()['airline_name']


    travel_class = request.form['class']

    purchase_date = datetime.now()
    dt_string = purchase_date.strftime("%Y/%m/%d %H:%M:%S")


    card = request.form['card_type']
    name = request.form['name_card']
    exp = request.form['expiry']

    exp_year = exp[0:4]
    exp_month = exp[5:7]

    mod_expiry = exp_year + '-' + exp_month + '-01'

    uniqueID = False
    ticket_id = 0
    # check for dupe id
    while(not uniqueID):
        ticket_id = random.randint(0, 10000000)
        query = 'SELECT ticket_id FROM ticket WHERE ticket_id = %s'
        cursor.execute(query, ticket_id)
        data = cursor.fetchone()
        if (data):
            pass
        else:
            uniqueID = True

    info = (ticket_id, username, travel_class, airline_name, flight_number,
                           departure, float(price), dt_string, card, name, mod_expiry)


    query = 'INSERT INTO ticket VALUES(%s, %s, %s, %s, %s, %s,' \
            '%s, %s, %s, %s, %s)'
    cursor.execute(query, info)
    conn.commit()
    cursor.close()
    return redirect(url_for('chome'))

@app.route('/cancel_flight', methods=["post"])
def cancel_flight():
    email = session['username']
    cursor = conn.cursor()
    ticket_id = request.form['selected_ticket']

    print("Attempting to cancel ticket " + ticket_id)

    query = 'SELECT departure_date_time FROM flight WHERE flight_number IN' \
            '(SELECT flight_number FROM ticket WHERE ticket_id = %s)'
    cursor.execute(query, ticket_id)

    departure = cursor.fetchone()['departure_date_time']

    now = datetime.now()

    departure_datetime = datetime.strptime(departure, '%Y-%m-%d')

    time_diff = departure_datetime - now
    time_diff_hours = divmod(time_diff.total_seconds(), 3600)[0]

    print("Flight in " + str(time_diff_hours))


    if (time_diff_hours < 24.0):
        return redirect(url_for('chome', cancel_error="You may not cancel a ticket less than 24 hours prior "
                                                      "to takeoff."))



    # ensure ticket belongs to logged in customer
    query = 'SELECT customer_email FROM ticket WHERE ticket_id = %s'
    cursor.execute(query, int(ticket_id))
    ticket_email = cursor.fetchone()

    if (email == ticket_email['customer_email']):
        pass
    else:
        return redirect(url_for('chome', cancel_error="Unable to cancel ticket!"))

    query = 'DELETE FROM ticket WHERE ticket_id = %s'
    cursor.execute(query, ticket_id)
    conn.commit()
    return redirect(url_for('chome', cancel_success="Ticket " + ticket_id + " canceled successfully."))

# RATINGS

@app.route('/ratings')
def ratings():
    cursor = conn.cursor()
    flight_number = request.args.get('flight_number')
    query = 'SELECT * FROM ratings WHERE flight_number = %s'


    try:
        post_err = request.args.get('post_err')
    except werkzeug.exceptions.BadRequestKeyError:
        post_err = None

    try:
        delete_err = request.args.get('delete_message')
    except werkzeug.exceptions.BadRequestKeyError:
        delete_err = None

    cursor.execute(query, flight_number)

    rating_data = cursor.fetchall()

    print(rating_data)

    compiled_data = []

    for entry in rating_data:
        compiled_data.append([entry['customer_email'],
                             entry['rating'],
                             entry['comments']])


    return render_template('ratings.html', data=compiled_data, flight_number=flight_number,
                           post_err=post_err, delete_message=delete_err)

@app.route('/post_rating', methods=['post'])
def post_rating():
    username = session['username']

    cursor = conn.cursor()

    # check for pre existing comment

    query = 'SELECT * FROM ratings WHERE customer_email = %s'
    cursor.execute(query, username)
    preexisting_rating = cursor.fetchone()
    flight_number = request.form['flight_number']

    if (preexisting_rating):
        print("Pre existing comment!")
        return redirect(url_for('ratings', flight_number=flight_number,
                                post_err="You may only have one rating at a time. Please " \
                                "delete your comment first."))

    comment = request.form['comment']

    rating = request.form['score']




    query = 'INSERT INTO ratings VALUES (%s, %s, %s, %s)'
    cursor.execute(query, (flight_number, username,
                           rating, comment))

    conn.commit()


    return redirect(url_for('ratings', flight_number=flight_number))

@app.route('/delete_rating', methods=['post'])
def delete_rating():
    username = session['username']
    flight_number = request.form['flight_number']

    cursor = conn.cursor()

    query = 'SELECT * FROM ratings WHERE customer_email = %s'
    cursor.execute(query, username)
    preexisting_rating = cursor.fetchone()

    if (preexisting_rating):

        query = 'DELETE FROM ratings WHERE customer_email = %s'
        cursor.execute(query, username)
        conn.commit()
        return redirect(url_for('ratings', flight_number=flight_number, delete_message="Comment deleted."))

    else:
        return redirect(url_for('ratings', flight_number=flight_number, delete_message="No comment to delete."))




# STAFF FLIGHT MANAGEMENT

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
        cursor.close()
        return render_template('create_flight.html', error="Duplicate flight number")
    else:
        query = 'INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (flight_no, flight_status, dept_date, airline,
                               airplane, dept_code, arriv_code, arri_date, base_price))
        conn.commit()
        cursor.close()
        return render_template('create_flight.html', success="Flight" + flight_no + "created!")



# LOGIN

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

    cursor.close()
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
        cursor.close()
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
        cursor.close()
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





if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)