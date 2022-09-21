import os
import requests 


#------------------------------------------------------------------------------
# getting all of my inputs for use in the action
#------------------------------------------------------------------------------

# setting the dbt cloud token to use dbt cloud API
dbt_cloud_token = os.environ["INPUT_DBT_CLOUD_TOKEN"]

# setting the dbt cloud account id 
dbt_cloud_account_id = os.environ["INPUT_DBT_CLOUD_ACCOUNT_ID"]

# setting the dbt cloud job id
dbt_cloud_job_id = os.environ["INPUT_DBT_CLOUD_JOB_ID"]

# # setting the job_check_interval
# job_check_interval = os.environ["INPUT_JOB_CHECK_INTERVAL"]

# # setting the failure_check_on_job_error
# fail_check_on_job_error = os.environ["INPUT_FAIL_CHECK_ON_JOB_ERROR"]

#------------------------------------------------------------------------------
# use environment variables to set dbt cloud api configuration
#------------------------------------------------------------------------------

# setting the headers for the dbt cloud api request
req_auth_headers = {'Authorization': f'Token {dbt_cloud_token}'}

# setting the url for the dbt cloud api request
base_dbt_cloud_api_url = f'https://cloud.getdbt.com/api/v2/accounts/{dbt_cloud_account_id}'

# setting the dbt cloud run status to human readable codes
run_status_map = { # dbt run statuses are encoded as integers. This map provides a human-readable status
  1:  'Queued',
  2:  'Starting',
  3:  'Running',
  10: 'Success',
  20: 'Error',
  30: 'Cancelled',
}

#------------------------------------------------------------------------------
# setting a function to return the most recent run for a given job
#------------------------------------------------------------------------------

def get_most_recent_run_for_job(base_url, headers, job_id):

    # setting the request url
    dbt_cloud_runs_url = f"{base_url}/runs/?job_definition_id={job_id}"

    # getting the run id
    most_recent_run_id = requests.get(dbt_cloud_runs_url, headers=headers).json()['data'][-1]['id']

    # returning the run id
    return most_recent_run_id

#------------------------------------------------------------------------------
# setting a function to return the status of the given job
#------------------------------------------------------------------------------

def get_run_status(base_url, headers, run_id):
    
    # setting the request url
    dbt_cloud_run_status_url = f"{base_url}/runs/{run_id}"
    
    # get status
    run_status_code = requests.get(dbt_cloud_run_status_url, headers=headers).json()['data']['status']
    
    # get status mapping
    run_status = run_status_map[run_status_code]
    
    # returning the run status
    return run_status



def main():

    # getting the run id of the most recent run of the given job
    most_recent_run_id = get_most_recent_run_for_job(base_url=base_dbt_cloud_api_url, headers=req_auth_headers, job_id=dbt_cloud_job_id)

    # getting the status of the that run
    run_status = get_run_status(base_url=base_dbt_cloud_api_url, headers=req_auth_headers, run_id=most_recent_run_id)

    print(f"::set-output name=myOutput::{run_status}")


if __name__ == "__main__":
    main()
