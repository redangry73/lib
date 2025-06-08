from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import select

from lib import create_user, create_book, create_booking, delete_booking, get_session, user, book

app = Flask(__name__)
app.secret_key = 'change-this-secret'

@app.route('/')
def index():
    session = get_session()
    books = session.execute(select(book)).scalars().all()
    session.close()
    return render_template('index.html', books=books)

@app.route('/create_user', methods=['POST'])
def create_user_route():
    name = request.form.get('name')
    email = request.form.get('email')
    if create_user(name, email):
        flash('User created successfully')
    else:
        flash('Failed to create user')
    return redirect(url_for('index'))

@app.route('/add_book', methods=['POST'])
def add_book_route():
    title = request.form.get('title')
    author = request.form.get('author')
    copies = int(request.form.get('copies', 1))
    create_book(title, author, copies)
    flash('Book added successfully')
    return redirect(url_for('index'))

@app.route('/create_booking', methods=['POST'])
def create_booking_route():
    email = request.form.get('email')
    title = request.form.get('title')
    author = request.form.get('author')
    resp = create_booking(email, author, title)
    flash(resp.INFO)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
