import requests
import json

from glibby.Graph.Group import Group
from glibby.Graph.User import User
from glibby.Graph.Spn import Spn
from glibby.Graph.Application import Application
from glibby.Graph.Attacks import Attacks


class GraphOperations:
    def __init__(self, access_token):
        #super().__init__(access_token)
        self.access_token = access_token
        self.session = requests.session()
        self.session.headers = {'Authorization': 'Bearer {0}'.format(self.access_token)}

        self.group = Group(self)
        self.user = User(self)
        self.spn = Spn(self)
        self.app = Application(self)

        self.attacks = Attacks(self)

    @staticmethod
    def display_response_info(response):
        print('\tStatus Code: {0}\n\tDescription: {1}'.format(response.status_code, response.content))

    def object_id_from_name(self, object_type, object_name, api_endpoint):
        """
        This function retrieves an object id from an object name for all Microsoft Graph objects.
        :param object_type: The object type.
        :param object_name: The object name.
        :param api_endpoint: The API endpoint that the function has to access in order to fetch the object id.
        :return: a json object that contains the object's full name ('name'), the object id ('object_id') and the
        app id ('app_id'). If the object is not service principal or app registration, the 'app_id' value should be an
        empty string.
        """

        object_type = object_type.lower()

        self.session.headers['ConsistencyLevel'] = 'eventual'
        response = self.session.get(api_endpoint)
        del self.session.headers['ConsistencyLevel']

        if response.status_code != 200:
            print('[-] Error searching the {0} {1}'.format(object_type, object_name))
            self.display_response_info(response)
            return {'', '', ''}

        content = json.loads(response.content.decode('utf-8'))
        if '@odata.count' in content.keys():
            data_count = content['@odata.count']
        else:
            data_count = len(content['value'])

        if data_count == 0:
            print('[-] No {0} found with name {1}'.format(object_type, object_name))
            return {'', '', ''}
        elif data_count == 1:
            entry = content['value'][0]
        else:
            print('[~] There is more than one {0} matching this name. Choose the {0} you want: '.format(object_type))
            content = content['value']
            for i, entry in enumerate(content):
                if object_type == 'user':
                    print('\t{0}) {1} --> {2}'.format(i + 1, entry['displayName'], entry['userPrincipalName']))
                else:
                    print('\t{0}) {1}'.format(i + 1, entry['displayName']))
            choice = int(input('-> '))
            if choice not in range(1, len(content) + 1):
                print('[-] Invalid option')
                return {'', '', ''}
            entry = content[choice - 1]

        return {
            'name': entry['displayName'],
            'object_id': entry['id'],
            # If the object is an app, return the application ID as well
            'app_id': entry['appId'] if 'appId' in entry.keys() else '',
        }

    def role_id_from_name(self, name):
        # TODO: add support for role from name in the 'object_id_from_name' function and delete this function
        role_definitions = self.get_role_definitions()
        if not role_definitions:
            return ''

        options = []
        for definition in role_definitions:
            if name in definition['displayName'].lower():
                options.append(definition)
        if len(options) == 0:
            print('[-] Given role was not found')
            return '', ''
        elif len(options) == 1:
            role = options[0]
        else:
            print('[~] There is more than one role matching this name. Choose the role you want:')
            for i, option in enumerate(options):
                print('\t{0}) {1}'.format(i + 1, option['displayName']))
            choice = int(input('-> '))
            if choice not in range(1, len(options) + 1):
                print('[-] Invalid option')
                return '', ''
            role = options[choice - 1]

        return role['displayName'], role['id']

    def assign_role_to_object(self, object_id, role_id):
        """
        This function assigns an Entra ID role to an object
        :param object_id: The object id to assign the role to.
        :param role_id: The role id of the role to assign.
        :return: Boolean. True if the function succeeded, False otherwise.
        """
        self.session.headers['Content-Type'] = 'application/json'
        body = {
            '@odata.type': '#microsoft.graph.unifiedRoleAssignment',
            'principalId': object_id,
            'roleDefinitionId': role_id,
            'directoryScopeId': '/'
        }
        response = self.session.post('https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignments',
                                     json=body)
        del self.session.headers['Content-Type']

        if response.status_code == 201:
            print('[+] Added the {0} role to {1}'.format(role_id, object_id))
            return True
        elif response.status_code == 400 and 'A conflicting object with one or more of the specified property values is present in the directory.' in response.json()['error']['message']:
            print('[~] Role {0} is already assigned to {1}'.format(role_id, object_id))
        else:
            print('[-] Error adding the {0} role to {1}'.format(role_id, object_id))
            self.display_response_info(response)
            return False

    def add_object_owner(self, object_type, owner_id, object_id):
        """
        This function adds a new owner to an Entra ID object.
        :param object_type: The object type of the target object.
        :param owner_id: The object id of the new owner.
        :param object_id: The object id of the target object.
        :return: Boolean. True if the function succeeded, False otherwise.
        """
        body = {
            '@odata.id': 'https://graph.microsoft.com/beta/directoryObjects/{0}'.format(owner_id)
        }
        self.session.headers['Content-Type'] = 'application/json'
        response = self.session.post(
            'https://graph.microsoft.com/beta/{0}/{1}/owners/$ref'.format(object_type, object_id), json=body)
        del self.session.headers['Content-Type']

        if response.status_code == 204:
            print('[+] Added {0} to owners of {1}'.format(owner_id, object_id))
            return True
        elif response.status_code == 400 and ('One or more added object references already exist for the following '
                                              'modified properties') in response.json()['error']['message']:
            print('[~] {0} is already an owner of {1}'.format(owner_id, object_id))
            return True
        else:
            print('[-] Error adding {0} to owners of {1}'.format(owner_id, object_id))
            self.display_response_info(response)
            return False

    def remove_object_owner(self, object_type, object_id, owner_id):
        """
        This function removes a specific owner from an Entra ID object.
        :param object_type: The object type of the target object.
        :param object_id: The object id of the target object.
        :param owner_id: The object id of the new owner.
        :return: Boolean. True if the function succeeded, False otherwise.
        """
        response = self.session.delete('https://graph.microsoft.com/beta/{0}/{1}/owners/{2}/$ref'.format(object_type, object_id, owner_id))
        if response.status_code == 204:
            print('[+] Removed {0} from owners of {1}'.format(owner_id, object_id))
            return True
        else:
            print('[-] Error removing {0} from owners of {1}'.format(owner_id, object_id))
            self.display_response_info(response)
            return False

    def get_role_definitions(self):
        url = 'https://graph.microsoft.com/beta/roleManagement/directory/roleDefinitions'
        response = self.session.get(url)
        if response.status_code == 200:
            print('[+] Fetched role definitions')
            return json.loads(response.content.decode('utf-8'))['value']
        else:
            print('[-] Failed to fetch role definitions')
            self.display_response_info(response)
            return ''

    def get_role_definition(self, role_name):
        role_name = role_name.lower()

        role_definitions = self.get_role_definitions()
        if not role_definitions:
            return ''

        for role in role_definitions:
            current_role_name = role['displayName']
            if current_role_name.lower() == role_name:
                print('[+] Got role definition id of role {0}: {1}'.format(current_role_name, role['id']))
                return role['id']
        print('[-] Failed to find role definition id of role {0}'.format(role_name))
        return ''
