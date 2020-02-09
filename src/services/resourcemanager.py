# -*- coding: utf-8 -*-
"""
client for cloudresourcemanager.googleapis.com
"""
import httplib2
import csv
import json
import os
from io import StringIO
from time import sleep



from apiclient.errors import HttpError
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

from src.services.oauth2_flow import credentials_using_auth_code
from src.services.storage import get_content
from src.utils import with_retry, check_if_role_exists


# If authorization_code is provided, then it's converted into a
# Bearer token to call the API.
class ResourceManagerClient:
    def __init__(self, authorization_code=None):
        self.ancestry = None
        self.billing_mapping = None
        self.country_folder_mapping = None
        self.base_url = 'https://cloudresourcemanager.googleapis.com/'
        self.authorization_code = authorization_code

        credentials = GoogleCredentials.get_application_default()

        if os.environ.get('DEBUG', 'no').lower() == 'yes':

            from google.oauth2 import service_account
            SCOPES = [
                'https://www.googleapis.com/auth/cloud-platform',
            ]
            SERVICE_ACCOUNT_FILE = \
                'credentials/gcp-flask-api-credentials.json'

            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES
            )

        if authorization_code is not None:

            credentials = credentials_using_auth_code(authorization_code)

        self.credentials = credentials
        self.service_v1beta1 = discovery.build(
            'cloudresourcemanager',
            'v1beta1',
            credentials=credentials,
        )

        self.service_v1 = discovery.build(
            'cloudresourcemanager',
            'v1',
            credentials=credentials,
        )

        self.project_id = None
        self.project_number = None

    def get_service(
            self,
            name='cloudresourcemanager',
            version='v2',
            use_user_credentials=False
    ):
        if use_user_credentials and self.authorization_code is not None:
            credentials = credentials_using_auth_code(self.authorization_code)
        else:
            credentials = GoogleCredentials.get_application_default()

        return discovery.build(
            name,
            version=version,
            credentials=credentials,
        )

    def create_project(
            self,
            parent_id=os.environ.get('DEFAULT_PARENT_FOLDER_ID',
                                     '414914948118'),
            project_name=None,
            project_id=None,
            labels=None,
            **kwargs
    ):
        service = self.get_service(version='v1', use_user_credentials=False)

        if parent_id is None:
            parent = {
                "id": os.environ.get('ORGANIZATION_ID'),
                "type": "organization"
            }
        else:
            parent = {
                "id": parent_id,
                "type": "folder"
            }

        project_body = {
            "name": project_name,
            "projectId": project_id,
            "parent": parent,
            "labels": labels
        }

        project_creation_request = service.projects().create(
            body=project_body
        )

        try:
            operation = project_creation_request.execute()
            for i in [5, 1, 1, 1, 1, 2, 4, 8, 16]:
                sleep(i)
                operation_response = self.service_v1.operations().get(
                    name=operation.get('name')
                ).execute()

                if operation_response.get('done'):
                    break

            response = operation_response.get('response')
        except HttpError as err:
            return json.loads(err.content)

        self.project_id = response.get('projectId')
        self.project_number = response.get('projectNumber')

        return response

    def get_iam_policy(self, project_id=None):
        service = self.get_service(version='v1beta1', use_user_credentials=True)

        if project_id is None:
            project_id = self.project_id

        request = service.projects().getIamPolicy(
            resource=project_id,
            body={},
        )

        response = get_response(request)
        print(response)

        return response

    def set_iam_policy(self, bindings, bindings_to_remove=None,
                       project_id=None):
        if project_id is None:
            project_id = self.project_id

        service = self.get_service(version='v1beta1', use_user_credentials=True)

        # Append current bindings
        current_iam_policy = self.get_iam_policy(project_id=project_id)
        current_bindings = current_iam_policy.get('bindings')
        bindings.append(current_bindings)

        # Remove bindings
        if bindings_to_remove:
            for binding_to_remove in bindings_to_remove:
                for binding in bindings:
                    if type(binding) is list:
                        for b in binding:
                            if type(b) is dict:
                                remove_member(b, binding_to_remove)
                    elif type(binding) is dict:
                        remove_member(binding, binding_to_remove)

        set_iam_policy_request_body = {
            "policy": {"bindings": bindings}
        }

        request = service.projects().setIamPolicy(
            resource=project_id,
            body=set_iam_policy_request_body
        )

        response = get_response(request)

        return response

    def enable_service(self, service_name, project_number=None):
        if project_number is None:
            project_number = self.project_number

        service = self.get_service(name='serviceusage', version='v1beta1')

        request = service.services().enable(
            name='projects/{project_number}/services/{service_name}'.format(
                project_number=project_number,
                service_name=service_name,
            ),
        )

        response = get_response(request)

        return response

    def load_billing_mapping(self):
        if self.billing_mapping is None:
            billing_mapping_content = get_content(
                'gcp-flask-api',
                'billing_mapping.csv'
            ).decode('utf-8')
            reader = csv.reader(StringIO(billing_mapping_content),
                                delimiter=',')
            next(reader, None)  # skip the headers
            billing_mapping = {}
            for row in reader:
                if len(row) >= 2:
                    if row[0] and row[1]:
                        billing_mapping[row[0]] = row[1]

            self.billing_mapping = billing_mapping

    def load_country_folder_mapping(self):
        if self.country_folder_mapping is None:
            country_folder_mapping_content = get_content(
                'gcp-flask-api',
                'country_folder_mapping.csv'
            ).decode('utf-8')
            reader = csv.reader(StringIO(country_folder_mapping_content),
                                delimiter=',')
            next(reader, None)  # skip the headers
            country_folder_mapping = {}
            for row in reader:
                if len(row) >= 2:
                    if row[0] and row[1]:
                        country_folder_mapping[row[0]] = row[1]

            self.country_folder_mapping = country_folder_mapping

    def load_ancestry(self, project_id=None):
        if project_id is None:
            project_id = self.project_id

        service = self.get_service(version='v1beta1')

        if self.ancestry is None:
            request = service.projects().getAncestry(
                projectId=project_id,
                body={},
            )

            response = get_response(request)

            self.ancestry = response.get("ancestor", [])

    def get_country_folder_mapping(self, country):
        self.load_country_folder_mapping()

        return self.country_folder_mapping[country]

    def eligible_for_billing(self, project_id=None):
        if project_id is None:
            project_id = self.project_id

        eligible = False
        billing_account_id = None

        self.load_billing_mapping()
        self.load_ancestry(project_id)

        for ancestor in self.ancestry:
            if ancestor.get('resourceId').get('type') == 'folder' and \
                    ancestor.get('resourceId').get(
                        'id') in self.billing_mapping:
                eligible = True
                billing_account_id = self.billing_mapping.get(
                    ancestor.get('resourceId').get(
                        'id')
                )

        return eligible, billing_account_id

    def get_orgs(self):
        service = self.get_service(version='v1', use_user_credentials=True)

        request = service.organizations().search(body={})

        response = get_response(request)

        return response.get('organizations', [])

    def get_folders(self):
        service = self.get_service(
            version='v2beta1', use_user_credentials=True
        )

        request = service.folders().search(body={
            "query": "lifecycleState=ACTIVE"
        })

        response = get_response(request)

        return response.get('folders', [])

    # get all projects viewed by user.
    def get_projects(self):
        service = self.get_service(version='v1', use_user_credentials=True)
        request = service.projects().list()
        response = request.execute()
        return response

    # get info about specific project
    def get_project(self, project_id):
        service = self.get_service(version='v1', use_user_credentials=True)
        request = service.projects().get(projectId=project_id)
        return request.execute()

    # get policy for specific project
    def get_policy(self, project_id):
        """Gets IAM policy for a project."""
        # pylint: disable=no-member
        service = self.get_service(version='v1', use_user_credentials=True)
        policy = service.projects().getIamPolicy(
            resource=project_id, body={}).execute()
        print(policy)
        return policy


    # get logged in user info
    def get_logged_in_user_info(self):
        user_info_service = self.get_service('oauth2', version='v2', use_user_credentials=True)
        user_info = user_info_service.userinfo().get().execute()
        return user_info

    # get logged in user id
    def get_logged_in_user_id(self):
        user_info_service = discovery.build(
            serviceName='oauth2', version='v2',
            http=self.credentials.authorize(httplib2.Http()))
        user_info = user_info_service.userinfo().get().execute()
        return user_info['id']

    # adds a user to a speicific role in a project
    def add_user_to_project(self, project_id, member_id, role):
        if project_id is None:
            project_id = self.project_id

        service = self.get_service(version='v1beta1', use_user_credentials=True)
        current_iam_policy = self.get_iam_policy(project_id=project_id)
        if 'error' in current_iam_policy:
            return {
                       "error": current_iam_policy
                   }, current_iam_policy['error']['code']
        current_bindings = current_iam_policy.get('bindings')

        binding_of_role_exist = check_if_role_exists(current_bindings, role)

        if binding_of_role_exist != 0:
            add_member(binding_of_role_exist, member_id, role)
        else:
            add_member_to_new_role(current_bindings, role, member_id)

        set_iam_policy_request_body = {
            "policy": {"bindings": current_bindings}
        }

        request = service.projects().setIamPolicy(
            resource=project_id,
            body=set_iam_policy_request_body
        )
        response = get_response(request)

        return response

    # remove a user from a specific role in project
    def remove_user_from_project(self, project_id, member_id):
            if project_id is None:
                project_id = self.project_id

            service = self.get_service(version='v1beta1', use_user_credentials=True)
            current_iam_policy = self.get_iam_policy(project_id=project_id)
            if 'error' in current_iam_policy:
                return {
                           "error": current_iam_policy
                       }, current_iam_policy['error']['code']
            current_bindings = current_iam_policy.get('bindings')

            for binding in current_bindings:
                    remove_a_member(binding, member_id)

            set_iam_policy_request_body = {
                "policy": {"bindings": current_bindings}
            }

            request = service.projects().setIamPolicy(
                resource=project_id,
                body=set_iam_policy_request_body
            )
            response = get_response(request)

            return response

