# oDip DB API v1.1

Accepts data from an SNS topic, to add to DynamoDB.
Detects a new SNS Subscription Confirmation message and invokes the link to automatically confirm the request

Also provides endpoints for the following:

- Add Enquiry (/add-enquiry)
- Get All Enquiries (/get-all-enquiries)

## Pipeline Details

* "main" branch locked, can only be merged to via Pull Request.
* CI pipeline runs on creation of PR and PR can not be complete until CI is successful
* CD pipeline runs on successful merge to "main" branch.

### CI.yml:
- Runs with v3.8 and v3.9 of Python
- Installs Safety and Bandit manually (not contained within Requirements file, personal choice for the developer over whether to run these modules locally)
- Performs Linting Check
- Performs Safety Check
- Performs Bandit Check


### Main.yml:
- Integration:
    - Sets up Python v3.9
    - Installs Safety and Bandit manually (not contained within Requirements file, personal choice for the developer over whether to run these modules locally)
    - Performs Safety Check
    - Performs Bandit Check

* Deploy:
    * Needs Integration to complete
    * Configures AWS Credentials using GitHub Secrets
    * Creates a CodeDeploy Deployment object using AWS CLI and sends to pre-defined application on CodeDeploy

### Appspec.yml

* After-Install:
    * Restarts GUnicorn DB API service
