import json

class Subscription:
    def __init__(self, rm_operations):
        self.rm_operations = rm_operations

    def list(self):
        url = 'https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2021-03-01'
        body = {
            'query': 'resourcecontainers\n        | where type == \"microsoft.resources/subscriptions\"\n        | join kind=leftouter (securityresources \n            | where type == \"microsoft.security/securescores\"\n            | where properties.environment == \"Azure\" and properties.displayName == \"ASC score\"\n            ) on subscriptionId\n        | extend secureScore=properties1.score.percentage,\n            managementGroup=properties.managementGroupAncestorsChain,\n            subscriptionName=name,\n            status=properties.state\n        | project id, subscriptionId, subscriptionName, status, managementGroup, secureScore'
        }
        self.rm_operations.session.headers['Content-Type'] = 'application/json'
        response = self.rm_operations.session.post(url, json=body)
        del self.rm_operations.session.headers['Content-Type']

        self.rm_operations.display_response_info(response)
        if response.status_code == 200:
            print('[+] Fetched all subscriptions available to the current user')
        else:
            print('[-] Failed to fetch subscriptions')
            self.rm_operations.display_response_info(response)
            return

        properties = json.loads(response.content.decode('utf-8'))

        subscriptions = properties['data']
        count = properties['count']

        print('\tNumber of subscriptions: {0}'.format(count))
        for i in range(count):
            print('\t{0}) {1} --> {2}'.format(i + 1, subscriptions[i]['subscriptionName'], subscriptions[i]['subscriptionId']))

    def id_from_name(self, name):
        """
        This function retrieves the subscription id from the subscription name.
        :param name: The subscription name.
        :return: (string, string) --> A tuple that contains the subscription id and subscription name.
        """
        name = name.lower()
        response = self.rm_operations.session.get('https://management.azure.com/subscriptions?api-version=2018-02-01')
        if response.status_code != 200:
            print('[-] Error retrieving subscriptions')
            self.rm_operations.display_response_info(response)
            return

        subscriptions = json.loads(response.content.decode('utf-8'))['value']
        matches = []
        for subscription in subscriptions:
            if name in subscription['displayName'].lower():
                matches.append(subscription)
        if len(matches) == 0:
            print('[-] No subscriptions found for {0}'.format(name))
            return '', ''
        elif len(matches) == 1:
            return matches[0]['subscriptionId'], matches[0]['displayName']

        print('[~] There is more than one subscription matching this name. Choose the subscription you want: ')
        for index, match in enumerate(matches):
            print('{0}) {1}'.format(index + 1, match['displayName']))
        choice = int(input('-> '))
        if choice not in range(1, len(matches) + 1):
            print('[-] Invalid choice')
        return matches[choice - 1]['subscriptionId'], matches[choice - 1]['displayName']