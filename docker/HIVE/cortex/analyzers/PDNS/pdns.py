#!/usr/bin/env python
# encoding: utf-8

from cortexutils.analyzer import Analyzer

dnsData = [{'origin': 'GrumpyCatInc Passive DNS',
            'time_first': '2011-02-22T19:06:42',
            'rrtype': 'A',
            'rrname': 'cnc.server.com',
            'rdata': '66.66.66.66',
            'time_last': '2012-02-14T10:14:53'},
            {'origin': 'GrumpyCatInc Passive DNS',
            'time_first': '2017-01-11T07:07:07',
            'rrtype': 'A',
            'rrname': 'cnc.server2.com',
            'rdata': '77.77.77.77',
            'time_last': '2017-07-17T17:17:57'}]

class BasicAnalyzer(Analyzer):
    # Analyzer's constructor
    def __init__(self):
        # Call the constructor of the super class
        Analyzer.__init__(self)
        result = {}

        if self.data_type == 'domain':
            data = self.getData()
            
            for record in dnsData:
                if record['rrname'] == data:
                    result['raw_data'] = record

        return self.report(result)


if __name__ == '__main__':
    BasicAnalyzer().run()
