import rdflib
from rdflib.namespace import DCTERMS, RDF
from collections import Counter
from langdetect import detect
import logging
import urllib2
import json
import cache

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
    g.parse(format = 'n3', data = cache.get_uri(iri))
    total = Counter()
    _add_immediate_connections(rdflib.URIRef(iri), g, total)
    _add_friends(list(g.objects(rdflib.URIRef(iri), DCTERMS.subject)), total)
    result = [_en_abstract_of(friend) for (friend, _score) in total.most_common(10)]
    cache.set_content_for_main_subject(iri, result)

def _en_abstract_of(uri):
    g = rdflib.Graph()
    g.parse(format = 'n3', data = cache.get_uri(uri))
    for abstract in g.objects(predicate = rdflib.URIRef("http://dbpedia.org/ontology/abstract")):
        if detect(abstract) == 'en':
            return abstract

def _add_immediate_connections(subject, g, total):
    for pred in _PEOPLE_NW_PREDICATES:
        for related in g.objects(subject, pred):
            if isinstance(related, rdflib.URIRef):
                total[related] += 1

def _add_friends(dc_classes, total):
    for dc_class in dc_classes:
        try:
            dc_class_graph = rdflib.Graph()
            dc_class_graph.parse(format = 'n3', data = cache.get_uri(dc_class))
            for friend in dc_class_graph.subjects(DCTERMS.subject, dc_class):
                total[friend] += 1
        except Exception as e:
            logging.warn(e)

