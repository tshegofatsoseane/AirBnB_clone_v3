#!/usr/bin/python3
'''
Create view for Place objects - handles all default RESTful API actions
'''

# Imports necessary modules
from flask import abort, jsonify, request
# Import required models
from models.city import City
from models.place import Place
from models.state import State
from models.user import User
from models.amenity import Amenity
from api.v1.views import app_views
from models import storage


# Route for retrieving Place objects of a City
@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places_by_city(city_id):
    '''
    Retrieves list of Place objects of a City
    '''
    # Get City object with given ID from storage
    city = storage.get(City, city_id)
    if not city:
        # Return 404 error if City object not found
        abort(404)

    # Get Place objects of City and convert them to dictionaries
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


# Route for retrieving specific Place object by ID
@app_views.route('/places/<place_id>', methods=['GET'],
                 strict_slashes=False)
def get_place(place_id):
    '''
    Retrieves Place object
    '''
    # Get Place object with given ID from storage
    place = storage.get(Place, place_id)
    if place:
        # Return Place object in JSON format
        return jsonify(place.to_dict())
    else:
        # Return 404 error if Place object is not found
        abort(404)


# Route for deleting specific Place object by ID
@app_views.route('/places/<place_id>', methods=['DELETE'])
def delete_place(place_id):
    '''
    Deletes Place object
    '''
    # Get Place object with given ID from storage
    place = storage.get(Place, place_id)
    if place:
        # Delete Place object from storage and save changes
        storage.delete(place)
        storage.save()
        # Return an empty JSON with 200 status code
        return jsonify({}), 200
    else:
        # Return 404 error if Place object not found
        abort(404)


# Route for creating new Place object
@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    '''
    Creates Place object
    '''
    # Get City object with given ID from storage
    city = storage.get(City, city_id)
    if not city:
        # Return 404 error if City object is not found
        abort(404)

    # Check if request data in JSON format
    if not request.get_json():
        # Return 400 error if request data not in JSON format
        abort(400, 'Not a JSON')

    # Get JSON data from request
    data = request.get_json()
    if 'user_id' not in data:
        # Return 400 error if 'user_id' key missing in JSON data
        abort(400, 'Missing user_id')
    if 'name' not in data:
        # Return 400 error if 'name' key missing in JSON data
        abort(400, 'Missing name')

    # Get User object with given user_id from storage
    user = storage.get(User, data['user_id'])
    if not user:
        # Return 404 error if User object is not found
        abort(404)

    # Assign city_id to JSON data
    data['city_id'] = city_id
    # Creat new Place object with JSON data
    place = Place(**data)
    # Save Place object to storage
    place.save()
    # Return newly created Place object in JSON format 201 status
    return jsonify(place.to_dict()), 201


# Route updating existing Place object by ID
@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    '''
    Updates Place object
    '''
    # Get Place object with given ID from storage
    place = storage.get(Place, place_id)
    if place:
        # Checks request data in JSON format
        if not request.get_json():
            # Return 400 error if request data not in JSON format
            abort(400, 'Not a JSON')

        # Get the JSON data from the request
        data = request.get_json()
        ignore_keys = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
        # Update the attributes of the Place object with the JSON data
        for key, value in data.items():
            if key not in ignore_keys:
                setattr(place, key, value)

        # Save the updated Place object to the storage
        place.save()
        # Return the updated Place object in JSON format with 200 status code
        return jsonify(place.to_dict()), 200
    else:
        # Return 404 error if the Place object is not found
        abort(404)


# Error Handlers:
@app_views.errorhandler(404)
def not_found(error):
    '''
    Returns 404: Not Found
    '''
    # Return a JSON response for 404 error
    response = {'error': 'Not found'}
    return jsonify(response), 404


@app_views.errorhandler(400)
def bad_request(error):
    '''
    Return Bad Request message for illegal requests to the API
    '''
    # Return a JSON response for 400 error
    response = {'error': 'Bad Request'}
    return jsonify(response), 400


# New endpoint: POST /api/v1/places_search
@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """
    Retrieves Place objects based on the provided JSON search criteria
    """

    # Check if the request contains valid JSON
    if request.get_json() is None:
        abort(400, description="Not a JSON")

    # Extract data from the JSON request body
    data = request.get_json()

    if data and len(data):
        states = data.get('states', None)
        cities = data.get('cities', None)
        amenities = data.get('amenities', None)

    # If no criteria provided, retrieve all places
    if not data or not len(data) or (
            not states and
            not cities and
            not amenities):
        places = storage.all(Place).values()
        list_places = []
        for place in places:
            list_places.append(place.to_dict())
        return jsonify(list_places)

    list_places = []

    # Filter and retrieve places based on states criteria
    if states:
        states_obj = [storage.get(State, s_id) for s_id in states]
        for state in states_obj:
            if state:
                for city in state.cities:
                    if city:
                        for place in city.places:
                            list_places.append(place)

    # Filter and retrieve places based on cities criteria
    if cities:
        city_obj = [storage.get(City, c_id) for c_id in cities]
        for city in city_obj:
            if city:
                for place in city.places:
                    if place not in list_places:
                        list_places.append(place)

    # Filter places based on amenities criteria
    if amenities:
        if not list_places:
            list_places = storage.all(Place).values()
        amenities_obj = [storage.get(Amenity, a_id) for a_id in amenities]

        list_places = [place for place in list_places
                       if all([am in place.amenities
                               for am in amenities_obj])]

    # Prepare the final list of places for response
    places = []
    for p in list_places:
        d = p.to_dict()
        d.pop('amenities', None)
        places.append(d)

    # Return the list of places in JSON format
    return jsonify(places)
