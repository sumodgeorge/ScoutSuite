# -*- coding: utf-8 -*-

from ScoutSuite.providers.gcp.configs.base import GCPBaseConfig

from opinel.utils.console import printError, printException, printInfo

from googleapiclient import discovery


class IAMConfig(GCPBaseConfig):
    targets = (
        ('projects.serviceAccounts', 'ServiceAccounts', 'list', {'name': 'projects/ncccon2018prjct'}, False),
    )

    def __init__(self, thread_config):

        self.library_type = 'api_client_library'

        self.service_accounts = {}
        self.service_accounts_count = 0

        super(IAMConfig, self).__init__(thread_config)

    def parse_projects_serviceAccounts(self, service_account, params):

        service_account_dict = {}

        service_account_dict['id'] = service_account['uniqueId']
        service_account_dict['name'] = service_account['displayName']
        service_account_dict['email'] = service_account['email']
        service_account_dict['project_id'] = service_account['projectId']

        service_account_dict['keys'] = {}
        keys = self._get_service_account_keys(params['api_client'],
                                              service_account_dict['project_id'],
                                              service_account_dict['email'])
        if keys:
            for key in keys:
                service_account_dict['keys'][self.get_non_provider_id(key['name'])] = {
                    'name': key['name'],
                    'valid_after': key['validAfterTime'],
                    'valid_before': key['validBeforeTime'],
                    'key_algorithm': key['keyAlgorithm']
                }

        service_account_dict['bindingss'] = self._get_service_account_iam_policy(params['api_client'],
                                                                                 service_account_dict['project_id'],
                                                                                 service_account_dict['email'])

        self.service_accounts[service_account_dict['id']] = service_account_dict

        # required as target is 'projects.serviceAccounts' and not 'service_accounts'
        self.service_accounts_count+=1


    def _get_service_account_keys(self, api_client, project_id, service_account_email):

        try:
            #FIXME for some reason using the api_client fails, creating a new client doesn't generate an error...
            client = discovery.build('iam', 'v1')

            # response = api_client.projects().serviceAccounts().keys().list(
            response = client.projects().serviceAccounts().keys().list(
                name='projects/%s/serviceAccounts/%s' % (project_id, service_account_email)).execute()
            if 'keys' in response:
                return response['keys']
            else:
                return None
        except Exception as e:
            printError('Failed to get keys for service account %s: %s' % (service_account_email, e))
            return None

    def _get_service_account_iam_policy(self, api_client, project_id, service_account_email):

        try:
            #FIXME for some reason using the api_client fails, creating a new client doesn't generate an error...
            client = discovery.build('iam', 'v1')

            # response = api_client.projects().serviceAccounts().getIamPolicy(
            response = client.projects().serviceAccounts().getIamPolicy(
                resource='projects/%s/serviceAccounts/%s' % (project_id, service_account_email)).execute()
            if 'binginss' in response:
                return response['bindings']
            else:
                return None
        except Exception as e:
            printError('Failed to get IAM policy for service account %s: %s' % (service_account_email, e))
            return None