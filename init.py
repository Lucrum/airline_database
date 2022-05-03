from operator import imod
from turtle import home
from flask import Flask, render_template, request, session, redirect, url_for
from sql import Queries
import pymysql.cursors
import datetime

app = Flask(__name__)

conn = pymysql.connect(host='localhost', user ='root', password='root',
                        db='meetup', charset='utf8mb4', 
                        cursorclass=pymysql.cursors.DictCursor)

conn = pymysql.connect(host='localhost',
                       port=8880,
                       user='root',
                       password='root',
                       db='AirlineProject',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

app.secret_key = "encrypted"

#FlaskRoute for Customer Landing Page
@app.route('/')
def Landing():
    return render_template('CustomerLanding.html')

#FlaskRoute for Customer Comment Page
@app.route('/CustomerComment.html', methods = ['GET','POST'])
def newComment():
    if 'customer_email' not in session:
        return redirect(url_for('customer.cust_login'))

    status = None
    error = False

    if request.method == 'POST':

        email = session['customer_email']
        airline = request.form['Flight Airline']
        flight_num = request.form['Flight Number']
        rating = request.form['Rating']
        review = request.form['Review']
        depart = request.form['Departure Date']
        
        #Checking for Customer Email in the Purchased Ticket Table
        cursor = conn.cursor()
        cursor.execute(CustomerVerification, (email, airline, flight_num, depart))
        data = cursor.fetchone()
        print("Preparing...")

        if not data:
            error = True
            status = "No records found..."

        else:
            try:
                cursor.execute(CustomerRatings, (review, rating, email, airline, flight_num, depart))
                conn.commit()
                status = 'Thanks for your feedback =)'
                error = False
            except Exception as e:
                print(e)
                status = e
                error = True
        cursor.close()
        
    return render_template('/CustomerComment.html', status = status, error = error)


## Need to add bar chart/graph for the use case 
@app.route('/CustomerSpending.html', methods = ['GET','POST'])

def CustomerSpent():

    if 'customer_email' not in session:
        return redirect(url_for('#CUSTOMER LOGIN PAGE'))

    CustomerEmail = session['customer_email']
    
    cursor = conn.cursor()
    cursor.execute(SpentInYear, (CustomerEmail))
    year_spending = cursor.fetchone()['sum']
    print(year_spending)

    
    if request.method == 'POST':
        from_date = datetime.datetime.strptime(request.form['From'],'%m/%d/%Y').strftime('%Y-%m-%d')
        to_date = datetime.datetime.strptime(request.form['To'],'%m/%d/%Y').strftime('%Y-%m-%d')
        cursor.execute(SpentRangeMonthly, (CustomerEmail, from_date, to_date))

    else:
        cursor.execute(SpentOverSixMonths, (CustomerEmail))
    records = cursor.fetchall()
    cursor.close()
    return render_template('flight/customer_spending.html', flights = records, sum = year_spending)

#Flask Route for Customer View Flights

@app.route('/CustomerViewFlight.html', methods = ['GET','POST'])

def CustomerFlights():
    if 'customer_email' not in session:
        return redirect(url_for('#CustomerLogin'))

    cursor = conn.cursor()
    customer_email = session['customer_email']

    if request.method == 'POST':
        from_date = datetime.datetime.strptime(request.form['From'],'%m/%d/%Y').strftime('%Y-%m-%d')
        to_date = datetime.datetime.strptime(request.form['To'],'%m/%d/%Y').strftime('%Y-%m-%d')
        cursor.execute(CustomerFutureRange, (customer_email, from_date, to_date))
    else:
        cursor.execute(CustomerFutureFlights, (customer_email))
    records = cursor.fetchall()
    cursor.close()
    return render_template('flight/view_flight_table.html', flights = records)


#Flask Route for Customer Logout
@app.route('/CustomerLogout.html')
def logout():
    session.pop('customer_email')
    return render_template('CustomerLanding.html')

#Launch Session
if __name__ == "main":
    app.run('127.0.0.1', 5000, debug=True)






##########################################################################################################
#Also defined in /sql/Queries                                                                            
##########################################################################################################



#Customer Comment Query
#Dont have a purchase record table so need to take this data from the Ticket table (conflict between Departure time and Purchase Time)
CustomerVerification = 'SELECT * ' \
                  'FROM Ticket ' \
                  'WHERE customer_email = %s AND airline_name = %s ' \
                  'AND flight_number = %s AND CAST(flight_depart_datetime AS DATE) = %s'

#Submitting customer feedback to the Ratings Table
CustomerRatings = 'UPDATE Ratings ' \
                    'SET comments = %s, rating = %s ' \
                    'WHERE customer_email = %s AND airline_name = %s ' \
                    'AND flight_number = %s AND CAST(flight_depart_datetime AS DATE) = %s'

# Total Spent in Past Year
SpentInYear =       'SELECT SUM(sold_price) AS sum ' \
                    'FROM Ticket ' \
                    'WHERE customer_email = %s AND ticket_ID = ID ' \
                    'AND CAST(date_time AS date) >= DATE_ADD(CURDATE(), INTERVAL -1 YEAR) ' \
                    'AND CAST(date_time AS date) <= CURDATE()'

# Total Spent in Last 6 Months by Month (DEFAULT)
SpentOverSixMonths = 'SELECT YEAR(date_time) AS year, MONTHNAME(date_time) AS month, MONTH(date_time), SUM(sold_price) AS sum ' \
                     'FROM Ticket ' \
                     'WHERE customer_email = %s AND ticket_ID = ID ' \
                     'AND CAST(date_time AS date) >= DATE_ADD(CURDATE(), INTERVAL -6 MONTH) ' \
                     'AND CAST(date_time AS date) <= CURDATE() ' \
                     'GROUP BY YEAR(date_time), MONTH(date_time), MONTHNAME(date_time) ' \
                     'ORDER BY YEAR(date_time), MONTH(date_time) DESC'

# Total Spent in Range of Dates by Month
SpentRangeMonthly = 'SELECT YEAR(date_time) AS year, MONTHNAME(date_time) AS month, MONTH(date_time), SUM(sold_price) AS sum ' \
                    'FROM Purchases, Ticket ' \
                    'WHERE customer_email = %s AND ticket_ID = ID ' \
                    'AND CAST(date_time AS date) >= %s ' \
                    'AND CAST(date_time AS date) <= %s ' \
                    'GROUP BY YEAR(date_time), MONTH(date_time), MONTHNAME(date_time) ' \
                    'ORDER BY YEAR(date_time), MONTH(date_time) DESC'

#Future Customer Flights
CustomerFutureFlights = 'SELECT * ' \
                      'FROM Flight ' \
                      'WHERE (airline_name, flight_number) IN ' \
                      '(SELECT airline, flight_number ' \
                      'FROM Ticket' \
                      'WHERE id = ticket_id AND customer_email = %s ' \
                      'AND depart_datetime > CURRENT_TIMESTAMP)'

# Customer Flights (Range)
CustomerFutureRange = 'SELECT * ' \
                     'FROM Flight ' \
                     'WHERE (airline_name, flight_number) IN ' \
                     '(SELECT airline, flight_number ' \
                     'FROM Ticket' \
                     'WHERE id = ticket_id AND customer_email = %s ' \
                     'AND CAST(depart_datetime AS date) >= %s ' \
                     'AND CAST(depart_datetime AS date) <= %s)'