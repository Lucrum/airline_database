import pymysql
from pymysql import cursors
from flask import Flask, render_template, request, session, url_for, redirect
import search
import hashlib

app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                       port=8889,
                       user='root',
                       password='root',
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
    dept_datetime = request.form['departure_date']
    arri_datetime = request.form['arrival_date']
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
        query2 = 'INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query2, (flight_no, flight_status, dept_datetime, airline,
                               airplane, dept_code, arriv_code, arri_datetime, base_price))
        cursor.close()
        return render_template('create_flight.html', success="Flight " + flight_no + " has been created!")


@app.route('/change_status_of_flight')
def change_status_of_flight():
    return render_template('change_status.html')

@app.route("/changeStatus", methods=['post'])
def changeStatus():

    cursor = conn.cursor()
    flight_num = request.form['flight_number']
    flight_status = request.form['flight_status']

    query = 'SELECT * FROM flight WHERE flight_number = %s'
    cursor.execute(query, flight_num)
    flight_exist = cursor.fetchone()
    if (flight_exist):
        query2 = 'UPDATE flight SET flight_status  = %s WHERE flight_number = %s'
        cursor.execute(query2, (flight_status, flight_num))
        cursor.close()
        return render_template('change_status.html', success="Status of " + flight_num + " has been changed!")
    else:
        return render_template('change_status.html', error="Invalid flight number!")

@app.route('/add_airplane')
def add_airplane():
    cursor = conn.cursor()
    query3 = 'SELECT airline_name FROM airline'
    cursor.execute(query3)
    airline_list = cursor.fetchall()
    cursor.close()
    return render_template('add_plane.html', airline_list=airline_list)

@app.route('/addPlane', methods=['post'])
def addPlane():

    cursor = conn.cursor()
    airplane_id = request.form['airplane_id']
    num_of_seats = request.form['num_of_seats']
    manu = request.form['manufacturer']
    age = request.form['age']
    airline = request.form['airline']

    query = 'SELECT * FROM airplane WHERE airplane_id = %s'
    cursor.execute(query, airplane_id)
    dup_plane = cursor.fetchone()

    if (dup_plane):
        return render_template('add_plane.html', error="This airplane already exists!")
    else:
        query2 = 'INSERT INTO airplane VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(query2, (airplane_id, num_of_seats, manu, age, airline))
        query1 = 'SELECT * FROM airplane WHERE airline_name = %s'
        cursor.execute(query1, airline)
        data = cursor.fetchall()
        cursor.close()
        filtered_data = []
        for elem in data:
            filtered_data.append([elem['airplane_id'], elem['num_of_seats'],
                                  elem['manufacturer'], elem['age'], elem['airline_name']])
        cursor.close()
        return render_template('add_plane_confirmation.html', airplanes=filtered_data)

@app.route('/add_airport')
def add_airport():
    return render_template('add_new_airport.html')

@app.route("/addAirport", methods=['post'])
def addAirport():

    cursor = conn.cursor()
    airport_code = request.form['airport_code']
    airport_name = request.form['airport_name']
    country = request.form['country']
    city = request.form['city']
    type = request.form['type']

    query = 'SELECT * FROM airport WHERE airport_code = %s'
    cursor.execute(query, airport_code)
    airport_exist = cursor.fetchone()
    if (airport_exist):
        return render_template('add_new_airport.html', error="This airport already exists!")
    else:
        query2 = 'INSERT INTO airport VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(query2, (airport_code, airport_name, country, city, type))
        cursor.close()
        return render_template('add_new_airport.html', success="Airport " + airport_code + " has been added!")

@app.route('/view_report')
def view_report():
    return render_template('view_report.html')

@app.route("/viewReport", methods=['post'])
def viewReport():

    cursor = conn.cursor()
    last = request.form['last']


    if last == 'last_month':
        query1 = 'SELECT COUNT(*) as num_tickets_sold FROM ticket WHERE date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 MONTH)'
        cursor.execute(query1)
        result = cursor.fetchone()
    elif last == 'last_year':
        query2 = 'SELECT COUNT(*) as num_tickets_sold FROM ticket WHERE date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR)'
        cursor.execute(query2)
        result = cursor.fetchone()
    elif last == 'between':
        date1 = request.form['date1']
        date2 = request.form['date2']
        query3 = 'SELECT COUNT(*) as num_tickets_sold FROM ticket WHERE date(purchase_date_time) BETWEEN %s AND %s'
        cursor.execute(query3, (date1, date2))
        result = cursor.fetchone()
    else:
        return render_template('view_report_result.html', error='You must make a choice!')

    result_num = result['num_tickets_sold']

    query4 = 'SELECT MONTH(purchase_date_time) AS month FROM ticket'
    cursor.execute(query4)
    data = cursor.fetchall()
    months = []
    for each in data:
        months.append(each['month'])

    nums = []
    for i in months:
        query5 = 'SELECT COUNT(*) AS num FROM ticket WHERE MONTH(purchase_date_time) = %s'
        cursor.execute(query5, i)
        data2 = cursor.fetchone()
        nums.append(data2)

    cursor.close()

    return render_template('view_report_result.html', number=result_num, months=months, nums=nums)


