from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
from werkzeug.utils import secure_filename

from datetime import date
today = date.today()


app = Flask(__name__)
app.secret_key = 'super secret key'

UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# Database connection for XAMPP
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='task_manager'
    )
    return connection


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# Create Task
@app.route('/create', methods=['GET', "POST"])
def create():
    if request.method == "POST":
        form_data = request.form
        title = form_data["title"]
        text = form_data["desc"]
        date = today.strftime("%d %B %Y")

        file = request.files['inputFile']
        filename = secure_filename(file.filename)
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Insert Task into MySQL
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO task_table (title, description, image) VALUES (%s, %s, %s)"
            values = (title, text, filename)
            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            conn.close()

            return redirect('/dashboard')
        else:
            return "Invalid Upload: Only txt, pdf, png, jpg, jpeg, gif allowed"

    return render_template("create_task.html")


# Edit Task
@app.route('/edit/<int:id>', methods=['GET', "POST"])
def edit(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM task_table WHERE id = %s", (id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()

    if not data:
        return "Task Not Found", 404

    if request.method == "POST":
        title = request.form["title"]
        text = request.form["desc"]

        if title:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "UPDATE task_table SET title = %s, description = %s WHERE id = %s"
            values = (title, text, id)
            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            conn.close()

        return redirect('/')

    return render_template("edit.html", title=data["title"], desc=data["description"])


# Delete Task
@app.route('/delete/<int:id>', methods=['GET', "POST"])
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM task_table WHERE id = %s", (id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()

    if not data:
        return "Task Not Found", 404

    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM task_table WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/')

    return render_template("delete.html", title=data["title"])


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        list1 = {}

        # Connect to MySQL and fetch data
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT title, description FROM task_table")
        posts = cursor.fetchall()

        cursor.close()
        conn.close()

        for t in posts:
            list1[t["title"]] = t["description"]

        return render_template('base.html', username=session['user'], posts=posts)
    return redirect(url_for('login'))

@app.route('/searchTask', methods=['POST'])
def search():
    title = request.form["searc"]  # Get search input
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Search in MySQL
    query = "SELECT * FROM task_table WHERE title LIKE %s"
    cursor.execute(query, ("%" + title + "%",))
    posts = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('searched.html', posts=posts)


@app.route('/logout')
def logout():
    session.pop('user', None) 
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
