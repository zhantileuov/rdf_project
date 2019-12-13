from flask import Flask, render_template, jsonify
from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST, CSV
import urllib
import json
import pandas as pd
from pandas.io.json import json_normalize
from rdflib  import URIRef, BNode, Literal, Graph, Namespace
from rdflib.namespace import RDF, FOAF, RDFS, XSD
from datetime import datetime
#@app.route('/points', methods=['GET'])
app = Flask(__name__)

@app.route('/points', methods=['GET'])
def data():
    sparql = SPARQLWrapper("http://localhost:3030/current/")
    sparql.setQuery(''' PREFIX addr: <http://schemas.tails.com/2005#adresss/schema#>
                        PREFIX ex: <http://www.semweb.com/2001-schema#>
                        PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
                        PREFIX geoNames: <http://www.geonames.org/ontology#>
                        PREFIX mobVoc: <http://schema.mobivoc.org/>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX stPty: <http://www.semweb.org/2006/BycicleStation/property#>
                        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
                        PREFIX xml: <http://www.w3.org/XML/1998/namespace>
                        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                        select ?lat ?lon ?name ?avByc ?totByc ?status ?streetAddr ?creditCard ?lastupdate
                        where{
                                ?x  rdfs:label         ?name ;
                                addr:streetAdress  ?streetAddr ;
                                ex:hasAvaibility   [stPty:avBicyce     ?avByc ;
                                 stPty:lastUpdate   ?lastupdate ;
                                 stPty:paymentCard  ?creditCard ;
                                 stPty:status       ?status ;
                                 stPty:totBicycle   ?totByc
                               ] ;
                               geo:lat            ?lat ;
                               geo:lon            ?lon ;
     }'''
                        )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    lst = []
    geoJson = {}
    for i in range(len(results['results']['bindings'])):
        g =   dict({ "type": "Feature",
             "properties": {
             "name": results['results']['bindings'][i]['name']['value'],
             "address": results['results']['bindings'][i]['streetAddr']['value'],
             "lat": results['results']['bindings'][i]['lat']['value'],
             "lng": results['results']['bindings'][i]['lon']['value'],
             "status": results['results']['bindings'][i]['status']['value'],
             "available_bike": results['results']['bindings'][i]['avByc']['value'],
             "total": results['results']['bindings'][i]['totByc']['value'],
             "banking": results['results']['bindings'][i]['creditCard']['value'],
             "last_update": results['results']['bindings'][i]['lastupdate']['value'], },
             "geometry": {
             "type": "Point",
             "coordinates": [ float(results['results']['bindings'][i]['lon']['value']),
                              float(results['results']['bindings'][i]['lat']['value']) ] } },)
        lst.append(g)
        geoJson = {"type": "FeatureCollection",
                    "name": "jcd_jcdecaux.jcdvelov",'features': lst}

    response = app.response_class(
        response=json.dumps(geoJson),
        status=200,
        mimetype='application/json'
    )
    return response
@app.route('/update')
def update():
    cities = ['valence', 'marseille', 'lyon', 'nantes', 'toulouse']
#sparql = SPARQLWrapper("http://localhost:3030/eldiyar/update")
    for city in cities:
        url = urllib.request.urlopen('https://api.jcdecaux.com/vls/v1/stations?contract='+str(city)+'&apiKey=57ab2bbab8dda80e00969c4ea12d6debcaddd956')
        data = json.loads(url.read().decode(url.info().get_param('charset') or 'utf-8'))
        for i in range(len(data)):
            sparql = SPARQLWrapper("http://localhost:3030/history/")
            URIReff = ('<http://www.semweb.com/URIRef/'+data[i]['contract_name']+'/'+str(data[i]['number'])+'>')
            avail_bikes = data[i]['available_bikes']
            last_update = datetime.fromtimestamp(data[i]['last_update']/1000).strftime('%Y-%m-%dT%R')
            sparql.setQuery('''PREFIX ex: <http://www.semweb.com/2001-schema#>
                               PREFIX mobVoc: <http://schema.mobivoc.org/>
                               PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
                               PREFIX stPty: <http://www.semweb.org/2006/BycicleStation/property#>
                               INSERT DATA {''' + URIReff + '''ex:hasAvaibility   [ a   mobVoc:Avaibility ; ;
                                                                                 stPty:avBicyce     %d ;
                                                                                 stPty:lastUpdate   "%s"^^xsd:dateTime ;
                                                                                 stPty:paymentCard  %s ;
                                                                                 stPty:status       "%s" ;
                                                                                 stPty:totBicycle   %d
                                                                                 ]
                           }'''%( avail_bikes, last_update, data[i]['banking'], data[i]['status'], data[i]['bike_stands'],
                                        )

                        )
            sparql.setMethod(POST)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

    return jsonify({'results':'updated'})


