import rdflib
from rdflib.namespace import DCTERMS, RDF
from collections import Counter
from langdetect import detect
import logging
import urllib2
import json

def brief(iri, responder):
    g = rdflib.Graph()
    g.parse(iri)
    abstracts = dict()
    a = 'Sorry, no description.'
    for o in g.objects(predicate = rdflib.URIRef("http://dbpedia.org/ontology/abstract")):
        if detect(o) == 'en':
            a = o
    responder.writeln(a.encode('latin_1','ignore'))
    total = Counter()
    for p in [rdflib.URIRef('http://dbpedia.org/property/children'),
              rdflib.URIRef('http://dbpedia.org/property/predecessor'),
              rdflib.URIRef('http://dbpedia.org/property/successor'),
              rdflib.URIRef('http://dbpedia.org/property/deputy'),
              rdflib.URIRef('http://dbpedia.org/property/spouse')]:
        for o in g.objects(rdflib.URIRef(iri), p):
            if isinstance(o, rdflib.URIRef):
                total[o] += 1
    #problematic RDF.type, 
    #rdflib.URIRef('http://dbpedia.org/property/profession'),
    #rdflib.URIRef('http://dbpedia.org/property/office'),
    #rdflib.URIRef('http://dbpedia.org/property/wordnet_type')
    edges = list(g.objects(rdflib.URIRef(iri), DCTERMS.subject))
    logging.info('{} edges, selecting a few'.format(len(edges)))
    edges = edges[:12]
    logging.info(repr(edges))
    for o in edges:
        try:
            gg = rdflib.Graph()
            gg.parse(unicode(o))
            part = Counter()
            for oo in gg.subjects(DCTERMS.subject, o):
                part[oo] += 1
            total += part
        except Exception as e:
            logging.warn(e)
    logging.info(repr(total.most_common(10)))

