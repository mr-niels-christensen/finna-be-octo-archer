import json
import urllib2

def lookup(x, responder):
    req = urllib2.Request('http://lookup.dbpedia.org/api/search/KeywordSearch?QueryString={}'.format(x), None, {'Accept': 'application/json'})
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()
    data = json.loads(response)
    #s = rdflib.URIRef("http://dbpedia.org/resource/Margaret_Thatcher")
    #s = rdflib.URIRef("http://dbpedia.org/resource/Augustus")
    for result in data["results"]:
        responder.writeln(u'{}: {}'.format(result["label"], result["uri"]))

