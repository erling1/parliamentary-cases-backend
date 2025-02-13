from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import re
from main import Voterings_Oversikt_Stortinget

app = Flask(__name__)
CORS(app)

client = MongoClient('localhost', 27017)
db = client['political_cases']
collection = db['cases']

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = collection.find({'$or': [{'tittel': {'$regex': re.compile(query, re.IGNORECASE)}},
                                       {'korttittel': {'$regex': re.compile(query, re.IGNORECASE)}}]}).limit(10)
    
    return jsonify([{
        'id': doc['id'],
        'tittel': doc['tittel'],
        'korttittel': doc['korttittel'],
        'status' : doc['status'],
        'type': doc['type']
    } for doc in results])

@app.route('/stemmeresultat', methods=['GET'])
def stemmeresultat():
    sak_id = request.args.get('id', '')
    if not sak_id:
        return jsonify([])
    
    sak = Voterings_Oversikt_Stortinget(sak_id)

    #Dicts that returns 
    oversikt, info, enstemmig_vedtatt = sak.resultat()

    print(type(info))

    
    
    
    proposal = {}

    if not enstemmig_vedtatt:
    
        for key in oversikt.keys():

            

            voting_data = {
                    'representatives': [],
                    'information' : info,
                    'proposedBy' : 'proposed_by'
                }
                
            

            for i in range(len(oversikt[key]["navn"])):
                rep = {
                        'name': oversikt[key]['navn'][i],
                        'party': oversikt[key]['parti'][i],
                        'vote': oversikt[key]['votering'][i]
                    }
                voting_data['representatives'].append(rep)
                
            voting_data['voting_counts'] = {
                                'for': sum(1 for rep in voting_data['representatives'] if rep.get('vote', '').lower() == 'for'),
                                'mot': sum(1 for rep in voting_data['representatives'] if rep.get('vote', '').lower() == 'mot'),
                                'ikke_tilstede': sum(1 for rep in voting_data['representatives'] if rep.get('vote', '').lower() == 'ikke_tilstede')
                            }
                
            proposal[key] = voting_data

    else:
            
            proposal = {"result": "Enstemmig vedtatt",
                        "info" : info}
            print(info)
        


            
    return proposal


if __name__ == '__main__':
    app.run(port=5000, debug=True)