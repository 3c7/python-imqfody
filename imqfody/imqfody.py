import requests
import json

from requests.auth import HTTPBasicAuth


class FodyError(Exception):
    pass


class UnknownHandler(FodyError):
    pass


class HTTPError(FodyError):
    pass


class UnexpectedParameter(FodyError):
    pass


class IMQFody(object):
    def __init__(self, url, username, password, sslverify=True):
        object.__init__(self)
        self._url = url.rstrip('/')
        self._session = requests.session()
        self._session.auth = HTTPBasicAuth(username, password)
        self._session.verify = sslverify

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def _search(self, handler, endpoint, query):
        """Generic search method to build queries.

        :param handler: Handler on fody side: [contactdb, events, tickets, checkticket]
        :param endpoint: Specific endpoint; e.g. searchasn, searchorg etc.
        :param query: Input used for querying fody."""
        if handler not in ['contactdb', 'events', 'tickets', 'checkticket']:
            raise UnknownHandler('Handler must be one of [contactdb, events, tickets, checkticket].')
        response = self._session.get('{}/api/{}/{}'.format(self._url, handler, endpoint), data=query)
        if response.status_code != 200:
            raise HTTPError(response.status_code)
        dict_response = json.loads(response.text)
        response.close()
        return dict_response

    def _get_contacts_from_id_list(self, ids):
        """
        Get organisations by their ids, iterate over auto and manual contacts.

        :param ids: dictionary containing auto and manual ids
        :return: list of contacts
        """
        contacts = []
        for manual in ids['manual']:
            contacts.append(self._search('contactdb', 'org/manual/{}'.format(manual), {}))
        for auto in ids['auto']:
            contacts.append(self._search('contactdb', 'org/auto/{}'.format(auto), {}))
        return contacts

    def get_api_documentation(self):
        """Querying the base url returns the documentation"""
        return json.loads(self._session.get(self._url))

    # #################
    # ContactDB queries
    def ping(self):
        """
        Ping contactdb
        :return: dict
        """
        return self._search('contactdb', 'ping', {})

    def search_asn(self, asn):
        """
        Search in contactdb using an asn number

        :param asn: asn number as string
        :return: dict
        """
        result = self._search('contactdb', 'searchasn', {'asn': asn})
        return self._get_contacts_from_id_list(result)

    def search_org(self, name):
        """
        Search in contactdb using an organisation name

        :param name: organisation name to search for
        :return: dict
        """
        result = self._search('contactdb', 'searchorg', {'name': name})
        return self._get_contacts_from_id_list(result)

    def search_email(self, email):
        """
        Search in contactdb for an email

        :param email: email as string
        :return: dict
        """
        result = self._search('contactdb', 'searchcontact', {'email': email})
        return self._get_contacts_from_id_list(result)

    def search_cidr(self, cidr):
        """
        Search in contactdb using the cidr

        :param cidr: cidr as string
        :return: dict
        """
        result = self._search('contactdb', 'searchcidr', {'address': cidr})
        return self._get_contacts_from_id_list(result)

    def search_ip(self, ip):
        """
        Wrapper for search_cidr

        :param ip: ip as str
        :return: dict
        """
        return self.search_cidr(ip)

    def search_fqdn(self, fqdn):
        """
        Search in the contactdb for an fqdn.

        :param fqdn: fqdn as str
        :return: dict
        """

        result = self._search('contactdb', 'searchfqdn', {'domain': fqdn})
        return self._get_contacts_from_id_list(result)

    def search_national(self, cc):
        """
        Search through contactdb using a 2-3 letter country code

        :param cc:
        :return:
        """

        if len(cc) < 2 or len(cc) > 3:
            raise UnexpectedParameter('Country code should be 2 or 3 letters long.')
        result = self._search('contactdb', 'searchnational', {'countrycode', cc})
        return self._get_contacts_from_id_list(result)

    # #############
    # Event queries
    def get_event(self, id):
        """
        Retrieve event by id

        :param id: event id int
        :return: dict
        """
        response = self._session.get('{}/api/events'.format(self._url), data={'id': id})
        if response.status_code == 200:
            return json.loads(response.text)
        raise HTTPError('Statuscode: {}'.format(response.status_code))

    def get_event_subqueries(self):
        """
        Return dictionary of event subqueries

        :return: dict
        """
        return self._search('events', 'subqueries', {})

    def search_event(self, subquery):
        """
        Search for events by a subquery.

        :param subquery: dict subquery
        :return: dict
        """
        return self._search('events', 'search', subquery)

