"""client functions"""

from datetime import datetime

import requests
from pytz import timezone
from requests.auth import AuthBase

from inky_emt.model import Arrival, ArrivalInfo

API_TZ = timezone('Europe/Madrid')
_BASE_URL = 'https://openapi.emtmadrid.es/v1'


def _adapt_timestamp(ts):
    """
    Convert timestamps returned by the API to datetime objects.
    API returns milliseconds timestamps in Europe/Madrid tz.
    :param ts: the timestamp as a millisecond timestamp in Europe/Madrid tz
    :return: a tz-aware datetime object.
    """
    ts_seconds = int(ts / 1000)
    utc_ts = datetime.fromtimestamp(ts_seconds, API_TZ)
    return utc_ts - utc_ts.utcoffset()


def _current_date_str():
    now = datetime.now(API_TZ)
    return now.strftime("%Y%m%d")


def _validate_response(response):
    if not response.ok:
        response.raise_for_status()
    response_json = response.json()
    response_code = response_json['code']
    if response_code not in ['00', '01', '02']:
        raise Exception('Request failed: ' + response_json['description'])
    return


def _default_headers():
    return {
        'Content-Type': 'application/json'
    }


class EMTClient:

    @staticmethod
    def create(client_id, pass_key):
        """
        log-in the EMT open api system using the provided client id and
        passKey and return an instance of the EMTClient class
        """
        client = EMTClient(client_id, pass_key)

    def __init__(self, client_id, pass_key):
        self._client_id = client_id
        self._pass_key = pass_key
        self._auth = None

    def login(self) -> None:
        """Initialize authentication for the api"""
        url = _BASE_URL + '/mobilitylabs/user/login'
        headers = {
            'passKey': self._pass_key,
            'X-ClientId': self._client_id
        }

        response = requests.get(url, headers=headers)
        _validate_response(response)

        login_data = response.json()['data'][0]
        token = login_data['accessToken']
        self._auth = EmtAuth(token)

    def is_logged_in(self) -> bool:
        """Return True if the current authentication is valid, False if not"""
        if self._auth is None:
            return False

        url = _BASE_URL + '/mobilitylabs/user/whoami'
        response = requests.get(url, auth=self._auth,
                                headers=_default_headers())
        try:
            _validate_response(response)
        except Exception:
            return False

        return True

    def get_arrival_times(self, stop, line=None) -> ArrivalInfo:
        """
        Return a dictionary of arrival lines for the specified stop (mandatory).
        If line is specified, will only return arrival times for that line.
        :param stop: The stop number.
        :param line: The line id.
        :return: a ArrivalInfo dictionary.
        """
        if line is None:
            line = 'all'
        url = _BASE_URL + f'/transport/busemtmad/stops/{stop}/arrives/{line}'
        payload = {
            'statistics': 'N',
            'cultureInfo': 'EN',
            'Text_StopRequired_YN': 'Y',
            'Text_EstimationsRequired_YN': 'Y',
            'Text_IncidencesRequired_YN': 'Y',
            'DateTime_Referenced_Incidencies_YYYYMMDD': _current_date_str()
        }
        response = requests.post(url, auth=self._auth, json=payload,
                                 headers=_default_headers())
        _validate_response(response)

        arrival_info = response.json()['data'][0]
        stop_name = arrival_info['StopInfo'][0]['Description']
        arrival_times = [Arrival(
            line=item['line'],
            stop=item['stop'],
            destination=item['destination'],
            arrives_in=item['estimateArrive'],
            distance=item['DistanceBus']
        ) for item in arrival_info['Arrive']]
        incident = arrival_info['Incident']['ListaIncident']['data'] != []
        return ArrivalInfo(stop_name=stop_name,
                           arrivals=arrival_times,
                           incident=incident)


class EmtAuth(AuthBase):
    """Attaches EMT Authentication parameters to the given Request object."""

    def __init__(self, token):
        # setup any auth-related data here
        self._token = token

    def __call__(self, r):
        # modify and return the request
        r.headers['accessToken'] = self._token
        return r
