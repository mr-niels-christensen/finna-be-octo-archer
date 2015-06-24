import rdflib
from rdflib.namespace import DCTERMS, RDF

g = rdflib.Graph()
g.parse("http://dbpedia.org/resource/Margaret_Thatcher")
for o in g.objects(predicate = rdflib.URIRef("http://dbpedia.org/ontology/abstract")):
    if o.language == 'en':
        print o
for p in [DCTERMS.subject, 
          RDF.type, 
          rdflib.URIRef('http://dbpedia.org/property/profession'),
          rdflib.URIRef('http://dbpedia.org/property/office'),
          rdflib.URIRef('http://dbpedia.org/property/spouse'),
          rdflib.URIRef('http://dbpedia.org/property/children'),
          rdflib.URIRef('http://dbpedia.org/property/predecessor'),
          rdflib.URIRef('http://dbpedia.org/property/successor'),
          rdflib.URIRef('http://dbpedia.org/property/deputy'),
          rdflib.URIRef('http://dbpedia.org/property/spouse'),
          rdflib.URIRef('http://dbpedia.org/property/wordnet_type')]:
    print '-' * 40
    print p
    for o in g.objects(rdflib.URIRef("http://dbpedia.org/resource/Margaret_Thatcher"), p):
        print o


