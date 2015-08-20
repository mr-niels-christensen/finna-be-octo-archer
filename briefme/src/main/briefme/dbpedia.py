import rdflib
from rdflib import namespace

class DBpediaResource(object):
    def __init__(self):
        self._graph = rdflib.Graph()
        self._graph.bind('OWL', namespace.OWL)
        self._graph.bind('FOAF', namespace.FOAF)
        self._graph.bind('DC', namespace.DC)
        self._graph.bind('DCTERMS', namespace.DCTERMS)
        self._graph.bind('PROP', 'http://dbpedia.org/property/')
        self._graph.bind('RES', 'http://dbpedia.org/resource/')
        self._graph.bind('ONT', 'http://dbpedia.org/ontology/')

    @staticmethod
    def for_name(name):
        url = 'http://dbpedia.org/resource/{}'.format(name)
        res = DBpediaResource()
        res._graph.bind('I', url)
        res._graph.parse(url)
        return res

    def _get(self, predicate_qname):
        (pref, name) = predicate_qname.split(':')
        qname = None
        for prefix, namespace in self._graph.namespaces():
            if pref == prefix:
                for (s,o) in self._graph[:rdflib.URIRef(name, base = namespace)]:
                    yield (self._graph.qname(s), self._graph.qname(o))
                return
        raise Exception('{} not recognized as a prefix, in {}'.format(pref, predicate_qname))

if __name__ == '__main__':
    res = DBpediaResource.for_name('Titan_(moon)')
    print res._graph.serialize(format="n3")


