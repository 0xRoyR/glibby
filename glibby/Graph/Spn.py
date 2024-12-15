class Spn:
    def __init__(self, graph_operations):
        self.graph_operations = graph_operations

    def id_from_name(self, name):
        """
        Retrieves an object id for service principal by display name.
        :param name: The name of the service principal.
        :return: a json object that contains the object's full name ('name'), the object id ('object_id') and the
        app id ('app_id'). If the object is not service principal or app registration, the 'app_id' value should be an
        empty string.
        """
        api_endpoint = 'https://graph.microsoft.com/beta/servicePrincipals?$select=displayName,appId,id,preferredSingleSignOnMode,publisherName,homepage,appOwnerOrganizationId,accountEnabled,tags,applicationTemplateId,servicePrincipalType,createdDateTime,keyCredentials,servicePrincipalNames,preferredTokenSigningKeyThumbprint,&$search=\"displayName:{0}\"&$filter=tags/Any(x: x eq \'WindowsAzureActiveDirectoryIntegratedApp\')&$$count=true'.format(name)
        return self.graph_operations.object_id_from_name('spn', name, api_endpoint)

    def add_owner(self, owner_id, spn_id):
        """
        This function adds a new owner to service principal.
        :param owner_id: The object id of the new owner.
        :param spn_id: The object id of the service principal.
        :return: Boolean. True if the function succeeded, False otherwise.
        """
        return self.graph_operations.add_object_owner('servicePrincipals', owner_id, spn_id)

    def remove_owner(self, owner_id, spn_id):
        """
        This function removes an existing owner of service principal.
        :param owner_id: The object id of the owner to remove.
        :param spn_id: The object id of the service principal.
        :return: Boolean. True if the function succeeded, False otherwise.
        """
        return self.graph_operations.remove_object_owner('servicePrincipals', owner_id, spn_id)