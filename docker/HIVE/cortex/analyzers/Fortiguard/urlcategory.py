#!/usr/bin/env python
# encoding: utf-8


import re
import requests
from cortexutils.analyzer import Analyzer


class URLCategoryAnalyzer(Analyzer):

    def summary(self, raw):

        taxonomies = []

        if 'category' in raw:
            r = raw.get('category')
            value = "\"{}\"".format(r)
            if r == "Malicious Websites":
                level = "malicious"
            elif r == "Suspicious Websites":
                level = "suspicious"
            elif r == "Not Rated":
                level = "info"
            else:
                level = "safe"

            taxonomies.append(self.build_taxonomy(level, "Fortiguard", "URLCat", value))

        result = {"taxonomies": taxonomies}
        return result

    def run(self):
        Analyzer.run(self)

        if self.data_type == 'domain' or self.data_type == 'url':
            try:
                pattern = re.compile("(?:Category: )([\w\s]+)")
                baseurl = 'http://www.fortiguard.com/webfilter?q='
                url = baseurl + self.getData()
                req = requests.get(url)
                category_match = re.search(pattern, req.content, flags=0)
                self.report({
                    'category': category_match.group(1)
                })
            except ValueError as e:
                self.unexpectedError(e)
        else:
            self.notSupported()

if __name__ == '__main__':
    URLCategoryAnalyzer().run()
