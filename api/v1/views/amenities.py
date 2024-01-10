#!/usr/bin/python3
'''
Make view for Amenity objects and handle default RESTful API actions.
'''

# Import necessary modules
from flask import abort, jsonify, request
from models.amenity import Amenity
from api.v1.views import app_views
from models import storage


#  Retrieving all Amenity objects Route
@app_views.route('/amenities', methods=['GET'], strict_slashes=False)
def get_all_amenities():
    '''Retrieve list of Amenity objects'''
    # Get Amenity objects from storage
    amenities = storage.all(Amenity).values()
    # Convert objects to dictionaries and convert to jason
    return jsonify([amenity.to_dict() for amenity in amenities])


#  Retrieving specific Amenity object by ID Route
@app_views.route('/amenities/<amenity_id>',
                 methods=['GET'], strict_slashes=False)
def get_amenity(amenity_id):
    '''Retriev Amenity object'''
    # Get Amenity object with given ID from storage
    amenity = storage.get(Amenity, amenity_id)
    if amenity:
        # Return Amenity object JSON
        return jsonify(amenity.to_dict())
    else:
        # Return 404 error if Amenity object not found
        abort(404)


#  Delete specific Amenity object by ID Route
@app_views.route('/amenities/<amenity_id>', methods=['DELETE'])
def delete_amenity(amenity_id):
    '''Delete Amenity object'''
    # Get Amenity object with given IDfrom storage
    amenity = storage.get(Amenity, amenity_id)
    if amenity:
        # Delete Amenity object from storage and save
        storage.delete(amenity)
        storage.save()
        # Return empty JSON with 200 status
        return jsonify({}), 200
    else:
        # Return 404 error if Amenity object is not found
        abort(404)


# Create new Amenity object Route
@app_views.route('/amenities', methods=['POST'], strict_slashes=False)
def create_amenity():
    '''Create Amenity object'''
    if not request.get_json():
        # Return 400 error if request data not JSON format
        abort(400, 'Not a JSON')

    # Get JSON data from request
    data = request.get_json()
    if 'name' not in data:
        # Return 400 error name key missing in JSON data
        abort(400, 'Missing name')

    # Create new Amenity object with JSON data
    amenity = Amenity(**data)
    # Save Amenity object to storage
    amenity.save()
    # Return new  Amenity
    #  Return object in JSON format with 201 status
    return jsonify(amenity.to_dict()), 201


# Update existing Amenity object by ID Route 
@app_views.route('/amenities/<amenity_id>', methods=['PUT'],
                 strict_slashes=False)
def update_amenity(amenity_id):
    '''Updat Amenity object'''
    # Get Amenity object with given ID from storage
    amenity = storage.get(Amenity, amenity_id)
    if amenity:
        # Return 400 error if requested data not in JSON format
        if not request.get_json():
            abort(400, 'Not a JSON')

        # Get JSON data from request
        data = request.get_json()
        ignore_keys = ['id', 'created_at', 'updated_at']
        # Update attributes of Amenity object with JSON data
        for key, value in data.items():
            if key not in ignore_keys:
                setattr(amenity, key, value)

        # Save updated Amenity object to storage
        amenity.save()
        # Return updated Amenity object in JSON format with 200 status
        return jsonify(amenity.to_dict()), 200
    else:
        # Return 404 error if Amenity object not found
        abort(404)


# Error Handlers:
@app_views.errorhandler(404)
def not_found(error):
    '''Returns 404: Not Found'''
    # Return JSON response for 404 error
    response = {'error': 'Not found'}
    return jsonify(response), 404


@app_views.errorhandler(400)
def bad_request(error):
    '''Return Bad Request message for illegal requests to API.'''
    # Return JSON response for 400 error
    response = {'error': 'Bad Request'}
    return jsonify(response), 400