@app.route('/update_current')
def update_current():
    cities = ['valence', 'marseille', 'lyon', 'nantes', 'toulouse']
    #sparql = SPARQLWrapper("http://localhost:3030/eldiyar/update")
    for city in cities:
        url = urllib.request.urlopen('https://api.jcdecaux.com/vls/v1/stations?contract='+str(city)+'&apiKey=57ab2bbab8dda80e00969c4ea12d6debcaddd956')
        data = json.loads(url.read().decode(url.info().get_param('charset') or 'utf-8'))
        for i in range(len(data)):
            sparql = SPARQLWrapper("http://localhost:3030/current/")
            URIReff = ('<http://www.semweb.com/URIRef/'+data[i]['contract_name']+'/'+str(data[i]['number'])+'>')
            avail_bikes = data[i]['available_bikes']
            last_update = datetime.fromtimestamp(data[i]['last_update']/1000).strftime('%Y-%m-%dT%R')
            sparql.setQuery('''PREFIX ex: <http://www.semweb.com/2001-schema#>
                               PREFIX mobVoc: <http://schema.mobivoc.org/>
                               PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
                               PREFIX stPty: <http://www.semweb.org/2006/BycicleStation/property#>
                                DELETE {
                                        ?s  ex:hasAvaibility   ?o .
                                        ?o  ?p1  ?o1 .
                                        }
                                WHERE {
                                        VALUES (?s) { (''' + URIReff + ''') }
                                        ?s  ex:hasAvaibility  ?o .
                                        OPTIONAL {
                                        ?o  ?p1  ?o1  .
                                        FILTER (isBlank(?o))
                                            }
                                            }'''

                        )
            sparql.setMethod(POST)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            sparql.setQuery(''' PREFIX ex: <http://www.semweb.com/2001-schema#>
                                PREFIX mobVoc: <http://schema.mobivoc.org/>
                                PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
                                PREFIX stPty: <http://www.semweb.org/2006/BycicleStation/property#>
                                INSERT DATA {''' + URIReff + '''ex:hasAvaibility   [ a mobVoc:Avaibility ; ;
                                                                                    stPty:avBicyce     %d ;
                                                                                    stPty:lastUpdate   "%s"^^xsd:dateTime ;
                                                                                    stPty:paymentCard  %s ;
                                                                                    stPty:status       "%s" ;
                                                                                    stPty:totBicycle   %d
                                                                                    ]
                           }'''%( avail_bikes, last_update, data[i]['banking'], data[i]['status'], data[i]['bike_stands'],
                                        )

                        )
            sparql.setMethod(POST)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()



    return jsonify({'results':'updated'})

@app.route('/current_jsonld', methods=['GET'])
def current_jsonld():
    sparql = SPARQLWrapper("http://localhost:3030/current/")
    sparql.setQuery(''' PREFIX addr: <http://schemas.tails.com/2005#adresss/schema#>
                        PREFIX ex: <http://www.semweb.com/2001-schema#>
                        PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
                        PREFIX geoNames: <http://www.geonames.org/ontology#>
                        PREFIX mobVoc: <http://schema.mobivoc.org/>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX stPty: <http://www.semweb.org/2006/BycicleStation/property#>
                        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
                        PREFIX xml: <http://www.w3.org/XML/1998/namespace>
                        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                        select ?lat ?lon ?name ?avByc ?totByc ?status ?streetAddr ?creditCard ?lastupdate
                        where{
                                ?x  rdfs:label         ?name ;
                                addr:streetAdress  ?streetAddr ;
                                ex:hasAvaibility   [stPty:avBicyce     ?avByc ;
                                 stPty:lastUpdate   ?lastupdate ;
                                 stPty:paymentCard  ?creditCard ;
                                 stPty:status       ?status ;
                                 stPty:totBicycle   ?totByc
                               ] ;
                               geo:lat            ?lat ;
                               geo:lon            ?lon ;
     }'''
                        )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return jsonify(results)

@app.route('/rest_tolous')
def rest_tolous():
    from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST, CSV


    sparql = SPARQLWrapper("http://localhost:3030/rest/")
    sparql.setQuery('''PREFIX addr: <http://schemas.tails.com/2005#adresss/schema#>
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select ?lat ?lon ?name  ?streetAddr ?comment
    where{
            ?x
                addr:streetAdress  ?streetAddr ;
                rdfs:comment       ?comment;
                geo:lat            ?lat ;
                geo:lon            ?lon ;
         }'''

                            )



    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    lst=[]
    geoJson = {}
    for i in range(len(results['results']['bindings'])):
            g =   dict({ "type": "Feature",
                         "properties": {
                         "address": results['results']['bindings'][i]['streetAddr']['value'],
                         "comment": results['results']['bindings'][i]['comment']['value'],},
                         "geometry": {
                         "type": "Point",
                         "coordinates": [ float(results['results']['bindings'][i]['lat']['value']),
                                  float(results['results']['bindings'][i]['lon']['value']) ] } })
            lst.append(g)
            geoJson = {"type": "FeatureCollection",
                        "name": "jcd_jcdecaux.jcdvelov",'features': lst}

    response = app.response_class(
        response=json.dumps(geoJson),
        status=200,
        mimetype='application/json'
    )
    return response



@app.route('/')
def main():
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
