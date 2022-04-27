import pymysql
from pymysql import cursors
from flask import Flask, render_template, request, session, url_for, redirect
import search

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


@app.route('/home')
def home():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, username)

    # public flight data
    full_info = cursor.fetchone()
    name = full_info['first_name'] + " " + full_info['last_name']

    filtered_public_data = search.getPublicData()
    print(filtered_public_data)

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

    return render_template('home.html', username=name, public_flights=filtered_public_data,
                           cust_flights = filtered_customer_flights)

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
    query = 'SELECT * FROM user WHERE username = %s and password = %s'
    cursor.execute(query, (username, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('stafflogin.html', error=error)

@app.route('/cloginAuth', methods=['GET', 'POST'])
def cloginAuth():
    #grabs information from the forms
    username = request.form['cusername']
    password = request.form['cpassword']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM customer WHERE email = %s and c_password = %s'
    cursor.execute(query, (username, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('customerlogin.html', error=error)


#Authenticates the register
@app.route('/cregisterAuth', methods=['GET', 'POST'])
def cregisterAuth():
    #grabs information from the forms
    username = request.form['cusername']
    password = request.form['cpassword']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM user WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('customerregister.html', error = error)
    else:
        ins = 'INSERT INTO user VALUES(%s, %s)'
        cursor.execute(ins, (username, password))
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
    print(dob)


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
        ins = 'INSERT INTO airline_staff VALUES (%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, airline_name, fname, lname, dob))
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