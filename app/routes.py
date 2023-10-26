from app import app, db
from flask import render_template, redirect, url_for, flash
from app.forms import AddContact
from app.models import Contact


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    form = AddContact()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        phone_number = form.phone_number.data
        address = form.address.data
        print(first_name, last_name, phone_number, address)
        
        check_contact = db.session.execute(db.select(Contact).where( (Contact.phone_number==phone_number))).scalars().all()
        if check_contact:
            flash('A contact with that phone number already exists')
            return redirect(url_for('add_contact'))
        
        new_contact = Contact(first_name=first_name, last_name=last_name, phone_number=phone_number, address=address)
        db.session.add(new_contact)
        db.session.commit()
        
        
        return redirect(url_for('index'))
    return render_template('add.html', form=form)
