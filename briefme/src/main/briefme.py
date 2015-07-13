import rdflib
from rdflib.namespace import DCTERMS, RDF
from collections import Counter
from langdetect import detect

import urllib2
import json

def brief(x, responder):
    req = urllib2.Request('http://lookup.dbpedia.org/api/search/KeywordSearch?MaxHits=1&QueryString={}'.format(x), None, {'Accept': 'application/json'})
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()
    data = json.loads(response)
    #s = rdflib.URIRef("http://dbpedia.org/resource/Margaret_Thatcher")
    #s = rdflib.URIRef("http://dbpedia.org/resource/Augustus")
    s = rdflib.URIRef(data["results"][0]["uri"])
    g = rdflib.Graph()
    g.parse(unicode(s))
    abstracts = dict()
    for o in g.objects(predicate = rdflib.URIRef("http://dbpedia.org/ontology/abstract")):
        print '{},{}'.format(o.language, detect(o))
        abstracts[detect(o)] = o
    a = abstracts['en'] if 'en' in abstracts else abstracts[None]
    responder.writeln(a.encode('latin_1','ignore'))

    total = Counter()

    for p in [rdflib.URIRef('http://dbpedia.org/property/children'),
              rdflib.URIRef('http://dbpedia.org/property/predecessor'),
              rdflib.URIRef('http://dbpedia.org/property/successor'),
              rdflib.URIRef('http://dbpedia.org/property/deputy'),
              rdflib.URIRef('http://dbpedia.org/property/spouse')]:
        for o in g.objects(rdflib.URIRef("http://dbpedia.org/resource/Margaret_Thatcher"), p):
            total[o] += 1

    for p in [#DCTERMS.subject, 
              #problematic RDF.type, 
              #rdflib.URIRef('http://dbpedia.org/property/profession'),
              rdflib.URIRef('http://dbpedia.org/property/office'),
              #rdflib.URIRef('http://dbpedia.org/property/wordnet_type')
              ]:
        for o in g.objects(s, p):
            try:
                logging.info(unicode(o))
                gg = rdflib.Graph()
                gg.parse(unicode(o))
                part = Counter()
                for oo in gg.subjects(p, o):
                    part[oo] += 1
                total += part
            except Exception as e:
                print e
    for (uriref, no) in total.most_common(10):
        responder.writeln(u'{}: {}'.format(no, unicode(uriref)).encode('latin_1','ignore'))

