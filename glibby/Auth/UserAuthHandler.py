import requests
import json

class UserAuthHandler:
    def __init__(self, username, password, refresh_token=''):
        self.username = username
        self.password = password
        self.refresh_token = refresh_token

        self.session = requests.Session()
        self.session.headers = {}

        # self.tokens = {}

    @staticmethod
    def display_response_info(response):
        print('\tStatus Code: {0}\n\tDescription: {1}'.format(response.status_code, response.content))

    def get_access_token(self, tenant_id, resource, client_id='04b07795-8ddb-461a-bbee-02f9e1bf7b46', method='credentials'):
        """
        This function is responsible for obtaining an access token for a user.
        :param tenant_id: The user's tenant id
        :param resource: The resource to which the token will be obtained
        :param client_id: The client id to issue the access token to. This is an optional parameter. The default is the
        Microsoft Azure CLI client.
        :param method: The method to use in order to get the access token. If the 'credentials' method (default) is
        used, this function will use the 'password' grant type in oauth2 and get the access token by using the username
        and password specified when creating this class' instance. If the 'refresh_token' method is used, this function
        will use the 'refresh_token' grant type in oauth2 and get the access token by using a refresh token that was
        obtained in the 'get_refresh_token' method.
        :return: String. If succeeded, an access token will be returned. Otherwise, an empty string will be returned.
        """
        resource = resource.lower()
        resources = {
            'graph': 'https://graph.microsoft.com/.default',
            'rm': 'https://management.azure.com/.default'
        }
        if resource not in resources.keys():
            print('[-] Invalid resource')
            return

        if method == 'credentials':
            body = {
                'Grant_Type': 'password',
                'Scope': resources[resource],
                'Username': self.username,
                'Password': self.password,
                'Client_ID': client_id
            }
        elif method == 'refresh_token':
            body = {
                'Grant_Type': 'refresh_token',
                'Client_ID': client_id,
                'Refresh_Token': self.refresh_token
            }
        else:
            print('[-] Invalid method "{0}"'.format(method))
            return ''

        url = 'https://login.microsoftonline.com/{0}/oauth2/v2.0/token'.format(tenant_id)
        response = self.session.post(url, data=body)
        if response.status_code == 200:
            print('[+] Obtained access token to {0} for user {1}'.format(resource, self.username))
            return json.loads(response.content.decode('utf-8'))['access_token']
        else:
            print('[-] Error obtaining access token to {0} for user {1}'.format(resource, self.username))
            self.display_response_info(response)
            return ''


    def get_refresh_token(self, tenant_id, client_id='04b07795-8ddb-461a-bbee-02f9e1bf7b46'):
        """
        This function creates a refresh token for authentication for the current user.
        :param tenant_id: The tenant of the current user
        :param client_id: The client id to issue the refresh token to. This is an optional parameter. The default is the
        Microsoft Azure CLI client.
        :return: If succeeded, a tuple is returned. The first element is the refresh token and the second is the
        access token. Otherwise, a tuple of two empty strings is returned.
        """
        # The 'client_id' below is just the client id through where we will obtain the access / refresh token. For example, azure powershell cli client / outlook / whatever. It does not really matter what we choose here!

        body = {
            'Grant_Type': 'password',
            'Scope': 'openid offline_access',
            'Username': self.username,
            'Password': self.password,
            'Client_ID': client_id
        }

        url = 'https://login.microsoftonline.com/{0}/oauth2/v2.0/token'.format(tenant_id)
        #self.session.headers['Content-Type'] = 'application/json'
        response = self.session.post(url, data=body)
        print(response.status_code)
        if response.status_code == 200:
            print('[+] Obtained refresh token to {0} for user {1}'.format(tenant_id, self.username))
            refresh_token, access_token = response.json()['refresh_token'], response.json()['access_token']
            self.refresh_token = refresh_token
            return refresh_token, access_token
        else:
            print('[-] Error obtaining refresh token to {0} for user {1}'.format(tenant_id, self.username))
            self.display_response_info(response)
            return '', ''