@app.route('/view_top_des')
def view_top_des():
    return render_template('view_top_des.html')

@app.route("/viewDes", methods=['post'])
def viewDes():

    cursor = conn.cursor()
    last = request.form['last']

    if last == 'last_three_month':
        query1 = 'SELECT airport.city AS city, arrival_airport_code AS des_code,  COUNT(ticket_id) AS num_ticket FROM ticket, \
        flight, airport WHERE ticket.flight_number=flight.flight_number AND flight.arrival_airport_code=airport.airport_code \
        AND date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 3 MONTH) GROUP BY arrival_airport_code \
        ORDER BY num_ticket DESC LIMIT 3'
        cursor.execute(query1)
        data = cursor.fetchall()
    elif last == 'last_year':
        query2 = 'SELECT airport.city AS city, arrival_airport_code AS des_code,  COUNT(ticket_id) AS num_ticket FROM ticket, flight, \
        airport WHERE ticket.flight_number=flight.flight_number AND flight.arrival_airport_code=airport.airport_code AND \
        date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR) GROUP BY arrival_airport_code ORDER BY num_ticket DESC LIMIT 3'
        cursor.execute(query2)
        data = cursor.fetchall()
    else:
        return render_template('view_top_des.html', error="You must make a choice!")

    filtered_data = []
    for elem in data:
        filtered_data.append([elem['city'], elem['des_code'], elem['num_ticket']])
    cursor.close()
    return render_template('view_top_des_result.html', data=filtered_data)

@app.route('/view_revenue')
def view_revenue():
    cursor = conn.cursor()
    query1 = 'SELECT SUM(sold_price) as total_revenue_m FROM ticket WHERE date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 MONTH)'
    query2 = 'SELECT SUM(sold_price) as total_revenue_y FROM ticket WHERE date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR)'
    cursor.execute(query1)
    mdata = cursor.fetchone()
    cursor.execute(query2)
    ydata = cursor.fetchone()
    cursor.close()
    return render_template('view_revenue.html', mdata=mdata, ydata=ydata)

@app.route('/view_revenue_class')
def view_revenue_class():
    cursor = conn.cursor()
    query11 = "SELECT (CASE WHEN SUM(sold_price) is not null THEN SUM(sold_price) ELSE 0 END) as total_revenue_m\
     FROM ticket WHERE date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 MONTH) AND travel_class = 'First Class'"
    query12 = "SELECT (CASE WHEN SUM(sold_price) is not null THEN SUM(sold_price) ELSE 0 END) as total_revenue_m\
     FROM ticket WHERE date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 MONTH) AND travel_class = 'Business Class'"
    query13 = "SELECT (CASE WHEN SUM(sold_price) is not null THEN SUM(sold_price) ELSE 0 END) as total_revenue_m\
     FROM ticket WHERE date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 MONTH) AND travel_class = 'Economy Class'"
    query21 =  "SELECT (CASE WHEN SUM(sold_price) is not null THEN SUM(sold_price) ELSE 0 END) as total_revenue_y\
     FROM ticket WHERE date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR) AND travel_class= 'First Class'"
    query22 = "SELECT (CASE WHEN SUM(sold_price) is not null THEN SUM(sold_price) ELSE 0 END) as total_revenue_y\
     FROM ticket WHERE date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR) AND travel_class= 'Business Class'"
    query23 = "SELECT (CASE WHEN SUM(sold_price) is not null THEN SUM(sold_price) ELSE 0 END) as total_revenue_y\
     FROM ticket WHERE date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR) AND travel_class= 'Economy Class'"
    cursor.execute(query11)
    mdata1 = cursor.fetchone()
    cursor.execute(query12)
    mdata2 = cursor.fetchone()
    cursor.execute(query13)
    mdata3 = cursor.fetchone()
    cursor.execute(query21)
    ydata1 = cursor.fetchone()
    cursor.execute(query22)
    ydata2 = cursor.fetchone()
    cursor.execute(query23)
    ydata3 = cursor.fetchone()

    cursor.close()
    return render_template('view_revenue_class.html', mdata1=mdata1, mdata2=mdata2, mdata3=mdata3,\
                           ydata1=ydata1, ydata2=ydata2, ydata3=ydata3)



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
        return render_template('customerlogin.html')

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
        return render_template('stafflogin.html')

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