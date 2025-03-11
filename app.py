from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management


# Database connection for XAMPP
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # Default user for XAMPP
        password='',  # No password for XAMPP
        database='task_manager'
    )
    return connection


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']

        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if the username already exists
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            connection.close()
            return render_template('signup.html', error="Username already exists. Please choose another.")

        # Insert new user credentials into the database
        cursor.execute('INSERT INTO users (username, email, phone, password) VALUES (%s, %s, %s, %s )', (username, email, phone, password))
        connection.commit()
        
        cursor.close()
        connection.close()

        session['user'] = username
        return redirect(url_for('dashboard'))

    return render_template('signup.html')




@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if username exists
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()

        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials. Please try again.")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('base.html', username=session['user'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None) 
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
