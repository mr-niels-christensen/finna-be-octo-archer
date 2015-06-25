import rdflib
from rdflib.namespace import DCTERMS, RDF
from collections import Counter

import urllib2
import json
from sys import stdin
print 'Who?'
x = stdin.readline()
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
for o in g.objects(predicate = rdflib.URIRef("http://dbpedia.org/ontology/abstract")):
    if o.language == 'en':
        print o

total = Counter()

for p in [rdflib.URIRef('http://dbpedia.org/property/children'),
          rdflib.URIRef('http://dbpedia.org/property/predecessor'),
          rdflib.URIRef('http://dbpedia.org/property/successor'),
          rdflib.URIRef('http://dbpedia.org/property/deputy'),
          rdflib.URIRef('http://dbpedia.org/property/spouse')]:
    #print '-' * 40
    #print p
    for o in g.objects(rdflib.URIRef("http://dbpedia.org/resource/Margaret_Thatcher"), p):
        total[o] += 1

#print total.most_common(10)
print '.',

for p in [DCTERMS.subject, 
          #RDF.type, 
          rdflib.URIRef('http://dbpedia.org/property/profession'),
          rdflib.URIRef('http://dbpedia.org/property/office'),
          rdflib.URIRef('http://dbpedia.org/property/wordnet_type')]:
    #print '-' * 40
    #print p
    for o in g.objects(s, p):
        #print u"--> {}".format(o)
        print '.',
        try:
            gg = rdflib.Graph()
            gg.parse(unicode(o))
            part = Counter()
            for oo in gg.subjects(p, o):
                part[oo] += 1
            #print sum(part.values())
            total += part
            #print sum(part.values())
        except Exception as e:
            print e
        #print total.most_common(2)

print

for (uriref, no) in total.most_common(10):
    print u'{}: {}'.format(no, unicode(uriref))

