'''
Created on May 26, 2016

@author: philipkershaw
'''
import unittest
import os

import requests


from csw_esgf_search.search import CCIODPSearch

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class CCIODPSearchTestCase(unittest.TestCase):

    SPARQL_HOSTNAME = None
    with open(os.path.join(THIS_DIR, 'sparql_hostname.txt'), 
              'r') as sparql_hostname_file:
        SPARQL_HOSTNAME = sparql_hostname_file.read().strip()
        del sparql_hostname_file
        
    CSW_URI = None
    with open(os.path.join(THIS_DIR, 'csw_uri.txt'), 'r') as csw_uri_file:
        CSW_URI = csw_uri_file.read().strip()
        del csw_uri_file
    
    CSW_GET_RECORDS_QUERY = None
    with open(os.path.join(THIS_DIR, 'csw_query.xml'), 'r') as csw_query_file:
        CSW_GET_RECORDS_QUERY = csw_query_file.read().strip()
        del csw_query_file

    def test01_csw_get_records(self):
        resp = requests.post(self.__class__.CSW_URI,
                             headers={'Content-type': 'application/xml'},
                             data=self.__class__.CSW_GET_RECORDS_QUERY)
        self.assertTrue(resp, 'null response')

    def test02_csw_get_records_parse_content(self):
        search = CCIODPSearch(self.__class__.CSW_URI, None, None)
        
        search_results = search.csw_query(self.__class__.CSW_GET_RECORDS_QUERY)
        
        self.assertTrue(search_results, 'null search')
        print('{}'.format(search_results))

    def test02_query(self):
        search = CCIODPSearch(self.__class__.CSW_URI, None,
                              self.__class__.SPARQL_HOSTNAME) 
        
        search_results = search.query(self.__class__.CSW_GET_RECORDS_QUERY)
        
        self.assertTrue(search_results, 'null search')
        print('{}'.format(search_results))
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test01']
    unittest.main()