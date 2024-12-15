class Group:
    def __init__(self, graph_operations):
        self.graph_operations = graph_operations

    def id_from_name(self, name):
        """
        Retrieves an object id for group by display name.
        :param name: The name of the group.
        :return: a json object that contains the object's full name ('name'), the object id ('object_id') and the
        app id ('app_id'). If the object is not service principal or app registration, the 'app_id' value should be an
        empty string.
        """
        api_endpoint = 'https://graph.microsoft.com/beta/groups?$select=id,displayName,mailEnabled,securityEnabled,groupTypes,onPremisesSyncEnabled,mail,isAssignableToRole,writebackConfiguration,isManagementRestricted,resourceProvisioningOptions,expirationDateTime,createdDateTime,membershipRuleProcessingState&$search=\"displayName:{0}\" OR \"mail:{0}\"&$count=true'.format(name)
        return self.graph_operations.object_id_from_name('group', name, api_endpoint)

    def list_members(self):
        '''TODO'''
        pass

    def add_member(self, member_id, group_id):
        """
        Adds a new member to a group.
        :param member_id: The object id of the new member.
        :param group_id: The group id.
        :return: Boolean. True if the function succeeded, False otherwise.
        """
        body = {
            '@odata.id': 'https://graph.microsoft.com/beta/directoryObjects/{0}'.format(member_id)
        }
        self.graph_operations.session.headers['Content-Type'] = 'application/json'
        response = self.graph_operations.session.post('https://graph.microsoft.com/beta/groups/{0}/members/$ref'.format(group_id), json=body)
        del self.graph_operations.session.headers['Content-Type']

        if response.status_code == 204:
            print('[+] Added {0} to members of group {1}'.format(member_id, group_id))
            return True
        elif response.status_code == 400 and ('One or more added object references already exist for the following '
                                              'modified properties') in response.json()['error']['message']:
            print('[~] {0} is already a member of {1}'.format(member_id, group_id))
            return True
        else:
            print('[-] Error adding {0} to members of group {1}'.format(member_id, group_id))
            self.graph_operations.display_response_info(response)
            return False

    def remove_member(self, member_id, group_id):
        """
        Removes a member from a group.
        :param member_id: The object id of the new member.
        :param group_id: The group id.
        :return: Boolean. True if the function succeeded, False otherwise.
        """
        response = self.graph_operations.session.delete('https://graph.microsoft.com/beta/groups/{0}/members/{1}'.format(group_id, member_id))
        if response.status_code == 204:
            print('[+] Removed {0} from members of {1}'.format(member_id, group_id))
            return True
        else:
            print('[-] Error removing {0} from members of {1}'.format(member_id, group_id))
            self.graph_operations.display_response_info(response)
            return False

    def list_owners(self, group_name):
        # TO DO
        pass

    def add_owner(self, owner_id, group_name):
        """
        Adds an owner to a group.
        :param owner_id: The object id of the new owner
        :param group_name: The name of the group
        :return: Boolean. True if the function succeeded, False otherwise.
        """
        return self.graph_operations.add_object_owner('groups', owner_id, group_name)

    def remove_owner(self, owner_id, group_name):
        """
        Removes an owner from a group.
        :param owner_id: The object id of the owner
        :param group_name: Name of the group
        :return: Boolean. True if the function succeeded, False otherwise.
        """
        return self.graph_operations.remove_object_owner('groups', owner_id, group_name)