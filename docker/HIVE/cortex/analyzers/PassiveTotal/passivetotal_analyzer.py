#!/usr/bin/env python
# encoding: utf-8

from cortexutils.analyzer import Analyzer

from passivetotal.libs.dns import DnsRequest
from passivetotal.libs.enrichment import EnrichmentRequest
from passivetotal.libs.ssl import SslRequest
from passivetotal.libs.whois import WhoisRequest

class PassiveTotalAnalyzer(Analyzer):

    def __init__(self):
        Analyzer.__init__(self)
        self.service = self.getParam('config.service', None, 'PassiveTotal service is missing')
        self.username = self.getParam('config.username', None, 'PassiveTotal username is missing')
        self.api_key = self.getParam('config.key', None, 'PassiveTotal API key is missing')

    def summary(self, raw):
        taxonomies = []
        level = "info"
        namespace = "PT"
        predicate = "Service"
        value = "\"False\""

        result = {}
        # malware service
        if self.service == 'malware':
            predicate = "Malware"
            if 'results' in raw and raw['results']:
                result['malware'] = True
                level = "malicious"
            else:
                result['malware'] = False
                level = "safe"
            value = "\"{}\"".format(result['malware'])
            taxonomies.append(self.build_taxonomy(level, namespace, predicate, value))

        # osint service
        elif self.service == 'osint':
            predicate = "OSINT"
            if 'results' in raw and raw['results']:
                result['osint'] = True
            else:
                result['osint'] = False
            value = "\"{}\"".format(result['osint'])
            taxonomies.append(self.build_taxonomy(level, namespace, predicate, value))

        # passive dns service
        elif self.service == 'passive_dns':
            predicate = "PassiveDNS"
            if 'totalRecords' in raw and raw['totalRecords']:
                result['total'] = raw['totalRecords']
            else:
                result['total'] = 0

            if result['total'] < 2:
                value = "\"{} record\"".format(result['total'])
            else:
                value = "\"{} records\"".format(result['total'])

            taxonomies.append(self.build_taxonomy(level, namespace, predicate, value))

        # ssl certificate details service
        elif self.service == 'ssl_certificate_details':
            predicate = "SSL"
            if 'sha1' in raw:
                result['ssl'] = True
            else:
                result['ssl'] = False
            value = "\"{}\"".format(result['ssl'])
            taxonomies.append(self.build_taxonomy(level, namespace, predicate, value))

        # ssl certificate history service
        elif self.service == 'ssl_certificate_history':
            predicate = "SSLCertHistory"
            if 'results' in raw and raw['results']:
                result['ssl'] = True
                result['total'] = len(raw['results'])
                value = "\"{} record(s)\"".format(result['total'])
                taxonomies.append(self.build_taxonomy(level, namespace, predicate, value))

        # unique resolutions service
        elif self.service == 'unique_resolutions':
            predicate = "UniqueResolution"
            if 'total' in raw:
                result['total'] = raw['total']
                value = "\"{} record(s)\"".format(result['total'])
                taxonomies.append(self.build_taxonomy(level, namespace, predicate, value))

        # whois details service
        elif self.service == 'whois_details':
            predicate = "Whois"
            if 'registrant' in raw and 'organization' in raw['registrant'] and raw['registrant']['organization']:
                result['registrant'] = raw['registrant']['organization']
                value = "\"REGISTRANT: {}\"".format(result['registrant'])
                taxonomies.append(self.build_taxonomy(level, namespace, predicate, value))
            if 'registrar' in raw and raw['registrar']:
                result['registrar'] = raw['registrar']
                value = "\"REGISTRAR: {}\"".format(result['registrar'])
                taxonomies.append(self.build_taxonomy(level, namespace, predicate, value))

        return {"taxonomies":taxonomies}

    def run(self):
        Analyzer.run(self)

        data = self.getData()

        try:
            # enrichment service
            if self.service == 'enrichment':
                enrichment_request = EnrichmentRequest(username=self.username, api_key=self.api_key)
                result = enrichment_request.get_enrichment(query=data)
                self.report(result)

            # malware service
            elif self.service == 'malware':
                enrichment_request = EnrichmentRequest(username=self.username, api_key=self.api_key)
                result = enrichment_request.get_malware(query=data)
                self.report(result)

            # osint service
            elif self.service == 'osint':
                enrichment_request = EnrichmentRequest(username=self.username, api_key=self.api_key)
                result = enrichment_request.get_osint(query=data)
                self.report(result)

            # passive dns service
            elif self.service == 'passive_dns':
                dns_request = DnsRequest(username=self.username, api_key=self.api_key)
                result = dns_request.get_passive_dns(query=data)
                self.report(result)

            # ssl certificate details service
            elif self.service == 'ssl_certificate_details':
                ssl_request = SslRequest(username=self.username, api_key=self.api_key)
                result = ssl_request.get_ssl_certificate_details(query=data)
                self.report(result)

            # ssl certificate history service
            elif self.service == 'ssl_certificate_history':
                ssl_request = SslRequest(username=self.username, api_key=self.api_key)
                result = ssl_request.get_ssl_certificate_history(query=data)
                self.report(result)

            # unique resolutions service
            elif self.service == 'unique_resolutions':
                dns_request = DnsRequest(username=self.username, api_key=self.api_key)
                result = dns_request.get_unique_resolutions(query=data)
                self.report(result)

            # whois details service
            elif self.service == 'whois_details':
                whois_request = WhoisRequest(username=self.username, api_key=self.api_key)
                result = whois_request.get_whois_details(query=data)
                self.report(result)

            else:
                self.error('Unknown PassiveTotal service')

        except Exception as e:
            self.unexpectedError(e)

if __name__ == '__main__':
    PassiveTotalAnalyzer().run()
