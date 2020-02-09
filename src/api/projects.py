import os

from flask import request
from flask_restful import Resource

from src.controllers.project import ProjectController
from src.schemas.ProjectSchema import ProjectSchema
from src.services import oauth2_flow
from src.utils import validate_data, requires_auth, validate_email, validate_user_role, send_email
from flasgger import Swagger, swag_from


class DeployProjectEndpoint(Resource):
    # decorators = [requires_auth]
    @swag_from('../swagger/project/deploy_project.yml')
    def post(self):
        payload = request.get_json()
        #data = validate_data(payload, ProjectSchema)
        data = payload
        authorization_code = oauth2_flow.extract_auth_code(request)

        owner_email = data.get('owner_email')

        if '@' not in owner_email:
            return {
                       "message": "Not a valid email."
                   }, 401

        if len(owner_email.split('@')) != 2:
            return {
                       "message": "Not a valid email."
                   }, 401

        domain = owner_email.split('@')[1]


        country = data.get(
            'country', os.environ.get('DEFAULT_COUNTRY')
        ).lower()

        # parent_id = data.get(
        #     'folder_id', os.environ.get('DEFAULT_PARENT_FOLDER_ID')
        # )

        application_code = data.get('application_code', os.environ.get(
            'DEFAULT_APPLICATION_CODE', 'FR-XXX'
        ))
        budget_code = data.get('budget_code', os.environ.get(
            'DEFAULT_BUDGET_CODE', 'FR-XXX'
        ))
        env = data.get('environment', os.environ.get(
            'DEFAULT_ENVIRONMENT', 'DEV'
        ))

        return ProjectController.deploy_project(
            owner_email=owner_email,
            # parent_id=parent_id,
            country=country,
            name=data.get('name'),
            env=env,
            authorization_code=authorization_code
        )


class GetProjectsInfoEndpoint(Resource):
    @swag_from('../swagger/project/get_user_projects.yml')
    def get(self):
        authorization_code = oauth2_flow.extract_auth_code(request)
        print("AUTHORIZATION CODE       :")
        print(authorization_code)
        return ProjectController.get_projects_info(authorization_code=authorization_code)


class GetProjectInfoEndpoint(Resource):
    @swag_from('../swagger/project/get_project_info.yml')
    def get(self, project_id):
        authorization_code = oauth2_flow.extract_auth_code(request)
        return ProjectController.get_project_info(project_id, authorization_code=authorization_code)


class GetProjectPolicyEndpoint(Resource):
    @swag_from('../swagger/project/get_project_policy.yml')
    def get(self, project_id):
        authorization_code = oauth2_flow.extract_auth_code(request)
        return ProjectController.get_project_policy(project_id, authorization_code=authorization_code)


class GetUserInfoEndpoint(Resource):
    @swag_from('../swagger/user/get_user_info.yml')
    def get(self):
        authorization_code = oauth2_flow.extract_auth_code(request)
        return ProjectController.get_user_info(authorization_code=authorization_code)


class GetUserIdEndpoint(Resource):
    def get(self):
        authorization_code = oauth2_flow.extract_auth_code(request)
        return ProjectController.get_user_id(authorization_code=authorization_code)


class AddUserToProjectPolicyEndpoint(Resource):
    @swag_from('../swagger/project/add_user_to_project.yml')
    def post(self, project_id, member_id, role):
        if validate_user_role(role) == 0:
            return {
                       "message": "Not a valid user role."
                   }, 401
        authorization_code = oauth2_flow.extract_auth_code(request)
        return ProjectController.add_user_to_project(project_id, member_id, role, authorization_code=authorization_code)


class RemoveUserFromProjectPolicyEndpoint(Resource):
    @swag_from('../swagger/project/remove_user_from_project.yml')
    def post(self, project_id, member_id):
        #if validate_user_role(role) == 0:
        #    return {
        #               "message": "Not a valid user role."
        #           }, 401
        authorization_code = oauth2_flow.extract_auth_code(request)
        return ProjectController.remove_user_from_project(project_id, member_id,
                                                          authorization_code=authorization_code)
