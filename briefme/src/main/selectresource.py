import json
import urllib2

def lookup(phrase):
    #TODO move to web page
    req = urllib2.Request('http://lookup.dbpedia.org/api/search/KeywordSearch?QueryString={}'.format(phrase), None, {'Accept': 'application/json'})
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()
    data = json.loads(response)
    #http://dbpedia.org/resource/Margaret_Thatcher
    #http://dbpedia.org/resource/Augustus
    return data["results"]

