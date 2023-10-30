from . import api
from app import db
from app.models import Contact, User
from flask import request
from .auth import basic_auth, token_auth

# Endpoint to get token -  requires username/password
@api.route('/token')
@basic_auth.login_required
def get_token():
    auth_user = basic_auth.current_user()
    token = auth_user.get_token()
    return {'token': token}

# Endpoint to get an user by ID
@api.route('/users/<user_id>', methods=["GET"])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return {'error': f'User with an ID of {user_id} does not exist'}, 404
    return user.to_dict()

# Endpoint to create a new user
@api.route('/users', methods=["POST"])
def create_new_user():
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    data = request.is_json
    required_fields = ['first_name', 'last_name', 'email', 'username', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    
    new_user = User(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return new_user.to_dict(), 201

# Endpoint to get all contacts
@api.route('/contacts', methods=["GET"])
def get_contacts():
    contacts = db.session.execute(db.select(Contact)).scalars().all()
    return [contact.to_dict() for contact in contacts]

# Endpoint to get a contact by ID
@api.route('/contacts/<contact_id>', methods=["GET"])
def get_contact(contact_id):
    contact = db.session.get(Contact, contact_id)
    if not contact:
        return {'error':f'Contact with an ID of {contact_id} does not exist'}, 404
    return contact.to_dict

# Endpoint to create contact
@api.route('/contacts', methods=["POST"])
@token_auth.login_required
def contacts_post():
    # Check to see if that request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json
    # Validate incoming data
    required_fields = ['first_name', 'last_name', 'phone_number']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # Get data from the body
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')
    # Get user
    current_user = token_auth.current_user()
    
    # Create new contact to add to the database
    new_contact = Contact(first_name=first_name, last_name=last_name, phone_number=phone_number, user_id=current_user.id)
    db.session.add(new_contact)
    db.session.commit()
    return new_contact.to_dict(), 201

# Endpoint to edit an exiting contact
@api.route('/contacts/<contact_id>', methods=['PUT'])
@token_auth.login_required
def edit_contact(contact_id):
    # Check to see that the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # Get the contact from db
    contact = db.session.get(Contact, contact_id)
    if contact is None:
        return {'error': f"Post with an ID of {contact_id} does not exist"}, 404
    # Make sure authenticated user is the contact author
    current_user = token_auth.current_user()
    if contact.author != current_user:
        return {'error': 'You do not have permission to edit this post'}, 403
    data = request.json
    for field in data:
        if field in {'first_name', 'last_name', 'phone_number'}:
            setattr(contact, field, data[field])
    db.session.commit()
    return contact.to_dict()

# Endpoint to delete an exiting contact
@api.route('/contacts/<contact_id>', methods=["DELETE"])
@token_auth.login_required
def delete_contact(contact_id):
    # Get the contact from db
    contact = db.session.get(Contact, contact_id)
    if contact is None:
        return {'error': f'Contact with an ID of {contact_id} does not exist'}, 404
    # Make sure authenticated user is the contact author
    current_user = token_auth.current_user()
    if contact.author != current_user:
        return {'error': 'You do not have permission to delete this post'}, 403
    # Delete the contact
    db.session.delete(contact)
    db.session.commit()
    return {'success': f"{contact.first_name} {contact.last_name} has been deleted"}, 204