# function to remove member from role in a binding
def remove_member(binding, binding_to_remove):
    if binding.get('role') == binding_to_remove.get('role'):
        for member_to_remove in binding_to_remove.get('members'):
            if member_to_remove in binding.get('members'):
                binding.get('members').remove(member_to_remove)
                print("removed {}".format(member_to_remove))

# adds a member to an existing role
def add_member(binding, member_id, role):
    if 'group' in member_id:
        member_to_add = "group:"+member_id
    else :
        member_to_add = "user:"+member_id
    role_to_add = "roles/"+role
    if binding.get('role') == role_to_add:
            if member_to_add in binding.get('members'):
                print("user already exists {}".format(member_to_add))
            else:
                binding.get('members').append(member_to_add)
    else :
        add_member_to_new_role(binding, role, member_id)


# adds a new role and associate a user to that role
def add_member_to_new_role(bindings,role, member_id):
    member_to_add = "user:"+member_id
    role_to_add = "roles/"+role
    new_role = {
        "role": role_to_add,
        "members": [member_to_add]
    }

    bindings.append(new_role)
    return bindings


# removes a member from a specific role
def remove_a_member(binding,member_id):
    #role_of_member = "roles/"+role
    if 'group' in member_id:
        print("contains group ", member_id)
        member_to_remove = "group:"+member_id
    elif 'team' in member_id:
        print("contains team ", member_id)
        member_to_remove = "group:"+member_id
    else:
        member_to_remove = "user:"+member_id

    #if binding.get('role') == role_of_member:
    print("member_to_remove     ", member_to_remove)
    if member_to_remove in binding.get('members'):
        print("member found")
        binding.get('members').remove(member_to_remove)


def get_response(request, retry=True):
    try:
        if retry:
            return with_retry(request)
        else:
            return request.execute()
    except HttpError as err:
        return json.loads(err.content)

'''
def add_user_to_project(self,project_id,member_id,role):
    if project_id is None:
        project_id = self.project_id

    service = self.get_service('v1beta1')

    current_iam_policy = self.get_iam_policy(project_id=project_id)
    current_bindings = current_iam_policy.get('bindings')

    if
    for binding in current_bindings:
     add_member(binding,member_id,role)


    set_iam_policy_request_body = {
        "policy": {"bindings": current_bindings}
    }

    request = service.projects().setIamPolicy(
        resource=project_id,
        body=set_iam_policy_request_body
    )
    response = get_response(request)

    return response

'''

    #for project in response.get('projects', []):
        # TODO: Change code below to process each `project` resource:
    #    pprint(project)

    #request = service.projects().list_next(previous_request=request, previous_response=response)
