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

def brief(iri):
    uuid = uuid4()
    logging.debug('BEGIN brief {} for {}'.format(uuid, iri))
    cache.set_content_for_main_subject(iri, "")
    g = rdflib.Graph()
    logging.debug('STATUS brief {} for {}: ready to parse'.format(uuid, iri))
    g.parse(format = 'n3', data = cache.get_uri(iri))
    total = Counter()
    logging.debug('STATUS brief {} for {}: ready to _add_immediate_connections'.format(uuid, iri))
    _add_immediate_connections(rdflib.URIRef(iri), g, total)
    logging.debug('STATUS brief {} for {}: ready to _add_friends'.format(uuid, iri))
    _add_friends(list(g.objects(rdflib.URIRef(iri), DCTERMS.subject)), total)
    logging.debug('STATUS brief {} for {}: ready to get abstracts'.format(uuid, iri))
    result = [_en_abstract_of(friend) for (friend, _score) in total.most_common(10)]
    logging.debug('STATUS brief {} for {}: ready to set content'.format(uuid, iri))    
    cache.set_content_for_main_subject(iri, result)
    logging.debug('END brief {} for {}'.format(uuid, iri))

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

