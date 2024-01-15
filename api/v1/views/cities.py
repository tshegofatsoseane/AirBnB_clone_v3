#!/usr/bin/python3
'''
Create a new view for City objects - handles all default RESTful API actions.
'''

# Import necessary modules
from flask import abort, jsonify, request
# Import State and City models
from models.state import State
from models.city import City
from api.v1.views import app_views
from models import storage


# Route for retrieving City objects of specific State
@app_views.route('/states/<state_id>/cities', methods=['GET'],
                 strict_slashes=False)
def get_cities_by_state(state_id):
    '''
    Retrieves list of all City objects of State.
    '''
    # Get State object with given ID from storage
    state = storage.get(State, state_id)
    if not state:
        # Return 404 error if State object not found
        abort(404)

    # Get all City objects associated with
    #  State and convert them to dictionaries
    cities = [city.to_dict() for city in state.cities]
    return jsonify(cities)


# Route for retrieving specific City object by ID
@app_views.route('/cities/<city_id>', methods=['GET'], strict_slashes=False)
def get_city(city_id):
    '''
    Retrieves City object.
    '''
    # Get City object with given ID from storage
    city = storage.get(City, city_id)
    if city:
        # Return City object in JSON format
        return jsonify(city.to_dict())
    else:
        # Return 404 error if City object not found
        abort(404)


# Route for deleting specific City object by ID
@app_views.route('/cities/<city_id>', methods=['DELETE'])
def delete_city(city_id):
    '''
    Deletes City object.
    '''
    # Get City object with given ID from storage
    city = storage.get(City, city_id)
    if city:
        # Delete City object from storage and save changes
        storage.delete(city)
        storage.save()
        # Return empty JSON with 200 status code
        return jsonify({}), 200
    else:
        # Return 404 error if City object not found
        abort(404)


# Route for creating new City object under specific State
@app_views.route('/states/<state_id>/cities', methods=['POST'],
                 strict_slashes=False)
def create_city(state_id):
    '''
    Creates City object.
    '''
    # Get State object with given ID from storage
    state = storage.get(State, state_id)
    if not state:
        # Return 404 error if State object not found
        abort(404)

    # Check if request data is in JSON format
    if not request.get_json():
        # Return 400 error if request data not in JSON format
        abort(400, 'Not a JSON')

    # Get JSON data from request
    data = request.get_json()
    if 'name' not in data:
        # Return 400 error if 'name' key is missing in JSON data
        abort(400, 'Missing name')

    # Assign 'state_id' key in JSON data
    data['state_id'] = state_id
    # Create new City object with JSON data
    city = City(**data)
    # Save City object to storage
    city.save()
    # Return newly created City object in JSON format with 201 status code
    return jsonify(city.to_dict()), 201


# Route for updating existing City object by ID
@app_views.route('/cities/<city_id>', methods=['PUT'], strict_slashes=False)
def update_city(city_id):
    '''
    Updates City object.
    '''
    # Get City object with given ID from storage
    city = storage.get(City, city_id)
    if city:
        # Check if request data is in JSON format
        if not request.get_json():
            # Return 400 error if request data is not in JSON format
            abort(400, 'Not a JSON')

        # Get JSON data from request
        data = request.get_json()
        ignore_keys = ['id', 'state_id', 'created_at', 'updated_at']
        # Update attributes of City object with JSON data
        for key, value in data.items():
            if key not in ignore_keys:
                setattr(city, key, value)

        # Save the updated City object to the storage
        city.save()
        # Return the updated City object in JSON format with 200 status code
        return jsonify(city.to_dict()), 200
    else:
        # Return 404 error if the City object is not found
        abort(404)


# Error Handlers:
@app_views.errorhandler(404)
def not_found(error):
    '''
    404: Not Found.
    '''
    # Return a JSON response for 404 error
    return jsonify({'error': 'Not found'}), 404


@app_views.errorhandler(400)
def bad_request(error):
    '''
    Return Bad Request message for illegal requests to API.
    '''
    # Return a JSON response for 400 error
    return jsonify({'error': 'Bad Request'}), 400
