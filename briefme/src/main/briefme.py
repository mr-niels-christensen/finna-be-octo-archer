import rdflib
from rdflib.namespace import DCTERMS, RDF, RDFS
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

_THUMBNAIL_PREDICATE = rdflib.URIRef('http://dbpedia.org/ontology/thumbnail')

def _safe_detect(text):
    try:
        return detect(text)
    except LangDetectException:
        return None

#TODO: Add more documentation, and get rid of briefme.py
def brief(dbpedia_item):
    g = rdflib.Graph()
    g.parse(format = 'n3', data = cache.get_uri(dbpedia_item.external_url()))
    dbpedia_item.set_progress(0.1)
    thumbnail = g.value(subject = dbpedia_item.uriref(), predicate = _THUMBNAIL_PREDICATE)
    dbpedia_item.set_thumbnail(thumbnail)
    dbpedia_item.set_title(g.value(subject = dbpedia_item.uriref(), predicate = RDFS.label))
    total = Counter()
    _add_immediate_connections(dbpedia_item.uriref(), g, total)
    dbpedia_item.set_progress(0.2)
    _add_friends(list(g.objects(dbpedia_item.uriref(), DCTERMS.subject)), total, dbpedia_item)
    dbpedia_item.set_progress(0.6)
    result = list()
    for (index, (friend, _score)) in enumerate(total.most_common(10)):
        _add_en_abstract_of(friend, index, dbpedia_item, result)
    dbpedia_item.set_progress(0.9)
    dbpedia_item.set_data(result)

def _add_en_abstract_of(uri, index, dbpedia_item, result):
    g = rdflib.Graph()
    g.parse(format = 'n3', data = cache.get_uri(uri))
    labels = g.objects(subject = uri, predicate = RDFS.label)
    en_labels = [l for l in labels if l.language == 'en']
    dbpedia_item.set_progress(0.6 + 0.03*index)
    abstracts = g.objects(predicate = rdflib.URIRef("http://dbpedia.org/ontology/abstract"))
    en_abstracts = [a for a in abstracts if _safe_detect(a) == 'en']
    if len(en_abstracts) == 0:
        return
    if len(en_labels) == 0:
        en_labels = labels + [""]
    result.append([en_labels[0], sorted(en_abstracts, key=lambda a : a.language=='en')[-1]])

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

