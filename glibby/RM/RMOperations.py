import uuid
import json
import requests

from glibby.RM.Attacks import Attacks
from glibby.RM.Subscription import Subscription

class RMOperations:
    def __init__(self, access_token):
        self.access_token = access_token
        self.session = requests.session()
        self.session.headers = {'Authorization': 'Bearer {0}'.format(self.access_token)}

        self.attacks = Attacks(self)
        self.subscription = Subscription(self)

    @staticmethod
    def display_response_info(response):
        print('\tStatus Code: {0}\n\tDescription: {1}'.format(response.status_code, response.content))


    def get_role_definition(self, role_name):
        role_name = role_name.lower()

        url = 'https://management.azure.com/providers/Microsoft.Authorization/roleDefinitions?$filter=type eq \'BuiltinRole\'&api-version=2022-05-01-preview'
        response = self.session.get(url)
        if response.status_code == 200:
            print('[+] Fetched role definitions')
        else:
            print('[-] Failed to fetch role definitions')
            self.display_response_info(response)
            return ''

        role_definitions = json.loads(response.content.decode('utf-8'))['value']
        for role in role_definitions:
            if role['properties']['roleName'].lower() == role_name:
                print('[+] Got role definition id of role {0}: {1}'.format(role['properties']['roleName'], role['id']))
                return role['id']
        print('[-] Failed to find role definition id of role {0}'.format(role_name))
        return ''

    def grant_iam_role(self, object_type, object_id, role_definition_id, subscription_id , resource_group_name= '', resource_name=''):
        """
        :param object_type: The type of object that a role will be assigned to. Can contain 'user'/'group'/'spn'.
        :param object_id: The ID of the object that will be assigned to.
        :param role_definition_id: The id of the role definition to grant.
        :param subscription_id: The id of the subscription in which the resource resides.
        :param resource_group_name: The name of the target resource group. Should contain empty string if IAM role is
        granted against a subscription object.
        :param resource_name: The name of the target resource. Should contain empty string if IAM role is granted
        against a subscription object, or a resource group object.
        :return:
        """

        object_types = {
            'user': 'User',
            'group': 'Group',
            'spn': 'ServicePrincipal',
        }

        if object_type.lower() not in object_types.keys():
            print('[-] Object type {0} is not supported'.format(object_type))
            return False

        if resource_name and not resource_group_name:
            print('[-] Resource group name must be provided when granting IAM roles over specific resource')
            return False

        role_assignment_id = str(uuid.uuid4())
        body = {
            'Id': role_assignment_id,
            'Properties': {
                'Condition': None,
                'ConditionVersion': None,
                'Description': '',
                'PrincipalId': object_id,
                'PrincipalType': object_types[object_type].lower().capitalize(),
                'RoleDefinitionId': role_definition_id,
                'Scope': '/subscriptions/{0}'.format(subscription_id)
            }
        }

        if resource_name:
            url = 'https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Web/sites/{2}/providers/Microsoft.Authorization/roleAssignments/{3}?api-version=2020-04-01-preview'.format(subscription_id, resource_group_name, resource_name, role_assignment_id)
        elif resource_group_name:
            url = 'https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Authorization/roleAssignments/{2}?api-version=2020-04-01-preview'.format(subscription_id, resource_group_name, role_assignment_id)
        else:
            url = 'https://management.azure.com/subscriptions/{0}/providers/Microsoft.Authorization/roleAssignments/{1}?api-version=2020-04-01-preview'.format(subscription_id, role_assignment_id)

        self.session.headers['Content-Type'] = 'application/json'
        response = self.session.put(url, json=body)
        del self.session.headers['Content-Type']
        if response.status_code == 201:
            print('[+] Assigned role {0} to {1} {2}'.format(role_definition_id, object_types[object_type].lower(), object_id))
            return True
        elif response.status_code == 409:
            print('[~] Role {0} is already assigned to {0} {1}'.format(role_definition_id, object_types[object_type].lower(), object_id))
            return True
        else:
            print('[-] Error assigning role {0} to {1} {2}'.format(role_definition_id, object_types[object_type], object_id))
            self.display_response_info(response)
            return False
