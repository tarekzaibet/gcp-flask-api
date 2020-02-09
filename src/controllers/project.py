import os

from src.services.billing import BillingClient
from src.services.resourcemanager import ResourceManagerClient
from src.utils import make_project_name, make_project_id, sanitize_label_value, \
    send_email


class ProjectController():
    def __init__(self):
        pass

    @classmethod
    def deploy_project(cls, owner_email,
                       country=None,
                       name=None,
                       env=None,
                       authorization_code=None,
                       **kwargs):
        status = {
            "project_creation": "",
            "billing_activation": ""
        }

        # user_project_bindings = get_iam_owner_binding(owner_email)

        project_name = make_project_name(
            name=name,
            env=env,
        )
        project_id = make_project_id(name)

        # Create labels
        labels = {
            "application-name": sanitize_label_value(name),
            "environment": sanitize_label_value(env),
        }

        resource_manager_client = ResourceManagerClient(
            authorization_code=authorization_code
        )

        parent_id = resource_manager_client.get_country_folder_mapping(country)

        billing_client = BillingClient()

        print('Create GCP project...')

        # create GCP project
        project = resource_manager_client.create_project(
            parent_id=parent_id,
            project_name=project_name,
            project_id=project_id,
            labels=labels,
            **kwargs)

        if 'error' in project:
            print('Error when creating project')
            status["project_creation"] = "ERROR"
            return project
        else:
            status["project_creation"] = "OK"
            return project

        print('Project successfuly created.')


        # Construct response
        response = {
            "status": status,
            'project': project,
            # 'set_owner_policy': set_owner_policy,
        }

        return response

# def get_iam_owner_binding(email):
#     return [
#         {
#             "role": "roles/owner",
#             "members": ["user:{}".format(email)]
#         }
#     ]
    @classmethod
    def get_projects_info(cls,authorization_code=None):
        resource_manager_client = ResourceManagerClient(
            authorization_code=authorization_code
        )
        response = resource_manager_client.get_projects()
        return response

    @classmethod
    def get_project_info(cls,project_id,authorization_code=None):
        resource_manager_client = ResourceManagerClient(
            authorization_code=authorization_code
        )
        response = resource_manager_client.get_project(project_id)
        return response

    @classmethod
    def get_project_policy(cls,project_id,authorization_code=None):
        resource_manager_client = ResourceManagerClient(
            authorization_code=authorization_code
        )
        response = resource_manager_client.get_policy(project_id)
        return response

    @classmethod
    def get_user_info(cls, authorization_code=None):
        resource_manager_client = ResourceManagerClient(
            authorization_code=authorization_code
        )
        response = resource_manager_client.get_logged_in_user_info()
        return response

    @classmethod
    def get_user_id(cls, authorization_code=None):
        resource_manager_client = ResourceManagerClient(
            authorization_code=authorization_code
        )
        response = resource_manager_client.get_logged_in_user_info()
        return response['id']

    @classmethod
    def add_user_to_project(cls, project_id, member_id, role, authorization_code=None):
        resource_manager_client = ResourceManagerClient(
            authorization_code=authorization_code
        )
        response = resource_manager_client.add_user_to_project(project_id,member_id,role)
        return response

    @classmethod
    def remove_user_from_project(cls, project_id, member_id, authorization_code=None):
        resource_manager_client = ResourceManagerClient(
            authorization_code=authorization_code
        )
        response = resource_manager_client.remove_user_from_project(project_id,member_id)
        return response
