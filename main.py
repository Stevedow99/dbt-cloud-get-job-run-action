import os
import sys
import requests
import time


# ------------------------------------------------------------------------------
# getting all of my inputs for use in the action
# ------------------------------------------------------------------------------

# setting the dbt cloud token to use dbt cloud API
dbt_cloud_token = os.environ["INPUT_DBT_CLOUD_TOKEN"]

# setting the dbt cloud account id
dbt_cloud_account_id = os.environ["INPUT_DBT_CLOUD_ACCOUNT_ID"]

# setting the dbt cloud job id
dbt_cloud_job_id = os.environ["INPUT_DBT_CLOUD_JOB_ID"]

# setting the job_check_interval
job_check_interval = int(os.environ["INPUT_JOB_CHECK_INTERVAL"])

# ------------------------------------------------------------------------------
# use environment variables to set dbt cloud api configuration
# ------------------------------------------------------------------------------

# setting the headers for the dbt cloud api request
req_auth_headers = {'Authorization': f'Token {dbt_cloud_token}'}

# setting the url for the dbt cloud api request
base_dbt_cloud_api_url = f'https://cloud.getdbt.com/api/v2/accounts/{dbt_cloud_account_id}'

# setting the dbt cloud run status to human readable codes
# dbt run statuses are encoded as integers. This map provides a human-readable status
run_status_map = {
  1:  'Queued',
  2:  'Starting',
  3:  'Running',
  10: 'Success',
  20: 'Error',
  30: 'Cancelled',
}

# ------------------------------------------------------------------------------
# setting a function to return the most recent run for a given job
# ------------------------------------------------------------------------------


def get_most_recent_run_for_job(base_url, headers, job_id):

    # setting the request url
    dbt_cloud_runs_url = f"{base_url}/runs/?job_definition_id={job_id}"

    # getting the run
    most_recent_run = requests.get(dbt_cloud_runs_url, headers=headers, timeout=30).json()['data'][-1]

    # getting the run id
    run_id = most_recent_run['id']

    # getting the project id (used for links)
    project_id = most_recent_run['project_id']
    

    # returning the run id and project id of the most recent run
    return {"run_id" : run_id, "project_id" : project_id}

# ------------------------------------------------------------------------------
# setting a function to return the status of the given job
# ------------------------------------------------------------------------------


def get_run_status(base_url, headers, run_id): 

    # setting the request url
    dbt_cloud_run_status_url = f"{base_url}/runs/{run_id}"

    # get status
    run_status_code = requests.get(dbt_cloud_run_status_url, headers=headers, timeout=30).json()['data']['status']

    # get status mapping
    run_status = run_status_map[run_status_code]

    # returning the run status
    return run_status

# ------------------------------------------------------------------------------
# running the main function
# ------------------------------------------------------------------------------


def main():
    # getting the most recent run of the given job
    most_recent_run = get_most_recent_run_for_job(base_url=base_dbt_cloud_api_url, headers=req_auth_headers, job_id=dbt_cloud_job_id)

    # getting the run id of the most recent run
    most_recent_run_id = most_recent_run['run_id']

    # getting the project id of the most recent run
    most_recent_run_project = most_recent_run['project_id']

    # setting a link where the run can be looked up
    run_status_link = f'https://cloud.getdbt.com/#/accounts/{dbt_cloud_account_id}/projects/{most_recent_run_project}/runs/{most_recent_run_id}/'

    # setting up an intial wait period just in case the job takes some time to kick off
    time.sleep(10)

    # check status indefinitely with an initial wait period
    while True:
        run_status = get_run_status(base_url=base_dbt_cloud_api_url, headers=req_auth_headers, run_id=most_recent_run_id)
        print(f'Run status -> {run_status}')

        # if status is of kind finsihed them we stop the while loop and log
        if run_status in ['Error', 'Cancelled', 'Success']:
            print(f'Run {most_recent_run_id} of Job {dbt_cloud_job_id} finished with the status {run_status}. See details at {run_status_link}')
            # setting the output of the run status
            print(f"::set-output name=dbt_cloud_job_run_status::{run_status}")
            print(f"::set-output name=dbt_cloud_job_run_url::{run_status_link}")
            return

        # if run status is not of kind finished we hit the run again after an intercal
        else:
            print(f'Run {most_recent_run_id} of Job {dbt_cloud_job_id} is still running. See details at {run_status_link}')
            print(f'Sleeping for the set interval of {job_check_interval}, then gathering run status again')
        
        # sleeping for the interval
        time.sleep(job_check_interval)

if __name__ == "__main__":
    main()