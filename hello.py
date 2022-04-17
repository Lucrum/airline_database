import pymysql
from pymysql import cursors
from flask import Flask, render_template, request, session, url_for, redirect

app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airline',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

app.secret_key = "secret"

@app.route('/')
def landing():
    return render_template('login.html')

@app.route('/home')
def home():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT airline_name FROM airline'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=username, posts=data)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

@app.route('/loginAuth', methods=['GET','POST'])
def loginAuth():
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s and s_password = %s'
    cursor.execute(query, (username, password))

    data = cursor.fetchone()

    cursor.close()
    if(data):
        session['username'] = username
        return redirect(url_for('home'))
    else:
        error = "Invalid username or password"
        return render_template('login.html', error=error)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registerAuth', methods=['GET','POST'])
def registerAuth():
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()

    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))

    data = cursor.fetchone()

    if(data):
        error = "This user already exists"
        cursor.close()
        return render_template('register.html', error=error)
    else:
        ins = 'INSERT INTO airline_staff VALUES (%s, %s)'
        cursor.execute(ins, (username, password))

        conn.commit()
        cursor.close()
        succeed = "Success!"
        return render_template('index.html', success=succeed)

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