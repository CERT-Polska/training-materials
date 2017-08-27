#!/usr/bin/env python
# encoding: utf-8
from elasticsearch import Elasticsearch
from cortexutils.analyzer import Analyzer

es = Elasticsearch('10.34.1.20')



# Define analyzer's class
class BasicAnalyzer(Analyzer):
    # Analyzer's constructor
    def __init__(self):
        # Call the constructor of the super class
        Analyzer.__init__(self)

        result = {}
        es_result = []
        es_result_ = []

        if self.data_type == 'ip':
            data = self.getData()
            res = es.search(index="intelmq", doc_type="events", body={"query": {"match": {"source_ip": data }}})
            for doc in res['hits']['hits']:
                es_result.append(doc['_source']['source_ip'])
                es_result_.append(doc['_source'])
            result['source_ips'] = list(set(es_result))
            result['raw_data'] = es_result_

        # Return the report
        return self.report(result)

    def summary(self, raw_report):
        return {
            'count': len(raw_report['raw_data'])
        }

#    def artifacts(self, raw_report):
#        result = []
#        if 'findings' in raw_report:            
#            for item in raw_report['findings']:
#                result.append({'type': self.data_type, 'value': item})            

#        return result

# Invoke the analyzer
if __name__ == '__main__':
    BasicAnalyzer().run()
