from app import app
from flask import render_template, redirect, url_for
from app.forms import AddContact

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add():
    add = AddContact()
    if add.validate_on_submit():
        first_name = add.first_name.data
        last_name = add.last_name.data
        phone_number = add.phone_number.data
        address = add.address.data
        print(first_name, last_name, phone_number, address)
        return redirect(url_for('index'))
    return render_template('add.html', add=add)