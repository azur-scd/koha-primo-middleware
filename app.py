from flask import Flask, jsonify, abort, render_template,url_for,request,session, redirect, send_from_directory, Response, Blueprint
from flask_restful import Resource, reqparse
from flask_restful_swagger_2 import Api, swagger, Schema
from flask_json import FlaskJSON, json_response
from flask_cors import CORS
import pandas as pd
import requests
import json
from dotenv import dotenv_values
import config

env = dotenv_values(".env")

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

port = env['APP_PORT']
host = env['APP_HOST']
api_version = env['API_VERSION']
url_subpath = env['URL_SUBPATH']
demo_koha_api_public = env["DEMO_KOHA_API_PUBLIC"]
preprod_koha_api_public = env["PREPROD_KOHA_API_PUBLIC"]
mapping_bibs = config.MAPPING_BIBS
mapping_codes_types_pret = config.MAPPING_CODES_TYPES_PRET

class ReverseProxied(object):
    #Class to dynamically adapt Flask converted url of static files (/sttaic/js...) + templates html href links according to the url app path after the hostname (set in cnfig.py)
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
    if (item['checked_out_date'] is None) & (item["holding_library_id"] == item["home_library_id"]):
        result['checked_out_date'] = 'Disponible'
    elif (item['checked_out_date'] is None) & (item["holding_library_id"] != item["home_library_id"]):
        result['checked_out_date'] = 'Indisponible : en transfert'
    #elif item['checked_out_date'] is not None:
    else:
        result['checked_out_date'] = 'Indisponible : emprunté'
    result["item_type_id"] = mapping_codes_types_pret[item["item_type_id"]]
    result["home_library_id"] = mapping_bibs[item["home_library_id"]]
    result["location"] = item["location"]
    result["callnumber"] = item["callnumber"]
    return result

@api.representation('application/json')
def output_json(data, code):
    return json_response(data_=data, status_=code)

class HelloWorld(Resource):
    def get(self):
        # Default to 200 OK
        return jsonify({'msg': 'Hello world'})

class KohaApiPubliqueBibliosItems(Resource):
    @swagger.doc({
    })
    def get(self, biblio_id):
        url = f"{preprod_koha_api_public}biblios/{biblio_id}/items"
        response = requests.request("GET", url).text
        data = json.loads(response)
        new_data = [extract_koha_item(i) for i in data]        
        return jsonify(new_data)

api.add_resource(HelloWorld, f'/api/{api_version}', f'/api/{api_version}/hello')      
api.add_resource(KohaApiPubliqueBibliosItems, f'/api/{api_version}/koha/biblios_items/<string:biblio_id>')

if __name__ == '__main__':
    app.run(debug=True,port=port,host=host)