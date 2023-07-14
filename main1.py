from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Used to encrypt session data

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'to_do'
mysql = MySQL(app)

# Routes
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
       username = request.form['username']
       password = request.form['password']
        
       cur = mysql.connection.cursor()
       cur.execute("SELECT * FROM users WHERE username = %s", (username,))
       existing_user = cur.fetchone()
       if existing_user:
        return 'Username already exists!'
       
        
        
       cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                   (username, password))
       mysql.connection.commit()
       cur.close()
        
       return redirect('/login')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT username,password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        print('user detail',user)
        cur.close()
        
        
        if user and user[1] == password:
            session['username'] = user[0]
            return redirect('/todo')
            # return render_template('todo.html')
        else:
            error = 'Invalid username or password!' 
            return render_template('login.html', error = error)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/todo')
def todo():
    if 'username' in session:
        username = session['username']
        # Fetch tasks for the logged-in user from the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT task_id, title, description, status FROM tasks WHERE username = %s", (username,))
        tasks = cur.fetchall()
        cur.close()
        return render_template('todo.html', tasks=tasks)
        
    else:
        return render_template('todo.html')
    
    # return render_template('todo.html')


@app.route('/add_task', methods=['GET','POST'])
def add_task():
    if request.method == 'POST':
        username = session['username']
        title = request.form['title']
        description = request.form['description']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tasks (title, description, status, username) VALUES (%s, %s, %s, %s)",
                    (title, description, 'Pending', username))
        mysql.connection.commit()
        cur.close()
        return redirect('/todo')
        # return render_template('todo.html')
        
    return render_template('add_task.html')


@app.route('/update_task', methods=['GET', 'POST'])
def update_task():  
    if request.method == 'POST':
        task_id = request.form['task_id']
        status = request.form['status']
        username = session['username']

        cur = mysql.connection.cursor()
        cur.execute("update tasks SET status = %s where task_id = %s AND username = %s",
                    (status, task_id, username))
        mysql.connection.commit()
        cur.close()

        return redirect('/todo')
    else: 
        return render_template('update_task.html')

@app.route('/delete_task', methods=['GET','POST'])
def delete_task():
    if request.method == 'POST':
        task_id = request.form['task_id']
        username = session['username']
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM tasks WHERE task_id = %s AND username = %s", (task_id, username))
        mysql.connection.commit()
        cur.close()
        
        return redirect('/todo')
    else:
        return render_template('delete_task.html')

if __name__ == '__main__':
    app.run(debug=True)