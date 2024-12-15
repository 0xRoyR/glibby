import json
from datetime import datetime, timedelta


class Application:
    def __init__(self, graph_operations):
        self.graph_operations = graph_operations

    def id_from_name(self, name):
        """
        Retrieves an object id for app registration by display name.
        :param name: The name of the app registration.
        :return: a json object that contains the object's full name ('name'), the object id ('object_id') and the
        app id ('app_id'). If the object is not service principal or app registration, the 'app_id' value should be an
        empty string.
        """
        api_endpoint = 'https://graph.microsoft.com/beta/myorganization/applications/?$select=displayName,id,appId,info,createdDateTime,keyCredentials,passwordCredentials,deletedDateTime&$search=%22appId:{0}%22%20OR%20%22displayName:{0}%22%20&$orderby=displayName&$count=true'.format(name)
        return self.graph_operations.object_id_from_name('application', name, api_endpoint)

    def add_owner(self, owner_id, app_id):
        """
        This function adds a new owner to application (app registration).
        :param owner_id: The object id of the new owner.
        :param app_id: The object id of the application.
        :return: Boolean. True if the function succeeded, False otherwise.
        """
        return self.graph_operations.add_object_owner('applications', owner_id, app_id)

    def remove_owner(self, owner_id, app_id):
        """
        This function removes an existing owner of application (app registration).
        :param owner_id: The object id of the owner to remove.
        :param app_id: The object id of the application.
        :return: Boolean. True if the function succeeded, False otherwise.
        """
        return self.graph_operations.remove_object_owner('applications', owner_id, app_id)

    def create_secret(self, object_id, name='secret'):
        """
        Adds a new secret to an application object.
        :param object_id: The application object ID.
        :param name: The name of the new secret. This is an optional parameter. The default value for this parameter
        is "secret"
        :return: Tuple -> (String, String). If succeeded, it returns the key id of the new secret. Otherwise, it returns an empty string.
        """
        current_time = datetime.utcnow()
        start_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        end_time = (current_time + timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        body = {
            'passwordCredential': {
                'displayName': name,
                'startDateTime': start_time,
                'endDateTime': end_time
            }
        }
        self.graph_operations.session.headers['Content-Type'] = 'application/json;odata.metadata=minimal;odata.streaming=true;IEEE754Compatible=false;charset=utf-8'
        response = self.graph_operations.session.post('https://graph.microsoft.com/v1.0/myorganization/applications/{0}/addPassword'.format(object_id), json=body)
        del self.graph_operations.session.headers['Content-Type']
        if response.status_code == 200:
            print('[+] Added secret to application {0}'.format(object_id))
            content = json.loads(response.content.decode('utf-8'))
            print('\tDisplay Name: {0}'.format(content['displayName']))
            print('\tStart Time: {0}'.format(content['startDateTime']))
            print('\tEnd Time: {0}'.format(content['endDateTime']))
            print('\tHint: {0}'.format(content['hint']))
            print('\tKey ID: {0}'.format(content['keyId']))
            print('\tSecret: {0}'.format(content['secretText']))
            return content['keyId'], content['secretText']
        else:
            print('[-] Error adding secret to application {0}'.format(object_id))
            self.graph_operations.display_response_info(response)
            return '', ''

    def delete_secret(self, object_id, key_id):
        """
        Deletes a secret from an application object.
        :param object_id: The application object ID.
        :param key_id: The key id of the secret to be deleted
        :return: Boolean. If succeeded, True is returned. Otherwise, False is returned.
        """
        self.graph_operations.session.headers['Content-Type'] = 'application/json'
        body = {
            'keyId': key_id
        }
        response = self.graph_operations.session.post(
            'https://graph.microsoft.com/v1.0/myorganization/applications/{0}/removePassword'.format(object_id), json=body)
        del self.graph_operations.session.headers['Content-Type']
        if response.status_code == 204:
            print('[+] Deleted requested secret from application {0}'.format(object_id))
            return True
        else:
            print('[-] Error deleting requested secret from application {0}'.format(object_id))
            self.graph_operations.display_response_info(response)
            return False

