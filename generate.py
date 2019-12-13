import urllib
import json
import pandas as pd
from pandas.io.json import json_normalize
from rdflib  import URIRef, BNode, Literal, Graph
from rdflib import Namespace
from rdflib.namespace import RDF, FOAF, RDFS, XSD
from datetime import datetime

#api key = 57ab2bbab8dda80e00969c4ea12d6debcaddd956 for jsdeux api
#let's create RDF in TURTLE------------------------------------

# namesoaces we will use
ex = Namespace('http://www.semweb.com/2001-schema#')
mobVoc = Namespace('http://schema.mobivoc.org/')
geoNames = Namespace('http://www.geonames.org/ontology#')
addr = Namespace('http://schemas.tails.com/2005#adresss/schema#')
geo = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
vcard = Namespace('http://www.w3.org/2006/vcard/ns#')
stPty = Namespace('http://www.semweb.org/2006/BycicleStation/property#')

#create defaultgraph
g = Graph()

cities = ['valence', 'marseille', 'lyon', 'nantes', 'toulouse']

for city in cities:
    #request ti api
    url = urllib.request.urlopen('https://api.jcdecaux.com/vls/v1/stations?contract='+str(city)+'&apiKey=57ab2bbab8dda80e00969c4ea12d6debcaddd956')
    #loaded data
    data = json.loads(url.read().decode(url.info().get_param('charset') or 'utf-8'))
    #parse loaded and generate rdf turtle
    for i in range(len(data)):
            URIReff = URIRef('http://www.semweb.com/URIRef/'+data[i]['contract_name']+'/'+str(data[i]['number']))
            name = Literal(data[i]['name'], datatype=XSD.string)
            city = Literal(data[i]['contract_name'], lang='fr')
            address = Literal(data[i]['address'], lang="fr")
            lat = Literal(data[i]['position']['lat'], datatype = XSD.decimal)
            lon = Literal(data[i]['position']['lng'], datatype = XSD.decimal)
            avaibility = BNode()

            avail_bikes = Literal(data[i]['available_bikes'], datatype = XSD.integer)
            total_bikes = Literal(data[i]['bike_stands'], datatype = XSD.integer)
            banking = Literal(data[i]['banking'], datatype = XSD.boolean)
            date = Literal("12-09-2019T13:05", datatype = XSD.date)
            status = Literal(data[i]['status'], datatype = XSD.string)
            last_update = Literal(datetime.fromtimestamp(data[i]['last_update']/1000).strftime('%Y-%m-%dT%I:%M:%S'), datatype = XSD.dateTime)

            #here name space manager.

            g.namespace_manager.bind('geo', geo, override=False)
            g.namespace_manager.bind('vcard', vcard, override=False)
            g.namespace_manager.bind('geoNames', geoNames, override=False)
            g.namespace_manager.bind('addr', addr, override=False)
            g.namespace_manager.bind('mobVoc', mobVoc, override=False)
            g.namespace_manager.bind('ex', ex, override=False)
            g.namespace_manager.bind('stPty', stPty, override=False)

            #adding prepared static data to graph
            g.add((URIReff, RDF.type, mobVoc.BikeParkingStation))
            g.add((URIReff, RDFS.label, name))
            g.add((URIReff, addr.streetAdress, address))
            g.add((URIReff, vcard.inCity, city))
            g.add((URIReff, geo.lat, lat))
            g.add((URIReff, geo.lon, lon))
            #adding dynamic prepared data to graph(blank node)
            g.add((URIReff, ex.hasAvaibility, avaibility))
            g.add((avaibility, RDF.type, mobVoc.Avaibility))
            g.add((avaibility, stPty.avBicyce, avail_bikes))
            g.add((avaibility, stPty.totBicycle, total_bikes))
            g.add((avaibility, stPty.paymentCard, banking))
            g.add((avaibility, stPty.status, status))
            g.add((avaibility, stPty.lastUpdate, last_update))

g.serialize(destination='byke_data.ttl',format="turtle")
print('byke_data.ttl generated')

#-----------------here i found some data about allowed terasse in toulouse. It is very poor data. I need some time to improve
with open('terrasses-autorisees-ville-de-toulouse.geojson') as f:
    data = json.load(f)

ex = Namespace('http://www.semweb.com/2001-schema#')
tur = Namespace('http://schema.tur.org/')
addr = Namespace('http://schemas.tails.com/2005#adresss/schema#')
geo = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
vcard = Namespace('http://www.w3.org/2006/vcard/ns#')
g = Graph()
from urllib.parse import quote

for i in range(len(data[0]['features'])):

            try:
                URIReff = URIRef(quote('<http://semweb.com/get/'+data[0]['features'][i]['properties']['code_int']['id']+'>'))
            except KeyError:
                continue
            city = Literal(data[0]['features'][i]['properties']['commune'], lang='fr')
            domain_activite = (data[0]['features'][i]['properties']['domaine_activite'])
            address = Literal(data[0]['features'][i]['properties']['nom_voie'], lang="fr")
            try:
                nature_activite = Literal(data[0]['features'][i]['properties']['nature_activite'], lang='fr')
            except KeyError:
                continue

            lat = Literal(data[0]['features'][i]['properties']['x'], datatype = XSD.decimal)
            lon = Literal(data[0]['features'][i]['properties']['y'], datatype = XSD.decimal)


            g.namespace_manager.bind('geo', geo, override=False)
            g.namespace_manager.bind('vcard', vcard, override=False)
            g.namespace_manager.bind('addr', addr, override=False)
            g.namespace_manager.bind('tur', tur, override=False)
            g.namespace_manager.bind('ex', ex, override=False)

            g.add((URIReff, RDF.type, tur.Restraunte))
            g.add((URIReff, addr.streetAdress, address))
            g.add((URIReff, vcard.inCity, city))
            g.add((URIReff, geo.lat, lat))
            g.add((URIReff, geo.lon, lon))
            g.add((URIReff, RDFS.comment, nature_activite))


#anyway we are adding terasse data to triplestore
g.serialize(destination='terasse.ttl',format="turtle")
