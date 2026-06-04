import os
import requests
from .base_provider import DataProvider

class EIAProvider(DataProvider):
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('EIA_API_KEY', '')

    def get_brent(self):
        if not self.api_key:
            return {'success': False, 'source': 'EIA', 'error': 'missing api key'}
        try:
            url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
            params = {
                'api_key': self.api_key,
                'frequency': 'monthly',
                'data[0]': 'value',
                'facets[series][]': 'PET.RBRTE.D',
                'sort[0][column]': 'period',
                'sort[0][direction]': 'desc',
                'offset': 0,
                'length': 1
            }
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                price = data['response']['data'][0]['value']
                return {'success': True, 'price': round(float(price), 2), 'source': 'EIA'}
        except Exception:
            pass
        return {'success': False, 'source': 'EIA'}

    def get_selic(self):
        return {'success': False, 'source': 'EIA'}
