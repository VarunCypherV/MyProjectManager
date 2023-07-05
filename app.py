from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from flask import jsonify
import logging


app = Flask(__name__)
app.secret_key = 'your-secret-key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'  # Replace with your MySQL host
app.config['MYSQL_USER'] = 'root'  # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = 'Mysqlvarun#2004'  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'NewProjectManagement1'  # Replace with your MySQL database name

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

def get_projects_by_status(status):
    cur = mysql.cursor()
    query = "SELECT * FROM projects WHERE status = %s"
    cur.execute(query, (status,))
    projects = cur.fetchall()
    cur.close()
    return [{'id': project[0], 'project_name': project[1]} for project in projects]

def get_project_by_id(project_id):
    cur = mysql.cursor()
    query = "SELECT * FROM projects WHERE id = %s"
    cur.execute(query, (project_id,))
    project = cur.fetchone()
    cur.close()
    return project

def get_project_details(project_id):
    cur = mysql.cursor()
    query = "SELECT * FROM project_details WHERE project_id = %s"
    cur.execute(query, (project_id,))
    project_details = cur.fetchone()
    cur.close()
    return project_details


@app.route('/project/<username>')
def project(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))

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

    return redirect(url_for('project', username=session['username']))

@app.route('/move_project', methods=['POST'])
def move_project():
    project_id = request.form['project_id']
    current_status = request.form['current_status']
    new_status = request.form['new_status']

    # Update the project status
    query = "UPDATE projects SET status = %s WHERE id = %s AND status = %s"

    # Create a cursor object to execute queries
    cursor = mysql.cursor()
    cursor.execute(query, (new_status, project_id, current_status))
    mysql.commit()

    cursor.close()

    return redirect(url_for('project', username=session['username']))

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    # Delete the project from the database
    query = "DELETE FROM projects WHERE id = %s"
    cursor = mysql.cursor()
    cursor.execute(query, (project_id,))
    mysql.commit()
    cursor.close()

    return redirect(url_for('project', username=session['username']))

@app.route('/project-details/<int:project_id>', methods=['GET'])
def project_details(project_id):
    project = get_project_by_id(project_id)
    project_details = get_project_details(project_id)
    collaborators= get_collaborators(project_id)
    return jsonify({
        'start_date': project_details[2].isoformat(),
        'end_date': project_details[3].isoformat(),
        'budget': project_details[4],
        'owner': project_details[5],
        'collaborators': [{'collaborator_name': collaborator[2] , 'collaborator_id': collaborator[3]} for collaborator in collaborators]

    })

def get_collaborators(project_id):
    cur = mysql.cursor()
    query = "SELECT * FROM collaborators WHERE project_id = %s"
    cur.execute(query, (project_id,))
    collaborators = cur.fetchall()
    cur.close()
    return collaborators


@app.route('/collaborator-details/<int:emp_id>', methods=['GET'])
def collaborator_details(emp_id):
    cur = mysql.cursor()
    query = "SELECT * FROM collaborators_details WHERE emp_id = %s"
    cur.execute(query, (emp_id,))
    collaborator = cur.fetchall()
    cur.close()


    collaborator_details = {
        'name': collaborator[0][0],
        'worked_projects': collaborator[0][1],  # Number of worked projects
        'current_projects': collaborator[0][2],  # Number of current projects
        'age': collaborator[0][3],  # Age
        'emp_id': collaborator[0][4]  # Employee ID
    }
    #jsonify(collaborator_details)
    return collaborator
#



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)