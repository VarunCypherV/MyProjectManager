from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your-secret-key'
# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'  # Replace with your MySQL host
app.config['MYSQL_USER'] = 'root'  # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = 'Mysqlvarun#2004'  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'ProjectManagement'  # Replace with your MySQL database name

mysql = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB']
)

def authenticate_user(username, password):
    cur = mysql.cursor()
    query = "SELECT * FROM users WHERE username=%s AND password=%s"
    cur.execute(query, (username, password))
    user = cur.fetchone()
    cur.close()
    return user

def register_user(username, password):
    cur = mysql.cursor()
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    cur.execute(query, (username, password))
    mysql.commit()
    cur.close()

def get_projects_by_status(status):
    cur = mysql.cursor()
    query = "SELECT project_name FROM projects WHERE status = %s"
    cur.execute(query, (status,))
    projects = [row[0] for row in cur.fetchall()]
    cur.close()
    return projects

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('project', username=session['username']))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Authenticate the user by checking against the database
        user = authenticate_user(username, password)
        if user:
            # Authentication successful, store username in session
            session['username'] = username
            return redirect(url_for('project', username=username))
        else:
            # Authentication failed, redirect back to the login page with an error message
            return render_template('login.html', error='Invalid credentials. Please try again.')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Register the user by adding to the database
        register_user(username, password)

        # Redirect back to the login page after registration
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/project/<username>')
def project(username):
    # Get projects from the database for each column
    yet_to_start_projects = get_projects_by_status('Yet to Start')
    in_progress_projects = get_projects_by_status('In Progress')
    finished_projects = get_projects_by_status('Finished')

    return render_template('project.html', username=username, yet_to_start_projects=yet_to_start_projects,
                           in_progress_projects=in_progress_projects, finished_projects=finished_projects)

def add_project_to_db(project_name, status):
    cur = mysql.cursor()
    query = "INSERT INTO projects (project_name, status) VALUES (%s, %s)"
    cur.execute(query, (project_name, status))
    mysql.commit()
    cur.close()

@app.route('/add_project', methods=['POST'])
def add_project():
    if 'username' not in session:
        return redirect(url_for('login'))

    project_name = request.form['project_name']
    status = request.form['status']

    # Add the project to the database with the specified status
    add_project_to_db(project_name, status)

    return redirect('/project/' + session['username'])

@app.route('/move_project', methods=['POST'])
def move_project():
    project_id = request.form['project_id']
    new_status = request.form['new_status']

    # Connect to the database
    connection = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

    # Create a cursor object to execute queries
    cursor = connection.cursor()

    # Define the SQL query to update the project status
    query = "UPDATE projects SET status = %s WHERE id = %s"

    # Execute the query with the new_status and project_id parameters
    cursor.execute(query, (new_status, project_id))

    # Commit the changes to the database
    connection.commit()

    # Close the cursor and the database connection
    cursor.close()
    connection.close()

    return redirect(url_for('project', username=session['username']))

@app.route('/remove_project', methods=['POST'])
def remove_project():
    project_id = request.form['project_id']

    # Connect to the database
    connection = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

    # Create a cursor object to execute queries
    cursor = connection.cursor()

    # Define the SQL query to delete the project
    query = "DELETE FROM projects WHERE id = %s"

    # Execute the query with the project_id parameter
    cursor.execute(query, (project_id,))

    # Commit the changes to the database
    connection.commit()

    # Close the cursor and the database connection
    cursor.close()
    connection.close()

    return redirect(url_for('project', username=session['username']))

if __name__ == '__main__':
    app.secret_key = 'your-secret-key'  # Set a secret key for session management
    app.run(debug=True)
