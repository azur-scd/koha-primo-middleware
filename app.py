from flask import Flask, jsonify, abort, render_template,url_for,request,session, redirect, send_from_directory, Response, Blueprint
from flask_restful import Resource, reqparse
from flask_restful_swagger_2 import Api, swagger, Schema
from flask_json import FlaskJSON, json_response
from flask_cors import CORS
import pandas as pd
import requests
import json
import datetime
import locale
from dotenv import dotenv_values
import mappings
import config
import sys

env = dotenv_values(".env")

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

port = env['APP_PORT']
host = env['APP_HOST']
api_version = env['API_VERSION']
api_version_dev = env['API_VERSION_DEV']
url_subpath = env['URL_SUBPATH']
demo_koha_api_public = env["DEMO_KOHA_API_PUBLIC"]
prod_koha_api_public = env["PROD_KOHA_API_PUBLIC"]
prod_koha_api_auth = env["PROD_KOHA_API_AUTH"]
prod_koha_api_prive = env["PROD_KOHA_API_PRIVE"]

mapping_codes_types_pret = mappings.MAPPING_CODES_TYPES_PRET
mapping_bibs = mappings.MAPPING_BIBS
mapping_locs = mappings.MAPPING_LOCS
bibs_order = config.BIBS_ORDER
bibs_order_by_label = config.BIBS_ORDER_BY_LABEL
resanavette_bibs_true = config.RESANAVETTE_BIBS_TRUE
resa_bibs_true = config.RESA_BIBS_TRUE
resa_codes_pret_true = config.RESA_CODES_PRET_TRUE

# Set the locale to French
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

# Voir https://stackoverflow.com/questions/30743696/create-proxy-for-python-flask-application
# The ReverseProxied class is a middleware for a WSGI application that handles reverse proxy headers.
# It dynamically adapts Flask converted url of static files (/static/js...) + templates html href
# links according to the url app path after the hostname (set in .env)
class ReverseProxied(object):
    def __init__(self, app, script_name=None, scheme=None, server=None):
        self.app = app
        self.script_name = script_name
        self.scheme = scheme
        self.server = server

    def __call__(self, environ, start_response):
        if (
            script_name := environ.get('HTTP_X_SCRIPT_NAME', '')
            or self.script_name
        ):
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        if scheme := environ.get('HTTP_X_SCHEME', '') or self.scheme:
            environ['wsgi.url_scheme'] = scheme
        if server := environ.get('HTTP_X_FORWARDED_SERVER', '') or self.server:
            environ['HTTP_HOST'] = server
        return self.app(environ, start_response)

FlaskJSON(app)
api = Api(app, title='SCD-UCA Middleware Koha-Primo', api_version='1.0', api_spec_url='/api/swagger', base_path=f'{host}:{port}')
app.wsgi_app = ReverseProxied(app.wsgi_app, script_name=url_subpath)

@api.representation('application/json')
def output_json(data, code):
    return json_response(data_=data, status_=code)

################ HELPERS FUNCTIONS ######################
#########################################################

def convert_to_french_date(date_string):
    # Convert the date string to a datetime object
    date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    return date.strftime('%d %B %Y')

def resa_button_rules(items):
    libraries = [x.get('home_library_id') for x in items]
    codes_pret = [x.get('item_type_id') for x in items]
    if any(x in libraries for x in resanavette_bibs_true) & any(
        x in codes_pret for x in resa_codes_pret_true
    ):
        return "Réservation/Navette interBU"
    elif (
        all(x not in libraries for x in resanavette_bibs_true)
        & any(x in libraries for x in resa_bibs_true)
        & any(x in codes_pret for x in resa_codes_pret_true)
    ):
        return "Réservation"
    else:
        return "no button"

