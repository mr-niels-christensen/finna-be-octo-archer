import rdflib
from rdflib.namespace import DCTERMS, RDF
from collections import Counter
from langdetect import detect
import logging
import urllib2
import json

_PEOPLE_NW_PREDICATES = [rdflib.URIRef('http://dbpedia.org/property/children'),
                         rdflib.URIRef('http://dbpedia.org/property/predecessor'),
                         rdflib.URIRef('http://dbpedia.org/property/successor'),
                         rdflib.URIRef('http://dbpedia.org/property/deputy'),
                         rdflib.URIRef('http://dbpedia.org/property/spouse')]

_META_PREDICATES = [RDF.type, #problematic
        rdflib.URIRef('http://dbpedia.org/property/profession'),
        rdflib.URIRef('http://dbpedia.org/property/office'),
        rdflib.URIRef('http://dbpedia.org/property/wordnet_type')]

def brief(iri):
    g = rdflib.Graph()
    g.parse(iri)
    a = 'Sorry, no description.'
    for o in g.objects(predicate = rdflib.URIRef("http://dbpedia.org/ontology/abstract")):
        if detect(o) == 'en':
            a = o
    return {'abstract' : a, 'friends'  : _friends_of(rdflib.URIRef(iri), g)}

def _friends_of(subject, g):
    total = Counter()
    for pred in _PEOPLE_NW_PREDICATES:
        for related in g.objects(subject, pred):
            if isinstance(related, rdflib.URIRef):
                total[related] += 1
    dc_classes = list(g.objects(subject, DCTERMS.subject))
    dc_classes = dc_classes[:12]
    for dc_class in dc_classes:
        try:
            gg = rdflib.Graph()
            gg.parse(unicode(dc_class))
            part = Counter()
            for oo in gg.subjects(DCTERMS.subject, dc_class):
                part[oo] += 1
            total += part
        except Exception as e:
            logging.warn(e)
    return total.most_common(10)

