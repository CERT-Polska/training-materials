"""
============================
WebServices Client API
============================

This class provides a client API for all the GeoIP2 Precision web service end
points. The end points are Country, City, and Insights. Each end point returns
a different set of data about an IP address, with Country returning the least
data and Insights the most.

Each web service end point is represented by a different model class, and
these model classes in turn contain multiple record classes. The record
classes have attributes which contain data about the IP address.

If the web service does not return a particular piece of data for an IP
address, the associated attribute is not populated.

The web service may not return any information for an entire record, in which
case all of the attributes for that record class will be empty.

SSL
---

Requests to the GeoIP2 Precision web service are always made with SSL.

"""

import geoip2
import geoip2.models
import requests
from requests.utils import default_user_agent
from .errors import (AddressNotFoundError, AuthenticationError,
                     GeoIP2Error, HTTPError, InvalidRequestError,
                     OutOfQueriesError)

import sys

if sys.version_info[0] == 2 or (sys.version_info[0] == 3
                                and sys.version_info[1] < 3):
    import ipaddr as ipaddress  # pylint:disable=F0401
    ipaddress.ip_address = ipaddress.IPAddress
else:
    import ipaddress  # pylint:disable=F0401


class Client(object):

    """Creates a new client object.

    It accepts the following required arguments:

    :param user_id: Your MaxMind User ID.
    :param license_key: Your MaxMind license key.

    Go to https://www.maxmind.com/en/my_license_key to see your MaxMind
    User ID and license key.

    The following keyword arguments are also accepted:

    :param host: The hostname to make a request against. This defaults to
      "geoip.maxmind.com". In most cases, you should not need to set this
      explicitly.
    :param locales: This is list of locale codes. This argument will be
      passed on to record classes to use when their name properties are
      called. The default value is ['en'].

      The order of the locales is significant. When a record class has
      multiple names (country, city, etc.), its name property will return
      the name in the first locale that has one.

      Note that the only locale which is always present in the GeoIP2
      data is "en". If you do not include this locale, the name property
      may end up returning None even when the record has an English name.

      Currently, the valid locale codes are:

      * de -- German
      * en -- English names may still include accented characters if that is
        the accepted spelling in English. In other words, English does not
        mean ASCII.
      * es -- Spanish
      * fr -- French
      * ja -- Japanese
      * pt-BR -- Brazilian Portuguese
      * ru -- Russian
      * zh-CN -- Simplified Chinese.

    """

    def __init__(self, user_id, license_key, host='geoip.maxmind.com',
                 locales=None):
        if locales is None:
            locales = ['en']
        self._locales = locales
        self._user_id = user_id
        self._license_key = license_key
        self._base_uri = 'https://%s/geoip/v2.1' % host

    def city(self, ip_address='me'):
        """This method calls the GeoIP2 Precision City endpoint.

        :param ip_address: IPv4 or IPv6 address as a string. If no
           address is provided, the address that the web service is
           called from will be used.

        :returns: :py:class:`geoip2.models.City` object

        """
        return self._response_for('city', geoip2.models.City, ip_address)

    def country(self, ip_address='me'):
        """This method calls the GeoIP2 Country endpoint.

        :param ip_address: IPv4 or IPv6 address as a string. If no address
          is provided, the address that the web service is called from will
          be used.

        :returns: :py:class:`geoip2.models.Country` object

        """
        return self._response_for('country', geoip2.models.Country,
                                  ip_address)

    def insights(self, ip_address='me'):
        """This method calls the GeoIP2 Precision: Insights endpoint.

        :param ip_address: IPv4 or IPv6 address as a string. If no address
          is provided, the address that the web service is called from will
          be used.

        :returns: :py:class:`geoip2.models.Insights` object

        """
        return self._response_for('insights', geoip2.models.Insights,
                                  ip_address)

    def _response_for(self, path, model_class, ip_address):
        if ip_address != 'me':
            ip_address = str(ipaddress.ip_address(ip_address))
        uri = '/'.join([self._base_uri, path, ip_address])
        response = requests.get(uri, auth=(self._user_id, self._license_key),
                                headers={'Accept': 'application/json',
                                         'User-Agent': self._user_agent()})
        if response.status_code == 200:
            body = self._handle_success(response, uri)
            return model_class(body, locales=self._locales)
        else:
            self._handle_error(response, uri)

    def _user_agent(self):
        return 'GeoIP2 Python Client v%s (%s)' % (geoip2.__version__,
                                                  default_user_agent())

    def _handle_success(self, response, uri):
        try:
            return response.json()
        except ValueError as ex:
            raise GeoIP2Error('Received a 200 response for %(uri)s'
                              ' but could not decode the response as '
                              'JSON: ' % locals() +
                              ', '.join(ex.args), 200, uri)

    def _handle_error(self, response, uri):
        status = response.status_code

        if 400 <= status < 500:
            self._handle_4xx_status(response, status, uri)
        elif 500 <= status < 600:
            self._handle_5xx_status(status, uri)
        else:
            self._handle_non_200_status(status, uri)

    def _handle_4xx_status(self, response, status, uri):
        if not response.content:
            raise HTTPError('Received a %(status)i error for %(uri)s '
                            'with no body.' % locals(), status, uri)
        elif response.headers['Content-Type'].find('json') == -1:
            raise HTTPError('Received a %i for %s with the following '
                            'body: %s' %
                            (status, uri, response.content),
                            status, uri)
        try:
            body = response.json()
        except ValueError as ex:
            raise HTTPError(
                'Received a %(status)i error for %(uri)s but it did'
                ' not include the expected JSON body: ' % locals() +
                ', '.join(ex.args), status, uri)
        else:
            if 'code' in body and 'error' in body:
                self._handle_web_service_error(
                    body.get('error'), body.get('code'), status, uri)
            else:
                raise HTTPError(
                    'Response contains JSON but it does not specify '
                    'code or error keys', status, uri)

    def _handle_web_service_error(self, message, code, status, uri):
        if code in ('IP_ADDRESS_NOT_FOUND', 'IP_ADDRESS_RESERVED'):
            raise AddressNotFoundError(message)
        elif code in ('AUTHORIZATION_INVALID', 'LICENSE_KEY_REQUIRED',
                      'USER_ID_REQUIRED'):
            raise AuthenticationError(message)
        elif code == 'OUT_OF_QUERIES':
            raise OutOfQueriesError(message)

        raise InvalidRequestError(message, code, status, uri)

    def _handle_5xx_status(self, status, uri):
        raise HTTPError('Received a server error (%(status)i) for '
                        '%(uri)s' % locals(), status, uri)

    def _handle_non_200_status(self, status, uri):
        raise HTTPError('Received a very surprising HTTP status '
                        '(%(status)i) for %(uri)s' % locals(), status,
                        uri)
"""

:copyright: (c) 2014 by MaxMind, Inc.
:license: Apache License, Version 2.0

"""
