import base64
import json
import os

from googleapiclient import discovery

PROJECT_ID = os.getenv('GCP_PROJECT')
PROJECT_NAME = f'projects/{PROJECT_ID}'


def main(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    data = normalize_data(event)
    print(data)
    control_costs(data)


def normalize_data(event):
    '''
    normalize event data from source http and pubsub
    '''
    event_type = event.get("@type")
    if event_type:
        if 'PubsubMessage' in event_type:
            return json.loads(base64.b64decode(event['data']).decode('utf-8'))

    return event


def control_costs(data):
    cost_amount = data['costAmount']
    budget_amount = data['budgetAmount']
    if cost_amount <= budget_amount:
        print(f'No action necessary. (Current cost: {cost_amount})')
        return

    if PROJECT_ID is None:
        print('No project specified with environment variable')
        return

    billing = discovery.build(
        'cloudbilling',
        'v1',
        cache_discovery=False,
    )

    projects = billing.projects()

    billing_enabled = __is_billing_enabled(PROJECT_NAME, projects)

    if billing_enabled:
        __disable_billing_for_project(PROJECT_NAME, projects)
    else:
        print('Billing already disabled')


def __is_billing_enabled(project_name, projects):
    """
    Determine whether billing is enabled for a project
    @param {string} project_name Name of project to check if billing is enabled
    @return {bool} Whether project has billing enabled or not
    """
    try:
        res = projects.getBillingInfo(name=project_name).execute()
        return res['billingEnabled']
    except KeyError:
        # If billingEnabled isn't part of the return, billing is not enabled
        return False
    except Exception:
        print('Unable to determine if billing is enabled on specified project, assuming billing is enabled')
        return True


def __disable_billing_for_project(project_name, projects):
    """
    Disable billing for a project by removing its billing account
    @param {string} project_name Name of project disable billing on
    """
    body = {'billingAccountName': ''}  # Disable billing
    try:
        res = projects.updateBillingInfo(
            name=project_name, body=body).execute()
        print(f'Billing disabled: {json.dumps(res)}')
    except Exception as ex:
        print('Failed to disable billing, possibly check permissions', ex)
