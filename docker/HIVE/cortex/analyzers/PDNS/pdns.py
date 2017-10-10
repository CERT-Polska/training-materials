#!/usr/bin/env python
# encoding: utf-8

from cortexutils.analyzer import Analyzer

dnsData = [{'origin': 'GrumpyCatInc Passive DNS',
            'time_first': '2011-02-22T19:06:42',
            'rrtype': 'A',
            'rrname': 'deadly-ursa.enisa.ex',
            'rdata': '10.34.1.16',
            'time_last': '2012-02-14T10:14:53'},
            {'origin': 'GrumpyCatInc Passive DNS',
            'time_first': '2017-01-11T07:07:07',
            'rrtype': 'A',
            'rrname': 'deadly-ursa.enisa.ex',
            'rdata': '10.34.1.22',
            'time_last': '2017-07-17T17:17:57'}]

class BasicAnalyzer(Analyzer):
    # Analyzer's constructor
    def __init__(self):
        # Call the constructor of the super class
        Analyzer.__init__(self)
        result = {}
        results = []

        if self.data_type == 'domain':
            data = self.getData()
            
            for record in dnsData:
                if record['rrname'] == data:
                    results.append(record)
            result['raw_data'] = results
        
        if self.data_type == 'ip':
            data = self.getData()
            
            for record in dnsData:
                if record['rdata'] == data:
                    results.append(record)
            result['raw_data'] = results
        

        return self.report(result)


if __name__ == '__main__':
    BasicAnalyzer().run()
