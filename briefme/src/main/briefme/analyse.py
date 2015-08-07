import rdflib
from rdflib.namespace import DCTERMS, RDF, RDFS
from collections import Counter
from langdetect import detect
import logging
import urllib2
import json
from langdetect.lang_detect_exception import LangDetectException
import unicodedata as ud

from briefme.webgraph import WebGraph

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


_latin_letters= {}

def _is_latin(uchr):
    try: return _latin_letters[uchr]
    except KeyError:
         return _latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))

def _only_roman_chars(unistr):
    return all(_is_latin(uchr)
           for uchr in unistr
           if uchr.isalpha())

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
    g = WebGraph(dbpedia_item.external_url(), fail_if_not_loaded = True)
    dbpedia_item.set_progress(0.1)
    #Extract thumbnail and title
    thumbnail_url = g.value(subject = dbpedia_item.uriref(), predicate = _THUMBNAIL_PREDICATE)
    dbpedia_item.set_thumbnail_url(thumbnail_url)
    dbpedia_item.set_title(_best_label(g, dbpedia_item.uriref()))
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
    _add_intro(result, dbpedia_item.title)
    _add_extro(result, dbpedia_item.title)
    #Finalize item with the list of abstracts
    dbpedia_item.set_finished_with_data(result)

_STD_INTRO_TEMPLATE = 'This brief will first cover {}, then move on to a few related stories, like {} and {}. All content is provided by Wikipedia. Thank you!'
_ALT_INTRO_TEMPLATE = 'All content is provided by Wikipedia. Thank you!'

def _add_intro(label_abstract_list, title):
    '''Adds two strings, welcome message and introduction, to the label_abstract_list.
       @param label_abstract_list A even-length list of the form label0, abstract0, label1, abstract1,...
       @param title The title of the item.
    '''
    first_labels = label_abstract_list[0:5:2]
    intro = _ALT_INTRO_TEMPLATE if len(first_labels) < 3 else _STD_INTRO_TEMPLATE.format(*first_labels)
    label_abstract_list.insert(0, 'Welcome to the brief on {}.'.format(title))
    label_abstract_list.insert(1, intro)

def _add_extro(label_abstract_list, title):
    '''Adds one strings, an extro message, to the label_abstract_list.
       @param label_abstract_list A even-length list of the form label0, abstract0, label1, abstract1,...
       @param title The title of the item.
    '''
    label_abstract_list.append('This ends the brief on {}. Thank you for listening.'.format(title))

def _best_label(g, uri):
    '''Look up all labels for uri in g, return the best choice for English.
       @param g An rdflib graph
       @param uri The subject to find a label for
       @return An English RDFS.label, if possible, else one with Roman letters only,
       if possible, else "".
    '''
    labels = list(g.objects(subject = uri, predicate = RDFS.label))
    en_labels = [l for l in labels if l.language == 'en']
    #If there was no English label, pick a Roman-only one at random, or "" if no label at all
    if len(en_labels) == 0:
        en_labels = [l for l in labels if _only_roman_chars(l)] + [""]
    return en_labels[0]

def _add_en_abstract_of(uri, result):
    '''Appends two texts (rdflib.Literals) to result:
       the English label and abstract of the given uri.
       If no English abstract can be found, adds nothing.
       The label may be the empty string if no label was found.
       @param uri: URIRef of a DBpedia resource
       @param result: A list to add texts to.
    '''
    #Retrieve and parse graph, get labels and abstracts
    g = WebGraph(uri)
    abstracts = list(g.objects(predicate = rdflib.URIRef("http://dbpedia.org/ontology/abstract")))
    #If possible, find English abstracts
    en_abstracts = [a for a in abstracts if _safe_detect(a) == 'en']
    #Return without effect if there was no English abstract
    if len(en_abstracts) == 0:
        return
    result.append(_best_label(g, uri))
    #Pick an English abstract, preferring one tagged English
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
        dc_class_graph = WebGraph(dc_class)
        for friend in dc_class_graph.subjects(DCTERMS.subject, dc_class):
            total[friend] += 1
        dbpedia_item.set_progress(0.2 + 0.4*index/len(dc_classes) )

