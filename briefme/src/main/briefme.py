import rdflib

g = rdflib.Graph()
g.parse("http://dbpedia.org/resource/Margaret_Thatcher")
print("graph has %s statements." % len(g))
for (s,p,o) in g:
    print u'{} {} {}'.format(s,p,o) 
for o in g.objects(predicate = rdflib.URIRef("http://dbpedia.org/ontology/abstract")):
    if o.language == 'en':
        print o
