from . import api
from app import db
from app.models import Contact
from flask import request

# Endpoint to get all contacts
@api.route('/contacts', methods=["GET"])
def get_contacts():
    contacts = db.session.execute(db.select(Contact)).scalars().all()
    return [contact.to_dict() for contact in contacts]

# Endpoint to get a contact by ID
@api.route('/contacts/<contact_id>')
def get_contact(contact_id):
    contact = db.session.get(Contact, contact_id)
    if not contact:
        return {'error':f'Contact with an ID of {contact_id} does not exist'}, 404
    return contact.to_dict

# Endpoint create contact post
@api.route('/contacts', methods=["POST"])
def contacts_post():
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    data = request.json
    # Validate incoming data
    required_fields = ['first_name', 'last_name', 'phone_number']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')
    
    new_contact = Contact(first_name=first_name, last_name=last_name, phone_number=phone_number)
    db.session.add(new_contact)
    db.session.commit()
    return new_contact.to_dict(), 201