def extract_koha_item(item):
    # TODO vérifier le fonctionnement de checked out date
    # TODO revoir la détection des périodiques (ne plus s'appuyer sur HDL dans le code barre)
    # Exemple de réponse de la route publique de l'API Koha biblios/{biblio_id}/items (version 21.11 ; à vérifier en 23.11)
    # [{"acquisition_date":"2009-11-04",
    # "biblio_id":402754,               => biblionumber. Utilisé
    # "callnumber":"330.155 6 SEN",     => cote. Utilisé
    # "checked_out_date":null,          => date de prêt. Utilisé
    # "copy_number":null,
    # "damaged_status":0,
    # "effective_item_type_id":"NOR",
    # "effective_not_for_loan_status":0,
    # "external_id":"0962065252",        => code-barre. Utilisé
    # "holding_library_id":"SJA",        => bibliothèque effective (<> bibliothèque d'appartenance en cas de transfert). Utilisé
    # "home_library_id":"SJA",           => bibliothèque d'appartenance. Utilisé
    # "item_id":731974,
    # "item_type_id":"NOR",              => type de prêt. Utilisé
    # "location":"ECO",                  => localisation. Utilisé
    # "lost_status":0,
    # "not_for_loan_status":0,           => statut exclu du prêt. Utilisé pour repérer les états de collection
    # "public_notes":null,
    # "restricted_status":null,
    # "serial_issue_number":null,        => description. Utilisé
    # "uri":null,
    # "withdrawn":0}]
    result = {'biblio_id': item['biblio_id']}
    # s'il n'y a pas de date de retour et si le doc n'est pas en transfert -> disponible
    if (item['checked_out_date'] is None) & (item["holding_library_id"] == item["home_library_id"]):
        result['availability'] = 'Disponible'
    # s'il n'y a pas de date de retour et si le doc est en transfert -> indisponible
    elif (item['checked_out_date'] is None) & (item["holding_library_id"] != item["home_library_id"]):
        result['availability'] = 'Indisponible : en transit'
    # sinon (ie s'il y a une date de retour) -> indisponible
    #elif item['checked_out_date'] is not None:
    else:
        checked_out_date = convert_to_french_date(item['checked_out_date'])
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
    if item["not_for_loan_status"] = "2":
        result["serial_issue_number"] = f"Etat de collection : {item['serial_issue_number']}"
    elif item["serial_issue_number"] is not None:
        result["serial_issue_number"] =  item["serial_issue_number"]
    return result

def request_on_koha_api(biblio_id):
    url = f"{prod_koha_api_public}biblios/{biblio_id}/items"
    response = requests.request("GET", url).text
    data = json.loads(response)
    return [x for x in data if x["home_library_id"] != "BIBEL"]

def flatten(l):
    return [item for sublist in l for item in sublist]


################### API CLASSES ############################
############################################################

# The class "HelloWorld" is a resource that returns a JSON response with the message "Hello world"
# when a GET request is made.
class HelloWorld(Resource):
    def get(self):
        # Default to 200 OK
        return jsonify({'msg': 'Hello world'})
    
# It takes a biblio_id as input, and returns a list of converted items associated with that biblio_id
class InitKohaApiPubliqueBibliosItems(Resource):
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

# It takes a biblio_id as input, and returns a list of converted items associated with that biblio_id
class KohaApiPubliqueBibliosItems(Resource):
    @swagger.doc({
    })
    def get(self):
        biblio_ids = request.args.get("biblio_ids")
        datas = flatten([request_on_koha_api(id) for id in biblio_ids.split(",") if request_on_koha_api(id)])    
        ordered_data = sorted(datas, key=lambda x: bibs_order[x.get('home_library_id')])
        new_data = [extract_koha_item(i) for i in ordered_data]
        resa_button = resa_button_rules(datas)
        final_data = {"resa_button": resa_button, "items": new_data}
        return jsonify(final_data)
    
# It takes one biblio_id or a string of biblio_ids separated with comma as input, and returns a list of converted items associated with that biblio_id + the calculated value of the resarvation button to display (or not)
class DevKohaApiPubliqueBibliosItems(Resource):
    @swagger.doc({
    })
    def get(self):
        biblio_ids = request.args.get("biblio_ids")
        datas = flatten([request_on_koha_api(id) for id in biblio_ids.split(",") if request_on_koha_api(id)])    
        ordered_data = sorted(datas, key=lambda x: bibs_order[x.get('home_library_id')])
        new_data = [extract_koha_item(i) for i in ordered_data]
        resa_button = resa_button_rules(datas)
        final_data = {"resa_button": resa_button, "items": new_data}
        return jsonify(final_data)


api.add_resource(HelloWorld, f'/api/{api_version}', f'/api/{api_version}/hello')      
#api.add_resource(InitKohaApiPubliqueBibliosItems, f'/api/{api_version}/koha/biblios_items/<string:biblio_id>')
api.add_resource(KohaApiPubliqueBibliosItems, f'/api/{api_version}/koha/biblios_items')
#api.add_resource(DevKohaApiPubliqueBibliosItems, f'/api/{api_version_dev}/koha/biblios_items')

if __name__ == '__main__':
    app.run(debug=True,port=port,host=host)
