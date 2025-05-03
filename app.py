from datetime import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '<your_password>'
app.config['MYSQL_DB'] = '<db_name>'
mysql = MySQL(app)

app.secret_key = 'xyz'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '<email_id>' 
app.config['MAIL_PASSWORD'] = '<email_password>'
app.config['MAIL_DEBUG'] =True
mail = Mail(app)

@app.route('/')
def home():
    logged_in = session.get('logged_in', False)
    return render_template('home.html', logged_in=logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        contact_no = request.form['contact_no']
        if password != confirm_password:
            error = 'Passwords do not match'
            return render_template('signup.html', error=error)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password, email, contact_no) VALUES (%s, %s, %s, %s)", (username, password, email, contact_no))
        mysql.connection.commit()
        cur.close()
        msg = Message('Welcome to our Website',
                      sender='<email>',
                      recipients=[email])
        msg.body = 'Thank you for signing up for our website!'
        mail.send(msg)
        
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/ride')
def ride():
    if 'logged_in' in session:
        return render_template('ride.html')
    else:
        return redirect(url_for('login'))

@app.route('/rentals')
def rentals():
    if 'logged_in' in session:
        return render_template('rentals.html')
    else:
        return redirect(url_for('login'))

@app.route('/rentals/bus')
def bus_rental():
    if request.method == 'POST':
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        selected_model = request.form['model']
        return render_template('billing.html', date=date, start_time=start_time, end_time=end_time, model=selected_model)
    cur = mysql.connection.cursor()
    cur.execute("SELECT model_name FROM bus_models")
    bus_models = cur.fetchall()
    cur.close()
    return render_template('bus.html', available_models=bus_models)

@app.route('/rentals/bike')
def bike_rental():
    if request.method == 'POST':
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        selected_model = request.form['model']
        return render_template('billing.html', date=date, start_time=start_time, end_time=end_time, model=selected_model)
    cur = mysql.connection.cursor()
    cur.execute("SELECT model_name FROM bike_models")
    bike_models = cur.fetchall()
    cur.close()
    return render_template('bike.html', available_models=bike_models)

@app.route('/rentals/car', methods=['GET', 'POST'])
def car_rental():
    if request.method == 'POST':
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        selected_model = request.form['model']
        return render_template('billing.html', date=date, start_time=start_time, end_time=end_time, model=selected_model)
    cur = mysql.connection.cursor()
    cur.execute("SELECT model_name FROM car_models")
    car_models = cur.fetchall()
    cur.close()
    return render_template('car.html', available_models=car_models)

@app.route('/billing', methods=['POST'])
def billing():
    if request.method == 'POST':
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        model = request.form['model']
        price_per_hour = 25
        total_duration = (int(end_time) - int(start_time)) / 60
        total_price = total_duration * price_per_hour
        return render_template('billing.html', date=date, start_time=start_time, end_time=end_time,
                               model=model, total_duration=total_duration, price_per_hour=price_per_hour,
                               total_price=total_price)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/calculate_fare', methods=['POST'])
def calculate_fare():
    source = request.form['source']
    destination = request.form['destination']
    vehicle = request.form['vehicle']
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT distance FROM distances WHERE source=%s AND destination=%s", (source, destination))
    distance_data = cur.fetchone()
    if distance_data:
        distance = distance_data[0]
        fare_rate = {'auto': 50, 'bike': 30, 'car': 80}
        fare = fare_rate.get(vehicle, 0) * distance
        return jsonify({'fare': fare})
    else:
        return jsonify({'fare': None})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
