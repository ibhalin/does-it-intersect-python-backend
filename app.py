from flask import Flask
import psycopg2
import shapely as shp
import json

app = Flask(__name__)

with open("config.json", "r") as config_file:
    config = json.load(config_file)

def string_to_list_of_2_json(input):
    output = input.split('},{')
    output[0], output[1] = output[0] + '}', '{' + output[1]
    return output


def to_geometry(input):

    output =  string_to_list_of_2_json(input)
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
    response.headers['Access-Control-Allow-Origin'] = 'http://antoinehalin.fr'

    # Allow specific HTTP methods
    response.headers['Access-Control-Allow-Methods'] = 'GET'

    return response

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/shapely/get_predicates/<list_of_features>', methods=["GET"])
def get_shapely_predicates(list_of_features):
    if not isinstance(list_of_features, str):
        raise Exception("error: Input is not a string")
    features = to_geometry(list_of_features)
    return json.dumps({
        "isContain": tryCatch(shp.contains, features),
        "isCross": tryCatch(shp.crosses, features),
        "isEqual": tryCatch(shp.equals, features),
        "isIntersect": tryCatch(shp.intersects, features),
        "isOverlap": tryCatch(shp.overlaps, features),
        "isTouch": tryCatch(shp.touches, features),
        "isWithin": tryCatch(shp.within, features)})

@app.route('/postgis/get_predicates/<list_of_features>', methods=["GET"])
def get_postgis_predicates(list_of_features):

    if not isinstance(list_of_features, str):
        raise Exception("error: Input is not a string")
    
    connection = psycopg2.connect(
        host=config["db_host"],
        database=config["db_database"],
        user=config["db_user"],
        password=config["db_password"]
    )

    cursor = connection.cursor()
    features = string_to_list_of_2_json(list_of_features)
    print(features)
    cursor.callproc('my_predicate_check', (features[0], features[1]))
    result = cursor.fetchone()
    cursor.close()
    connection.close()


    if result is not None:
        return result[0]

    return "it failed"