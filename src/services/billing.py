# -*- coding: utf-8 -*-
"""
client for billing.googleapis.com
"""
import json
import os
import requests

from apiclient.errors import HttpError
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials


# Class Billing_client
class BillingClient:
    def __init__(self):
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

        self.credentials = credentials

        self.service = discovery.build(
            'cloudbilling',
            'v1',
            credentials=credentials,
        )

    def enable_billing(
            self,
            project_id=None,
            billing_account_id=None
    ):

        project_billing_info = {
            "billingAccountName": "billingAccounts/{}"
                .format(billing_account_id),
        }

        request = self.service.projects().updateBillingInfo(
            name='projects/{}'.format(project_id),
            body=project_billing_info
        )

        try:
            response = request.execute()
        except HttpError as err:
            return json.loads(err.content)

        return response


    '''
    def get_billing_accounts():
        try:
            response = requests.get('https://cloudbilling.googleapis.com/v1/billingAccounts')
        except HttpError as err:
            return json.loads(err.content)

        return response
    '''