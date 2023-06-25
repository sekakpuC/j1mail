# app.py
from flask import Flask, render_template, request, redirect, session, make_response
import json, uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Sample email data
emails = [
    {'id': 1, 'subject': 'Hello', 'sender': 'sender1@example.com'},
    {'id': 2, 'subject': 'Meeting', 'sender': 'sender2@example.com'},
    {'id': 3, 'subject': 'Important Announcement', 'sender': 'sender3@example.com'}
]
next_id = 4  # To track the ID for the next email

# Load user credentials from users.jsonl
def load_users():
    with open('users.jsonl', 'r') as file:
        return [json.loads(line) for line in file]

# Save user credentials to users.jsonl
def save_users(users):
    with open('users.jsonl', 'w') as file:
        for user in users:
            file.write(json.dumps(user) + '\n')

# Load browser sessions from sessions.jsonl
def load_sessions():
    try:
        with open('sessions.jsonl', 'r') as file:
            return [json.loads(line) for line in file]
    except FileNotFoundError:
        return []

# Save browser sessions to sessions.jsonl
def save_sessions(sessions):
    with open('sessions.jsonl', 'w') as file:
        for session in sessions:
            file.write(json.dumps(session) + '\n')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['user'] = user
                session['uuid'] = str(uuid.uuid4())
                sessions = load_sessions()
                sessions.append({'session_id': session['uuid'], 'user': user})
                save_sessions(sessions)
                response = make_response(redirect('/list'))
                response.set_cookie('username', user['username'])
                return response
        return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user' not in session:
        return redirect('/login')
    sessions = load_sessions()
    sessions = [s for s in sessions if s['session_id'] != session['uuid']]
    save_sessions(sessions)
    session.pop('user', None)

    response = make_response(redirect('/login'))
    response.delete_cookie('username')
    return response

@app.route('/protected')
def protected():
    if 'user' in session:
        return 'Welcome to the protected page, ' + session['user']['username']
    return 'Access denied'

@app.route('/list')
def list():
    if 'user' not in session:
        return redirect('/login')
    data={}
    data["emails"]=emails
    c=request.cookies
    username=c.get("username")
    data["username"]=username
    return render_template('list.html', data=data)

@app.route('/')
def index():
    return render_template('index.html', emails=emails)

@app.route('/create', methods=['GET', 'POST'])
def create():
    global next_id
    if request.method == 'POST':
        subject = request.form['subject']
        sender = request.form['sender']
        email = {'id': next_id, 'subject': subject, 'sender': sender}
        emails.append(email)
        next_id += 1
        return redirect('/')
    return render_template('create.html')

@app.route('/read/<int:email_id>', methods=['GET'])
def read(email_id):
    email = next((e for e in emails if e['id'] == email_id), None)
    if not email:
        return redirect('/')
    return render_template('read.html', email=email)

@app.route('/edit/<int:email_id>', methods=['GET', 'POST'])
def edit(email_id):
    email = next((e for e in emails if e['id'] == email_id), None)
    if not email:
        return redirect('/')
    if request.method == 'POST':
        email['subject'] = request.form['subject']
        email['sender'] = request.form['sender']
        return redirect('/')
    return render_template('edit.html', email=email)

@app.route('/delete/<int:email_id>')
def delete(email_id):
    global emails
    emails = [e for e in emails if e['id'] != email_id]
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
