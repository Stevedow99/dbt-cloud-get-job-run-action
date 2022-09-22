# dbt Cloud Get Job Run Action


This action will look up a [dbt Cloud](https://cloud.getdbt.com) job (based on job ID) and fetch the most recent run of that given job. It will then wait until the most recent run for that given job finishes and return the human readable status (e.g. `Success`, `Error`, `Cancelled`).

Some scenarios where this is useful:
- When you have a dbt repo that is used in multiple dbt Cloud projects and you would like to use the output of Slim CI PR jobs from both projects on a PR. Currently, in dbt Cloud only one of the two Slim CI PR jobs will show up on the PR even though both are being run in dbt Cloud. This Github action allows you to grab the other job's most recent run based on it's job id and return the status. This is useful when you want to make sure both Slim CI PR jobs pass on a given PR.

___

## **Inputs**

### Credentials

- `dbt_cloud_token` - dbt Cloud [API token](https://docs.getdbt.com/docs/dbt-cloud/dbt-cloud-api/service-tokens)
- `dbt_cloud_account_id` - dbt Cloud Account ID
- `dbt_cloud_job_id` - dbt Cloud Job ID

It's recommend to pass sensitive variables as GitHub secrets. [Example article on how to use Github Action secrets](https://www.theserverside.com/blog/Coffee-Talk-Java-News-Stories-and-Opinions/GitHub-Actions-Secrets-Example-Token-Tutorial)

### Action configuration

- `job_check_interval` - The interval between polls when checking the status of a dbt Cloud job (default is `45`)

___

## **Outputs**
- `dbt_cloud_job_run_status` - The human readable status of the given jobs most recent dbt Cloud run (e.g. `Success`, `Error`, `Cancelled`)
- `dbt_cloud_job_run_url` - A link to the dbt Cloud job run. _Note: if you are using Github action secerts from `dbt_cloud_account_id` this link will not work_

___


## **Creating a workflow**
```yaml
# This is a basic workflow to show using this action

# name of the workflow
name: Check dbt Cloud Job Run Status

# Controls when the workflow will run
on:
  pull_request:
    branches: [ "main" ]

  # Allows you to run this workflow manually from the Actions tab if needed
  workflow_dispatch:

# A workflow run is made up of one or more jobs that can run sequentially or in parallel
jobs:

  # This workflow contains a single job called "retrieve_dbt_cloud_job_status"
  retrieve_dbt_cloud_job_run_status:
  
    # The type of runner that the job will run on
    runs-on: ubuntu-latest

    # Steps represent a sequence of tasks that will be executed as part of the job
    steps:
      - name: Get dbt Cloud job run and return the status
        id: get_job_run
        uses: stevedow99/dbt-cloud-get-job-run-action@v1.0
        with:
          dbt_cloud_token: ${{ secrets.DBT_CLOUD_TOKEN }}
          dbt_cloud_account_id: 98765
          dbt_cloud_job_id: 123456
```
___
## **Examples of using this Github action with other workflows**

<br>

### Example using workflow to throw failures based on job status:
```yaml
# This is a basic workflow to show using this action

# name of the workflow
name: Check dbt Cloud Job Run Status

# Controls when the workflow will run
on:
  pull_request:
    branches: [ "main" ]

  # Allows you to run this workflow manually from the Actions tab if needed
  workflow_dispatch:

# A workflow run is made up of one or more jobs that can run sequentially or in parallel
jobs:

  # This workflow contains a single job called "retrieve_dbt_cloud_job_status"
  retrieve_dbt_cloud_job_run_status:
  
    # The type of runner that the job will run on
    runs-on: ubuntu-latest

    # Steps represent a sequence of tasks that will be executed as part of the job
    steps:

      # running the step to get the most recent job run results and return the status
      - name: Get dbt Cloud job run and return the status
        id: get_job_run
        uses: stevedow99/dbt-cloud-get-job-run-action@v1.0
        with:
          dbt_cloud_token: ${{ secrets.DBT_CLOUD_TOKEN }}
          dbt_cloud_account_id: 98765
          dbt_cloud_job_id: 123456

      # using the returned run status to throw an error on the PR if the dbt cloud job was not a sucess
      - name: Check on dbt cloud job failures
        if:  steps.get_job_run.outputs.dbt_cloud_job_run_status != 'Success'
        run: |
          echo "dbt cloud job failed or was cancelled, run status: ${{ steps.get_job_run.outputs.dbt_cloud_job_run_status }}"
          echo "view dbt cloud job run here: ${{ steps.get_job_run.outputs.dbt_cloud_job_run_url }}"
          exit 1

        # if the job was a success we log it
      - name: Check on dbt cloud job success
        if:  steps.get_job_run.outputs.dbt_cloud_job_run_status == 'Success'
        run: |
          echo "dbt cloud finished sucessfully, run status: ${{ steps.get_job_run.outputs.dbt_cloud_job_run_status }}"
          echo "view dbt cloud job run here: ${{ steps.get_job_run.outputs.dbt_cloud_job_run_url }}"
          exit 0
      
```
<br>

### Example using workflow to throw failures and add PR comments based on job status:
```yaml
# This is a basic workflow to show using this action

# name of the workflow
name: Check dbt Cloud Job Run Status

# Controls when the workflow will run
on:
  pull_request:
    branches: [ "main" ]

  # Allows you to run this workflow manually from the Actions tab if needed
  workflow_dispatch:

# A workflow run is made up of one or more jobs that can run sequentially or in parallel
jobs:

  # This workflow contains a single job called "retrieve_dbt_cloud_job_status"
  retrieve_dbt_cloud_job_run_status:
  
    # The type of runner that the job will run on
    runs-on: ubuntu-latest

    # Steps represent a sequence of tasks that will be executed as part of the job
    steps:

      # running the step to get the most recent job run results and return the status
      - name: Get dbt Cloud job run and return the status
        id: get_job_run
        uses: stevedow99/dbt-cloud-get-job-run-action@v1.0
        with:
          dbt_cloud_token: ${{ secrets.DBT_CLOUD_TOKEN }}
          dbt_cloud_account_id: 98765
          dbt_cloud_job_id: 123456
          
      # if the job run was a success we comment on the PR with a check and a link to the dbt Cloud Job run
      - name: PR comment with sucess
        uses: mshick/add-pr-comment@v1
        if:  steps.get_job_run.outputs.dbt_cloud_job_run_status == 'Success'
        with:
          message: |
            ## ✅ dbt Cloud job finished with the status ${{ steps.get_job_run.outputs.dbt_cloud_job_run_status }}
            View the dbt Cloud job run [here](${{ steps.get_job_run.outputs.dbt_cloud_job_run_url }})
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          repo-token-user-login: 'github-actions[bot]'
          allow-repeats: false # This is the default
          
          
      # if the run was a failure we comment on the PR with a X and a link to the dbt Cloud Job run
      - name: PR comment with failure
        uses: mshick/add-pr-comment@v1
        if:  steps.get_job_run.outputs.dbt_cloud_job_run_status != 'Success'
        with:
          message: |
            ## ❌ dbt Cloud job finished with the status ${{ steps.get_job_run.outputs.dbt_cloud_job_run_status }}
            View the dbt Cloud job run [here](${{ steps.get_job_run.outputs.dbt_cloud_job_run_url }})
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          repo-token-user-login: 'github-actions[bot]'
          allow-repeats: false # This is the default

      # using the returned run status to throw an error on the PR if the dbt cloud job was not a sucess
      - name: Check on dbt cloud job failures
        if:  steps.get_job_run.outputs.dbt_cloud_job_run_status != 'Success'
        run: |
          echo "dbt cloud job failed or was cancelled, run status: ${{ steps.get_job_run.outputs.dbt_cloud_job_run_status }}"
          echo "view dbt cloud job run here: ${{ steps.get_job_run.outputs.dbt_cloud_job_run_url }}"
          exit 1

        # if the job was a success we log it
      - name: Check on dbt cloud job success
        if:  steps.get_job_run.outputs.dbt_cloud_job_run_status == 'Success'
        run: |
          echo "dbt cloud finished sucessfully, run status: ${{ steps.get_job_run.outputs.dbt_cloud_job_run_status }}"
          echo "view dbt cloud job run here: ${{ steps.get_job_run.outputs.dbt_cloud_job_run_url }}"
          exit 0
      
```