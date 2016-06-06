#!/usr/bin/env python
# encoding: utf-8
'''
csw_esgf_search.search -- shortdesc

csw_esgf_search.search is a description

It defines classes_and_methods

'''
__all__ = []
__version__ = 0.1
__date__ = '2016-05-27'
__updated__ = '2016-05-27'
from xml.etree import ElementTree
import logging

import requests
from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore

log = logging.getLogger(__name__)


class CCIODPSearch:
    SPARQL_QUERY_URI = 'http://{}/sparql' 
    SPARQL_GRAPH_URI = 'http://{}/vocab/data/cci'
    # This allows us to use the prefix values in the queries rather than the url
    SPARQL_QUERY_PREFIXES = """
    PREFIX dc:  <http://purl.org/dc/elements/1.1/>
    PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX skos:  <http://www.w3.org/2004/02/skos/core#>
    """
    
    def __init__(self, csw_uri, esgf_search_uri, sparql_hostname):
        self.csw_uri = csw_uri
        self.esgf_search_uri = esgf_search_uri
        self.sparql_hostname = sparql_hostname
        self.sparql_graph = self.set_graph()
        
    def csw_query(self, csw_query):
        resp = requests.post(self.csw_uri,
                             headers={'Content-type': 'application/xml'},
                             data=csw_query)

        tree = ElementTree.fromstring(resp.content)
        
        print(resp.content)
        
        md_metadata_elems = tree.findall(
                            './/{http://www.isotc211.org/2005/gmd}MD_Metadata')
        
        search_results = []
        for md_metadata_elem in md_metadata_elems:
            search_result = {}
            title_elem = md_metadata_elem.find(
                    './/{http://www.isotc211.org/2005/gmd}MD_DataIdentification'
                    '/{http://www.isotc211.org/2005/gmd}citation'
                    '/{http://www.isotc211.org/2005/gmd}CI_Citation'
                    '/{http://www.isotc211.org/2005/gmd}title'
                    '/{http://www.isotc211.org/2005/gco}CharacterString')
            
            search_result['title'] = title_elem.text
            
            abstract_elem = md_metadata_elem.find(
                            './/{http://www.isotc211.org/2005/gmd}abstract/'
                            '{http://www.isotc211.org/2005/gco}CharacterString')
            search_result['abstract'] = abstract_elem.text
             
            anchor_elems = md_metadata_elem.findall(
                                './/{http://www.isotc211.org/2005/gmx}Anchor')
            search_result['vocab_terms'] = []
            for anchor_elem in anchor_elems:
                vocab_term = anchor_elem.attrib.get(
                                        '{http://www.w3.org/1999/xlink}href')
                if vocab_term is not None:
                    search_result['vocab_terms'].append(vocab_term)
            
            search_results.append(search_result)
            
            return search_results

    def set_graph(self):
        store = SPARQLStore(endpoint=self.__class__.SPARQL_QUERY_URI.format(
                                                    self.sparql_hostname))
        self.sparql_graph = Graph(
                            store=store, 
                            identifier=self.__class__.SPARQL_GRAPH_URI.format(
                                                    self.sparql_hostname))
     
    def get_facet_names(self):
        if self.sparql_graph is None:
            self.set_graph()
            
        statement = (
            '%s SELECT ?uri ?label ?description WHERE '
            '{?uri rdf:type skos:Collection . ?uri skos:prefLabel '
            '?label . OPTIONAL{?uri dc:description ?description}} '
            'ORDER BY ASC(?label)' 
        ) % self.__class__.SPARQL_QUERY_PREFIXES
            
        log.debug('SPARQL query = %r' % statement)

        return self.sparql_graph.query(statement)

    def get_facet_values(self, facet):
        statement = (
            '%s SELECT ?uri ?label ?definition WHERE '
            '{<%s> skos:member ?uri . ?uri skos:prefLabel ?label . '
            'OPTIONAL{?uri skos:definition ?definition}} '
            'ORDER BY ASC(?label)' % (
            self.__class__.SPARQL_QUERY_PREFIXES, facet)
            )
                     
        print('SPARQL query = %r' % statement)
        return self.sparql_graph.query(statement)    
    
    def query(self, csw_query):
        search_results = self.csw_query(csw_query)
        facet_names = self.get_facet_names()
        
        for facet in facet_names:
            print('\nFacet Label: %s - hover text: %s' %
                   (facet.label, facet.description))
            for member in self.get_facet_values(facet.uri):
                print('\t%s - hover text: %s - uri: %s' % (
                                member.label, member.definition, member.uri))
           
        for search_result in search_results:
            for vocab_term in search_result['vocab_terms']:
                pass
                 
        return search_results, facet_names