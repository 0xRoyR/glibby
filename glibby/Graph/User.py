class User:
    def __init__(self, graph_operations):
        self.graph_operations = graph_operations

    def list_authentication_methods(self, user_id):
        """
        List all authentication methods for a user.
        :param user_id: The ID of the user.
        :return: List of authentication methods. Each element (authentication method) in the list is a json object. If
        the function fails, it returns an empty list.
        """
        auth_methods_resp = self.graph_operations.session.get(
            'https://graph.microsoft.com/v1.0/users/{0}/authentication/methods'.format(user_id))
        authentication_methods = json.loads(auth_methods_resp.content.decode('utf-8'))['value']
        return authentication_methods

    def delete_authentication_method(self, user_id, authentication_method_name):
        """
        Deletes a authentication method for a user.
        :param user_id: The ID of the user.
        :param authentication_method_name: The name of the authentication method to delete.
        :return: Boolean. True if the authentication method was deleted, false otherwise.
        """
        authentication_methods = self.list_authentication_methods(user_id)
        for authentication_json in authentication_methods:
            if authentication_method_name.lower() in authentication_json['@odata.type'].lower():
                response = self.graph_operations.session.delete(
                    'https://graph.microsoft.com/beta/users/{0}/authentication/microsoftAuthenticatorMethods/{1}'.format(
                        user_id, authentication_json['id']))
                if response.status_code == 204:
                    print('[+] Deleted authenticator for {0}'.format(user_id))
                    return True
                else:
                    print('[-] Error deleting authenticator for {0}'.format(user_id))
                    self.graph_operations.display_response_info(response)
                    return False

    def change_phone_number(self, user_id, phone_number):
        """
        Changes the phone number for a user.
        :param user_id: The ID of the user.
        :param phone_number: The new phone number.
        :return: Boolean. True if the phone number was changed, false otherwise.
        """
        status = False

        self.graph_operations.session.headers['Content-Type'] = 'application.json'
        authentication_methods = self.list_authentication_methods(user_id)
        body = {'phoneNumber': phone_number}
        for authentication_json in authentication_methods:
            if 'phone' in authentication_json['@odata.type'].lower():
                body['phoneType'] = authentication_json['phoneType']
                method_id = authentication_json['id']
                response = self.graph_operations.session.patch(
                    'https://graph.microsoft.com/v1.0/users/{0}/authentication/phoneMethods/{1}'.format(user_id, method_id),
                    json=body)
                if response.status_code == 204:
                    print('[+] Changed phone number for {0}'.format(user_id))
                    status = True
                else:
                    print('[-] Error changing phone number for {0}'.format(user_id))
                    self.graph_operations.display_response_info(response)
        del self.graph_operations.session.headers['Content-Type']

        return status

    def set_password(self, user_id, password):
        """
        Sets the password for a user.
        :param user_id: The ID of the user.
        :param password: The new password.
        :return: Boolean. True if the password was changed, false otherwise.
        """
        self.graph_operations.session.headers['Content-Type'] = 'application/json'
        body = {
            'forceChangePasswordNextSignIn': False,
            'password': password
        }
        response = self.graph_operations.session.patch('https://graph.microsoft.com/v1.0/users/{0}'.format(user_id), data=body)
        del self.graph_operations.session.headers['Content-Type']
        if response.status_code == 204:
            print('[+] Changed the password for {0}'.format(user_id))
            return True
        else:
            print('[-] Error changing password for user {0}'.format(user_id))
            self.graph_operations.display_response_info(response)
            return False

    def id_from_name(self, name):
        """
        Retrieves an object id for a user by display name.
        :param name: The name of the user.
        :return: a json object that contains the object's full name ('name'), the object id ('object_id') and the
        app id ('app_id'). If the object is not service principal or app registration, the 'app_id' value should be an
        empty string.
        """
        api_endpoint = 'https://graph.microsoft.com/beta//users?$select=id,displayName,userPrincipalName,userType,onPremisesSyncEnabled,identities,companyName,creationType&$search=(\"displayName:{0}\" OR \"mail:{0}\" OR \"userPrincipalName:{0}\" OR \"givenName:{0}\" OR \"surName:{0}\" OR \"otherMails:{0}\")&$count=true'.format(name)
        return self.graph_operations.object_id_from_name('user', name, api_endpoint)

    def create(self, username, password, tenant_name):
        """
        Create a new Entra ID user.
        :param username: The username of the user.
        :param password: The password of the user.
        :param tenant_name: The tenant name of the tenant to create the user in.
        :return: String. The user's object id. If the function fails, it returns an empty string.
        """
        user_principal_name = '{0}@{1}'.format(username, tenant_name)
        body = {
            'accountEnabled': True,
            'displayName': username,
            'mailNickname': username,
            'passwordProfile': {
                'forceChangePasswordNextSignIn': False,
                'password': password
            },
            'userPrincipalName': user_principal_name
        }

        self.graph_operations.session.headers['Content-Type'] = 'application/json'
        response = self.graph_operations.session.post('https://graph.microsoft.com/v1.0/users', json=body)
        del self.graph_operations.session.headers['Content-Type']
        if response.status_code == 201:
            user_id = json.loads(response.content.decode('utf-8'))['id']
            print('[+] Created user {0}. User ID: {1}'.format(user_principal_name, user_id))
            return user_id
        else:
            print('[-] Error creating user {0}'.format(user_principal_name))
            self.graph_operations.display_response_info(response)
            return ''

    def delete(self, user_id):
        """
        Deletes a user by its ID.
        :param user_id: (String) The ID of the user.
        :return: (Boolean) True if the user was successfully deleted, False otherwise.
        """
        response = self.graph_operations.session.delete('https://graph.microsoft.com/v1.0/users/{0}'.format(user_id))
        if response.status_code == 204:
            print('[+] Deleted user {0}'.format(user_id))
            return True
        else:
            print('[-] Error deleting user {0}'.format(user_id))
            return False