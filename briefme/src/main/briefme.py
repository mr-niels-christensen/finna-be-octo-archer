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

def brief(dbpedia_item):
    uuid = uuid4()
    logging.debug('BEGIN brief {} for {}'.format(uuid, dbpedia_item))
    g = rdflib.Graph()
    logging.debug('STATUS brief {} for {}: ready to parse'.format(uuid, dbpedia_item))
    g.parse(format = 'n3', data = cache.get_uri(dbpedia_item.external_url()))
    dbpedia_item.set_progress(0.1)
    total = Counter()
    logging.debug('STATUS brief {} for {}: ready to _add_immediate_connections'.format(uuid, dbpedia_item))
    _add_immediate_connections(rdflib.URIRef(dbpedia_item.external_url()), g, total)
    dbpedia_item.set_progress(0.3)
    logging.debug('STATUS brief {} for {}: ready to _add_friends'.format(uuid, dbpedia_item))
    _add_friends(list(g.objects(rdflib.URIRef(dbpedia_item.external_url()), DCTERMS.subject)), total)
    dbpedia_item.set_progress(0.8)
    logging.debug('STATUS brief {} for {}: ready to get abstracts'.format(uuid, dbpedia_item))
    result = [_en_abstract_of(friend) for (friend, _score) in total.most_common(10)]
    dbpedia_item.set_progress(0.9)
    logging.debug('STATUS brief {} for {}: ready to set content'.format(uuid, dbpedia_item))    
    dbpedia_item.set_data(result)
    logging.debug('END brief {} for {}'.format(uuid, dbpedia_item))

def _en_abstract_of(uri):
    g = rdflib.Graph()
    g.parse(format = 'n3', data = cache.get_uri(uri))
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

def _add_friends(dc_classes, total):
    for dc_class in dc_classes:
        try:
            dc_class_graph = rdflib.Graph()
            data = cache.get_uri(dc_class)
            dc_class_graph.parse(format = 'n3', data = data)
            for friend in dc_class_graph.subjects(DCTERMS.subject, dc_class):
                total[friend] += 1
        except Exception as e:
            logging.warn(e)

