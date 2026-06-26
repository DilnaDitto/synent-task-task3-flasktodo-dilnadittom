from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'       # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = 'root' \
'' # Replace with your MySQL password
app.config['MYSQL_DB'] = 'todo_db'

mysql = MySQL(app)

# 1. NEW: Attractive Home Page
@app.route('/')
def home():
    return render_template('home.html')

# 2. Main Task Board
@app.route('/tasks')
def tasks():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks ORDER BY is_completed ASC, created_at DESC")
    all_tasks = cur.fetchall()
    
    # Check if we are currently editing a task
    edit_id = request.args.get('edit_id')
    task_to_edit = None
    if edit_id:
        cur.execute("SELECT * FROM tasks WHERE id = %s", (edit_id,))
        task_to_edit = cur.fetchone()
        
    cur.close()
    return render_template('tasks.html', tasks=all_tasks, task_to_edit=task_to_edit)

# 3. Create: Add a new task
@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    if title and title.strip():
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES (%s)", (title.strip(),))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('tasks'))

# 4. Update: Save changes to an existing task
@app.route('/update/<int:id>', methods=['POST'])
def update_task(id):
    new_title = request.form.get('title')
    if new_title and new_title.strip():
        cur = mysql.connection.cursor()
        cur.execute("UPDATE tasks SET title = %s WHERE id = %s", (new_title.strip(), id))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('tasks'))

# 5. NEW FUNCTIONALITY: Mark Task as Complete/Incomplete
@app.route('/toggle/<int:id>/<int:status>')
def toggle_task(id, status):
    new_status = False if status == 1 else True
    cur = mysql.connection.cursor()
    cur.execute("UPDATE tasks SET is_completed = %s WHERE id = %s", (new_status, id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('tasks'))

# 6. Delete: Remove a task
@app.route('/delete/<int:id>')
def delete_task(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('tasks'))

if __name__ == '__main__':
    app.run(debug=True)