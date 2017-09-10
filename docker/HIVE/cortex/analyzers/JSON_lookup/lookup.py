#!/usr/bin/env python
# encoding: utf-8
import json
from cortexutils.analyzer import Analyzer

with open('cnc_servers') as data_file:
    data = json.load(data_file)

class BasicAnalyzer(Analyzer):
    # Analyzer's constructor
    def __init__(self):
        # Call the constructor of the super class
        Analyzer.__init__(self)
        result = {}

        if self.data_type == 'ip':
            input_data = self.getData()
            
            for event in data:
                if event['address']:
                    if event['address'][0]['ip'] == input_data:
                        result['raw_data'] = event

        return self.report(result)


if __name__ == '__main__':
    BasicAnalyzer().run()
