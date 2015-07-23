import rdflib
from rdflib.namespace import DCTERMS, RDF
from collections import Counter
from langdetect import detect
import logging
import urllib2
import json
import cache
from langdetect.lang_detect_exception import LangDetectException
from uuid import uuid4

_PEOPLE_NW_PREDICATES = [rdflib.URIRef('http://dbpedia.org/property/children'),
                         rdflib.URIRef('http://dbpedia.org/property/predecessor'),
                         rdflib.URIRef('http://dbpedia.org/property/successor'),
                         rdflib.URIRef('http://dbpedia.org/property/deputy'),
                         rdflib.URIRef('http://dbpedia.org/property/spouse')]

_META_PREDICATES = [RDF.type, #problematic
        rdflib.URIRef('http://dbpedia.org/property/profession'),
        rdflib.URIRef('http://dbpedia.org/property/office'),
        rdflib.URIRef('http://dbpedia.org/property/wordnet_type')]

#TODO: Add more documentation, and get rid of briefme.py
def brief(dbpedia_item):
    g = rdflib.Graph()
    g.parse(format = 'n3', data = cache.get_uri(dbpedia_item.external_url()))
    #for pred in g.predicates(subject = dbpedia_item.uriref()):
    #    logging.debug(pred)
    dbpedia_item.set_progress(0.1)
    total = Counter()
    _add_immediate_connections(dbpedia_item.uriref(), g, total)
    dbpedia_item.set_progress(0.2)
    _add_friends(list(g.objects(dbpedia_item.uriref(), DCTERMS.subject)), total, dbpedia_item)
    dbpedia_item.set_progress(0.6)
    result = [_en_abstract_of(friend, index, dbpedia_item) for (index, (friend, _score)) in enumerate(total.most_common(10))]
    dbpedia_item.set_progress(0.9)
    dbpedia_item.set_data(result)

def _en_abstract_of(uri, index, dbpedia_item):
    g = rdflib.Graph()
    g.parse(format = 'n3', data = cache.get_uri(uri))
    dbpedia_item.set_progress(0.6 + 0.03*index)
    for abstract in g.objects(predicate = rdflib.URIRef("http://dbpedia.org/ontology/abstract")):
        try:
            if detect(abstract) == 'en':
                return abstract
        except LangDetectException:
            pass
    return "Sorry, no description of {}".format(uri)

def _add_immediate_connections(subject, g, total):
    for pred in _PEOPLE_NW_PREDICATES:
        for related in g.objects(subject, pred):
            if isinstance(related, rdflib.URIRef):
                total[related] += 1

def _add_friends(dc_classes, total, dbpedia_item):
    for (index, dc_class) in enumerate(dc_classes):
        try:
            dc_class_graph = rdflib.Graph()
            data = cache.get_uri(dc_class)
            dc_class_graph.parse(format = 'n3', data = data)
            for friend in dc_class_graph.subjects(DCTERMS.subject, dc_class):
                total[friend] += 1
            dbpedia_item.set_progress(0.2 + 0.4*index/len(dc_classes) )
        except Exception as e:
            logging.warn(e)

