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


class IMQFody:
    def __init__(self, url, username, password, sslverify=True):
        self._url = url.rstrip('/')
        self._session = requests.session()
        self._session.verify = sslverify
        self._credentials = username, password
        self._login()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def _login(self):
        """Implement new token based auth."""
        response = self._session.post(
            f"{self._url}/api/login", data={
                "username": self._credentials[0],
                "password": self._credentials[1]
            }
        )
        if response.status_code != 200:
            raise HTTPError(f"Fody returned invalid HTTP response: {response.status_code} - {response.text}")

        response_data = response.json()
        if "login_token" not in response_data:
            raise KeyError(f"Fody API should have returned a login token, but hasn't.")
        self._session.headers.update({"Authorization": response_data["login_token"]})

    def _search(self, handler, endpoint, query):
        """Generic search method to build queries.

        :param handler: Handler on fody side: [contactdb, events, tickets, checkticket]
        :param endpoint: Specific endpoint; e.g. searchasn, searchorg etc.
        :param query: Input used for querying fody."""
        if handler not in ['contactdb', 'events', 'tickets', 'checkticket']:
            raise UnknownHandler('Handler must be one of [contactdb, events, tickets, checkticket].')
        response = self._session.get('{}/api/{}/{}'.format(self._url, handler, endpoint), data=query)
        if response.status_code != 200:
            raise HTTPError(f"Fody returned {response.status_code}: {response.text}")
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

        :param cc: 2 to 3 letter Country code
        :return: dict
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
            return response.json()[0]
        raise HTTPError('Statuscode {} while getting event by id.'.format(response.status_code))

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

    def get_event_stats(self, subquery):
        """
        Returns distribution of events for a given subquery

        :param subquery: dict subquery
        :return: dict
        """
        return self._search('events', 'stats', subquery)

    def export_events(self, subquery):
        """
        Exports events matching the subquery

        :param subquery: dict subquery
        :return: dict
        """
        return self._search('events', 'export', subquery)

    # ##############
    # Ticket queries
    def get_ticket(self, id):
        """
        Get ticket by id

        :param id: ticket id
        :return: dict
        """
        response = self._session.get('{}/api/tickets'.format(self._url), data={'id': id})
        if response.status_code == 200:
            return response.json()
        raise HTTPError('Statuscode {} while getting ticket by id.'.format(response.status_code))

    def get_ticket_subqueries(self):
        """
        Returns a dict of subqueries.

        :return: dict
        """
        return self._search('tickets', 'subqueries', {})

    def search_ticket(self, subquery):
        """
        Search for tickets matching the subquery

        :param subquery: dict subquery
        :return: dict
        """
        return self._search('tickets', 'search', subquery)

    def get_ticket_stats(self, subquery):
        """
        Get a statistic tickets matching the subquery.

        :param subquery: dict subquery
        :return: dict
        """
        return self._search('tickets', 'stats', subquery)

    def get_ticket_recipient(self, ticket_number):
        """
        Get the recipient for a given ticket.

        :param ticket_number: ticket number
        :return: dict
        """
        return self._search('tickets', 'getRecipient', {'ticketnumber': ticket_number})

    def get_ticket_event_ids(self, ticket_number):
        """
        Get eventIds for a ticket.

        :param ticket_number: ticket number
        :return: dict
        """
        return self._search('checkticket', 'getEventIDsForTicket', {'ticket': ticket_number})

    def get_ticket_events(self, ticket_number, limit=0):
        """
        Get events for a ticket

        :param ticket_number: ticket number
        :param limit: limits the output to [limit] events, default 0
        :return: dict
        """
        self._search('checkticket', 'getEventsForTicket', {'ticket': ticket_number, 'limit': limit})

    def get_last_ticket_number(self):
        """
        Returns the last ticket number
        :return: dict
        """
        return self._search('checkticket', 'getLastTicketNumber', {})
