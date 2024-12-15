import requests
import json

class SPNAuthHandler:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

        self.session = requests.Session()
        self.session.headers = {}

    @staticmethod
    def display_response_info(response):
        print('\tStatus Code: {0}\n\tDescription: {1}'.format(response.status_code, response.content))

    def get_access_token(self, tenant_id, resource):
        resource = resource.lower()
        resources = {
            'graph': 'https://graph.microsoft.com/.default',
            'rm': 'https://management.azure.com/.default'
        }

        if resource not in resources.keys():
            print('[-] Invalid resource')
            return ''

        body = {
            'Grant_Type': 'client_credentials',
            'Scope': resources[resource],
            'Client_ID': self.client_id,
            'Client_Secret': self.client_secret
        }

        url = 'https://login.microsoftonline.com/{0}/oauth2/v2.0/token'.format(tenant_id)

        response = self.session.post(url, data=body)
        if response.status_code == 200:
            print('[+] Obtained access token to {0} for spn {1}'.format(resource, self.client_id))
            return json.loads(response.content.decode('utf-8'))['access_token']
        else:
            print('[-] Error obtaining access token to {0} for spn {1}'.format(resource, self.client_id))
            self.display_response_info(response)
            return ''
