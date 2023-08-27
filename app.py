from flask import Flask
import shapely as shp
from json import dumps

app = Flask(__name__)

def to_geometry(input) :

    output = input.split('},{')
    output[0], output[1] = output[0] + '}', '{' + output[1]
    output = [shp.from_geojson(i) for i in output]

    return output

def tryCatch(f, features) :
    try :
        res = f(features[0], features[1])
        if (res != 1 and res != 0) : #checks if res is not a boolean as bool are just int in python
            return "error : shapely function didn't return boolean as expected"
        return str(res).lower()
    except Exception as e:
        return str(e)

@app.after_request
def add_cors_headers(response):
    # Allow requests from any origin
    response.headers['Access-Control-Allow-Origin'] = '*'

    # Allow specific HTTP methods
    response.headers['Access-Control-Allow-Methods'] = 'GET'

    return response

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/shapely/get_predicates/<list_of_features>', methods=["GET"])
def get_shapely_predicates(list_of_features):
    features = to_geometry(list_of_features)
    return dumps({
        "isContain": tryCatch(shp.contains, features),
        "isCross": tryCatch(shp.crosses, features),
        "isEqual": tryCatch(shp.equals, features),
        "isIntersect": tryCatch(shp.intersects, features),
        "isOverlap": tryCatch(shp.overlaps, features),
        "isTouch": tryCatch(shp.touches, features),
        "isWithin": tryCatch(shp.within, features)})