from flask import Flask, jsonify, abort, render_template,url_for,request,session, redirect, send_from_directory, Response, Blueprint
from flask_restful import Resource, reqparse
from flask_restful_swagger_2 import Api, swagger, Schema
from flask_json import FlaskJSON, json_response
import pandas as pd
import requests
import json
from dotenv import dotenv_values

env = dotenv_values(".env")

app = Flask(__name__)
port = env['APP_PORT']
host = env['APP_HOST']
api_version = env['API_VERSION']
url_subpath = env['URL_SUBPATH']
koha_api_public_test = env["KOHA_API_PUBLIC_TEST"]

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

@api.representation('application/json')
def output_json(data, code):
    return json_response(data_=data, status_=code)

class HelloWorld(Resource):
    def get(self):
        # Default to 200 OK
        return jsonify({'msg': 'Hello world'})

class KohaApiPubliqueItems(Resource):
    @swagger.doc({
    })
    def get(self, biblio_id):
        url = f"{koha_api_public_test}biblios/{biblio_id}/items"
        response = requests.request("GET", url).text
        data = json.loads(response)        
        return jsonify(data)

api.add_resource(HelloWorld, f'/api/{api_version}', f'/api/{api_version}/hello')      
api.add_resource(KohaApiPubliqueItems, f'/api/{api_version}/koha_items/<string:biblio_id>')

if __name__ == '__main__':
    app.run(debug=True,port=port,host=host)