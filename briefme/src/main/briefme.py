import rdflib
from rdflib.namespace import DCTERMS, RDF
from collections import Counter
from langdetect import detect
import logging
import urllib2
import json

def brief(iri, responder):
    g = rdflib.Graph()
    logging.info('Parsing {}'.format(iri))
    g.parse(iri)
    logging.info('{} entries in {}'.format(len(g), g))
    abstracts = dict()
    for o in g.objects(predicate = rdflib.URIRef("http://dbpedia.org/ontology/abstract")):
        print '{},{}'.format(o.language, detect(o))
        abstracts[detect(o)] = o
    a = abstracts['en'] if 'en' in abstracts else abstracts[None]
    responder.writeln(a.encode('latin_1','ignore'))
    logging.info('Now for some serious crunching...')
    total = Counter()
    for p in [rdflib.URIRef('http://dbpedia.org/property/children'),
              rdflib.URIRef('http://dbpedia.org/property/predecessor'),
              rdflib.URIRef('http://dbpedia.org/property/successor'),
              rdflib.URIRef('http://dbpedia.org/property/deputy'),
              rdflib.URIRef('http://dbpedia.org/property/spouse')]:
        for o in g.objects(rdflib.URIRef("http://dbpedia.org/resource/Margaret_Thatcher"), p):
            total[o] += 1
    for p in [DCTERMS.subject, 
              #problematic RDF.type, 
              #rdflib.URIRef('http://dbpedia.org/property/profession'),
              rdflib.URIRef('http://dbpedia.org/property/office'),
              #rdflib.URIRef('http://dbpedia.org/property/wordnet_type')
              ]:
        for o in g.objects(rdflib.URIRef(iri), p):
            try:
                logging.info(unicode(o))
                gg = rdflib.Graph()
                gg.parse(unicode(o))
                part = Counter()
                for oo in gg.subjects(p, o):
                    part[oo] += 1
                total += part
            except Exception as e:
                print e
    logging.info('Crunched it!')
    for (uriref, no) in total.most_common(10):
        logging.info(u'{}: {}'.format(no, unicode(uriref)).encode('latin_1','ignore'))

