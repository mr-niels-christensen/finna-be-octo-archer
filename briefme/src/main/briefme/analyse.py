import rdflib
from rdflib.namespace import DCTERMS, RDF, RDFS
from collections import Counter
from langdetect import detect
import logging
import urllib2
import json
from langdetect.lang_detect_exception import LangDetectException

from briefme import cache

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
    '''Determines the language of the text.
       @param text: A text in string or unicode
       @return Language code for the text (e.g. 'en') or None.
    '''
    try:
        return detect(text)
    except LangDetectException:
        return None

def brief(dbpedia_item):
    '''Creates a "brief" for the given Item.
       Analyses DBpedia and updates the Item with progress,
       thumbnail and English texts.
       @param dbpedia_item: An Item for a DBpedia resource.
    '''
    #Parse the graph of facts about the main subject (identified by the Item's external_url)
    g = rdflib.Graph()
    g.parse(format = 'n3', data = cache.get_uri(dbpedia_item.external_url()))
    dbpedia_item.set_progress(0.1)
    #Extract thumbnail and title
    thumbnail_url = g.value(subject = dbpedia_item.uriref(), predicate = _THUMBNAIL_PREDICATE)
    dbpedia_item.set_thumbnail_url(thumbnail_url)
    dbpedia_item.set_title(g.value(subject = dbpedia_item.uriref(), predicate = RDFS.label))
    #Accumulate related resources and count how many relations each has to the main subject
    total = Counter()
    _add_immediate_connections(dbpedia_item.uriref(), g, total)
    dbpedia_item.set_progress(0.2)
    _add_friends(list(g.objects(dbpedia_item.uriref(), DCTERMS.subject)), total, dbpedia_item)
    dbpedia_item.set_progress(0.6)
    #Collect abstracts of the 10 most related resources (normally topped by the main subject)
    result = list()
    for (index, (friend, _score)) in enumerate(total.most_common(10)):
        _add_en_abstract_of(friend, result)
        dbpedia_item.set_progress(0.6 + 0.03*index)

    dbpedia_item.set_progress(0.9)
    #Finalize item with the list of abstracts
    dbpedia_item.set_finished_with_data(result)

def _add_en_abstract_of(uri, result):
    '''Appends two texts (rdflib.Literals) to result:
       the English label and abstract of the given uri.
       If no English abstract can be found, adds nothing.
       The label may be the empty string if no label was found.
       @param uri: URIRef of a DBpedia resource
       @param result: A list to add texts to.
    '''
    #Retrieve and parse graph, get labels and abstracts
    g = rdflib.Graph()
    g.parse(format = 'n3', data = cache.get_uri(uri))
    labels = list(g.objects(subject = uri, predicate = RDFS.label))
    abstracts = list(g.objects(predicate = rdflib.URIRef("http://dbpedia.org/ontology/abstract")))
    #If possible, find English labels and abstracts
    en_labels = [l for l in labels if l.language == 'en']
    en_abstracts = [a for a in abstracts if _safe_detect(a) == 'en']
    #Return without effect if there was no English abstract
    if len(en_abstracts) == 0:
        return
    #If there was no English label, pick one at random, or "" if no label at all
    if len(en_labels) == 0:
        en_labels = list(labels) + [""]
    result.append(en_labels[0])
    #Pick an English abstract, prerring one tagged English
    result.append(sorted(en_abstracts, key=lambda a : a.language=='en')[-1])

def _add_immediate_connections(subject, g, total):
    '''Updates total for every resource that is related to
       subject by a predicate in _PEOPLE_NW_PREDICATES
       @param subject: The subject we are counting relations to
       @param g: The rdflib.Graph to search for relations
       @param total: A Counter keeping score of the number of relations
       from subject to a resource
    '''
    for pred in _PEOPLE_NW_PREDICATES:
        for related in g.objects(subject, pred):
            if isinstance(related, rdflib.URIRef):
                total[related] += 1

def _add_friends(dc_classes, total, dbpedia_item):
    '''Updates total for every resource that is in one
       of the classes in dc_classes (on DBpedia).
       @param dc_classes: The Dublin Core classes that count
       as a relation to our main subject. Can be a generator.
       @param total: A Counter keeping score of the number of relations
       from subject to a resource
       @param dbpedia_item: Used for updating progress
    '''
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
