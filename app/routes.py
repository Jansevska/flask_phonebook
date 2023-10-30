from app import app, db
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import AddContact, SignUpForm, LoginForm
from app.models import Contact, User


@app.route('/')
def index():
    # Not sure about this.... needs to be logged in to view and edit/delete contacts
    # @login_required
    # contacts = db.session.execute(db.select(Contact)).scalars().all()
    return render_template('index.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    # create instance of the signupform
    form = SignUpForm()
    if form.validate_on_submit():
        # Get the data from each of the fidls
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        # print(first_name, last_name, username, email, password)
        
        # Check to see if the user already exists
        check_user = db.session.execute(db.select(User).where( (User.username==username) | (User.email==email) )).scalars().all()
        if check_user:
            flash('A user with that username and/or email already exists')
            return redirect(url_for('signup'))
        
        # Create new instance of the User class with the data from the form
        new_user = User(first_name = first_name, last_name = last_name, username = username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        # log the newly created user in
        login_user(new_user)
        
        flash(f"{new_user.username} has been created and is logged in!")
        
        # Redirect back to the home page
        return redirect(url_for('phonebook'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember_me = form.remember_me.data
        user = db.session.execute(db.select(User).where(User.username==username)).scalar()
        if user is not None and user.check_password(password):
            login_user(user, remember=remember_me)
            # log user in via Flask-Login
            flash(f'{user.username} has successfully logged in.')
            return redirect(url_for('phonebook'))
        else:
            flash('Incorrect username and/or password')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have successfully logged out')
    return redirect(url_for('index'))

@app.route('/phonebook')
@login_required
def phonebook():
    contacts = db.session.execute(db.select(Contact)).scalars().all()
    return render_template('phonebook.html', contacts=contacts)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_contact():
    form = AddContact()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        phone_number = form.phone_number.data
        address = form.address.data
        
        check_contact = db.session.execute(db.select(Contact).where( (Contact.phone_number==phone_number))).scalars().all()
        if check_contact:
            flash('A contact with that phone number already exists')
            return redirect(url_for('add_contact'))
        
        new_contact = Contact(first_name=first_name, last_name=last_name, phone_number=phone_number, address=address, user_id=current_user.id)
        db.session.add(new_contact)
        db.session.commit()
        flash(f"{new_contact} has been added to your contacts")
        
        return redirect(url_for('phonebook'))
    return render_template('add.html', form=form)


# @app.route('/contacts/<contact_id>/contacts_view')
# @login_required
# def contacts_view(contact_id):
    # contact = db.session.get(Contact, contact_id)
    # if not contact:
    #     flash('That contact does not exist')
    #     return redirect(url_for('contacts_view'))
    # return render_template('add.html', contact=contact)

@app.route('/contacts/<contact_id>/edit_contact', methods=["GET", "POST"])
@login_required
def edit_contact(contact_id):
    contact = db.session.get(Contact, contact_id)
    if not contact:
        flash('That contact does not exist')
        return redirect(url_for('phonebook'))
    if current_user != contact.author:
        flash('Please login to view and edit contacts')
        return redirect(url_for('login', contact_id=contact_id))
    
    form = AddContact()
    if form.validate_on_submit():
        contact.first_name = form.first_name.data
        contact.last_name = form.last_name.data
        contact.phone_number = form.phone_number.data
        contact.address = form.address.data
        
        db.session.commit()
        flash(f'{contact.first_name} {contact.last_name} has been edited.', 'success')
        return redirect(url_for('phonebook'))
    
    form.first_name.data = contact.first_name
    form.last_name.data = contact.last_name
    form.phone_number.data = contact.phone_number
    form.address.data = contact.address
    return render_template('edit_contact.html', contact=contact, form=form)
    
@app.route('/contacts/<contact_id>/delete', methods=["DELETE"])
@login_required
def delete_contact(contact_id):
    contact = db.session.get(Contact, contact_id)
    if not contact:
        flash('That contact does not exist')
        return redirect(url_for('phonebook'))

    db.session.delete(contact)
    db.session.commit()

    flash(f"{contact.first_name} {contact.last_name} has been deleted")
    return redirect(url_for('phonebook'))
