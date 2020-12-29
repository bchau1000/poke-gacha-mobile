# app.py

from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'PokeTable'
app.config['MONGO_URI'] = 'mongodb+srv://m001-student:OiHx3bVFmlOyMo5T@cluster0.xbjek.mongodb.net/PokeTable?retryWrites=true&w=majority'

mongo = PyMongo(app)

@app.route('/')
def default():
  return 'default page'

@app.route('/api/pokedex', methods=['GET'])
def get_all_pokemon():
  query = request.args.get('search')
  pokeData = mongo.db.pokemonData
  output = []
  if query:
    for document in pokeData.aggregate([
      {
      "$search": {
            "text": {
                    "query": query,
                    "path": "pokeName",
                    "fuzzy": {"maxEdits" : 1}#this allows only one character to be off
                    }
            }
      },
      {
        "$project":{#each field in the collection that has 1 will be returned in the iterable
          "_id":1,
          "pokeName":1
          }
      }
      ]):
        output.append({'pokeName':document['pokeName'],'id':document['_id']})
  else: #return all pokemon
    output = [{'name':document['pokeName'],'id':str(document['_id'])} for document in pokeData.find()]

  if output:
    return jsonify(output)
  else:
    return "{} Not Found".format(query)


@app.route('/api/evolution/<int:evo_id>', methods=['GET'])
def get_evo_chain_by_id (evo_id):
  evoData = mongo.db.evolutionData
  output = []
  evoDoc = evoData.find_one({"_id":evo_id})
  
  for idx,group in enumerate(evoDoc["evoTree"]):
    output.append([])
    for element in group:
      output[idx].append(
        {"id":element,
        "pokeName":group[element]})
  
  if output:
    return jsonify({'result' : output})
  else:
    return "{} Could Not Be Found".format(evo_id)


@app.route('/api/evolution/<string:pokeNameInput>', methods=['GET'])
def get_evo_chain_by_name(pokeNameInput):
  output = []
  pokeData = mongo.db.pokemonData
  evoData = mongo.db.evolutionData
  pokeDoc = pokeData.find_one({"pokeName":pokeNameInput})
  evoDoc = evoData.find_one({"_id":pokeDoc["evoChainId"]})
  
  for idx,group in enumerate(evoDoc["evoTree"]):
    output.append([])
    for element in group:
      output[idx].append(
        {
          "id":element,
          "pokeName":group[element]})
  
  if output:
    return jsonify({'result' : output})
  else:
    return "{} Not Found".format(pokeNameInput)

if __name__ == '__main__':
    app.run(debug=True)
