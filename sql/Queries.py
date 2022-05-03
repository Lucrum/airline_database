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