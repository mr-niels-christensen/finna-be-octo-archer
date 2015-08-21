import rdflib
from rdflib import namespace

class DBpediaResource(object):
    def __init__(self):
        self._graph = rdflib.Graph()
        self._graph.bind('OWL', 'http://www.w3.org/2002/07/owl#')
        self._graph.bind('FOAF', namespace.FOAF)
        self._graph.bind('DC', namespace.DC)
        self._graph.bind('DCTERMS', namespace.DCTERMS)
        self._graph.bind('PROP', 'http://dbpedia.org/property/')
        self._graph.bind('RES', 'http://dbpedia.org/resource/')
        self._graph.bind('CAT', 'http://dbpedia.org/resource/Category:')
        self._graph.bind('UMBELRC', 'http://umbel.org/umbel/rc/')
        self._graph.bind('YAGO', 'http://dbpedia.org/class/yago/')
        self._graph.bind('ONT', 'http://dbpedia.org/ontology/')
        self._graph.bind('PROV', 'http://www.w3.org/ns/prov#')

    @staticmethod
    def for_name(name, lang='en'):
        url = 'http://dbpedia.org/resource/{}'.format(name)
        res = DBpediaResource()
        res._graph.bind('I', url)
        res._graph.parse(url)
        res._rm_other_languages(lang)
        res._rm_admin_triples()
        return res

    @staticmethod
    def category_for_name(name, lang='en'):
        url = 'http://dbpedia.org/resource/Category:{}'.format(name)
        res = DBpediaResource()
        res._graph.bind('I', url)
        res._graph.parse(url)
        res._rm_other_languages(lang)
        res._rm_admin_triples()
        return res

    @staticmethod
    def yago_for_name(name, lang='en'):
        url = 'http://dbpedia.org/class/yago/{}'.format(name)
        res = DBpediaResource()
        res._graph.bind('I', url)
        res._graph.parse(url)
        res._rm_other_languages(lang)
        res._rm_admin_triples()
        return res

    def _rm_other_languages(self,lang = 'en'):
        for (s, p, o) in self._graph:
            if isinstance(o, rdflib.Literal):
                if o.language not in [lang, None]:
                    self._graph.remove((s, p, o))

    def _rm_admin_triples(self):
        for qname in ['ONT:wikiPageDisambiguates', 
                      'ONT:wikiPageRedirects', 
                      'ONT:wikiPageID', 
                      'ONT:wikiPageRevisionID', 
                      'OWL:differentFrom', 
                      'OWL:sameAs', 
                      'FOAF:primaryTopic' ,
                      'FOAF:isPrimaryTopicOf', 
                      'PROV:wasDerivedFrom']:
            p = self._to_uriref(qname)
            print p
            for (s, o) in self._graph[:p]:
                self._graph.remove((s, p, o))

    def _to_uriref(self, qname):
        (pref, name) = qname.split(':')
        for prefix, namespace in self._graph.namespaces():
            if pref == prefix:
                return rdflib.URIRef(unicode(namespace) + unicode(name))
        raise Exception('{} not recognized as a prefix, in {}'.format(pref, qname))


    def _get(self, predicate_qname):
        for (s,o) in self._graph[:self._to_uriref(predicate_qname)]:
            yield (self._simplify(s), self._simplify(o))

    def _simplify(self, uri):
        if isinstance(uri, rdflib.Literal):
            return uri
        try:
            return self._graph.qname(uri)
        except:
            ns = {namespace : prefix for (prefix, namespace) in self._graph.namespaces()}
            if uri in ns:
                return ns[uri]
            return unicode(uri)

if __name__ == '__main__':
    #res = DBpediaResource.for_name('Titan_(moon)')
    #res = DBpediaResource.category_for_name('Moons_of_Saturn')
    res = DBpediaResource.yago_for_name('Planet109394007')
    print res._graph.serialize(format="n3")



