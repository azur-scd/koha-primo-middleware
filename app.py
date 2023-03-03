from flask import Flask, jsonify, abort, render_template,url_for,request,session, redirect, send_from_directory, Response, Blueprint
from flask_restful import Resource, reqparse
from flask_restful_swagger_2 import Api, swagger, Schema
from flask_json import FlaskJSON, json_response
from flask_cors import CORS
import pandas as pd
import requests
import json
from dotenv import dotenv_values
import mappings
import config

env = dotenv_values(".env")

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

port = env['APP_PORT']
host = env['APP_HOST']
api_version = env['API_VERSION']
url_subpath = env['URL_SUBPATH']
demo_koha_api_public = env["DEMO_KOHA_API_PUBLIC"]
prod_koha_api_public = env["PROD_KOHA_API_PUBLIC"]
mapping_codes_types_pret = mappings.MAPPING_CODES_TYPES_PRET
mapping_bibs = mappings.MAPPING_BIBS
mapping_locs = mappings.MAPPING_LOCS
bibs_order = config.BIBS_ORDER
bibs_order_by_label = config.BIBS_ORDER_BY_LABEL

# It dynamically adapts Flask converted url of static files (/sttaic/js...) + templates html href
# links according to the url app path after the hostname (set in cnfig.py)
class ReverseProxied(object):
    def __init__(self, app, script_name=None, scheme=None, server=None):
        self.app = app
        self.script_name = script_name
        self.scheme = scheme
        self.server = server

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '') or self.script_name
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        scheme = environ.get('HTTP_X_SCHEME', '') or self.scheme
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        server = environ.get('HTTP_X_FORWARDED_SERVER', '') or self.server
        if server:
            environ['HTTP_HOST'] = server
        return self.app(environ, start_response)

FlaskJSON(app)
api = Api(app, title='SCD-UCA Middleware Koha-Primo', api_version='1.0', api_spec_url='/api/swagger', base_path=f'{host}:{port}')
app.wsgi_app = ReverseProxied(app.wsgi_app, script_name=url_subpath)

def extract_koha_item(item):
    result = {}
    # s'il n'y a pas de date de retour et si le doc n'est pas en transfert -> disponible
    if (item['checked_out_date'] is None) & (item["holding_library_id"] == item["home_library_id"]):
        result['availability'] = 'Disponible'
    # s'il n'y a pas de date de retour et si le doc est en transfert -> indisponible
    elif (item['checked_out_date'] is None) & (item["holding_library_id"] != item["home_library_id"]):
        result['availability'] = 'Indisponible : en transit'
    # sinon (ie s'il y a une date de retour) -> indisponible
    #elif item['checked_out_date'] is not None:
    else:
        checked_out_date = item['checked_out_date']
        result['availability'] = f'Indisponible : emprunté (Retour le {checked_out_date})'
    # Bibliothèque
    result["home_library_id"] = mapping_bibs[item["home_library_id"]]
    # Localisation
    if item["location"] is not None:
        result["location"] = mapping_locs[item["location"]]
    # Cote
    if item["callnumber"] is not None:
        result["callnumber"] = item["callnumber"]
    # Type de prêt
    if item["item_type_id"] is not None:
        result["loan_type"] = mapping_codes_types_pret[item["item_type_id"]]
    # si pério on affiche l' état de coll ; si monographie on affiche la description
    if item["external_id"].startswith('HDL'):
        result["serial_issue_number"] = f"Etat de collection : {item['serial_issue_number']}"
    elif item["serial_issue_number"] is not None:
        result["serial_issue_number"] =  item["serial_issue_number"]
    return result

@api.representation('application/json')
def output_json(data, code):
    return json_response(data_=data, status_=code)

class HelloWorld(Resource):
    def get(self):
        # Default to 200 OK
        return jsonify({'msg': 'Hello world'})

# It takes a biblio_id as input, and returns a list of items associated with that biblio_id
class KohaApiPubliqueBibliosItems(Resource):

    @swagger.doc({
    })

    def get(self, biblio_id):
        url = f"{prod_koha_api_public}biblios/{biblio_id}/items"
        response = requests.request("GET", url).text
        data = json.loads(response)
        ordered_data = sorted(data, key=lambda x: bibs_order[x.get('home_library_id')])
        # Pour inverser : sorted(data, key=lambda x: bibs_order[x.get('home_library_id')], reverse=True)
        new_data = [extract_koha_item(i) for i in ordered_data]       
        return jsonify(new_data)

api.add_resource(HelloWorld, f'/api/{api_version}', f'/api/{api_version}/hello')      
api.add_resource(KohaApiPubliqueBibliosItems, f'/api/{api_version}/koha/biblios_items/<string:biblio_id>')

if __name__ == '__main__':
    app.run(debug=True,port=port,host=host)

    ## Doc pour recevoir des args du type url/biblios_items/25894/?record_type=book
    # https://github.com/marshmallow-code/webargs/blob/dev/examples/flaskrestful_example.py