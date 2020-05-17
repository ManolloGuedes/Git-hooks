Installation steps:

- It's needed to have pip3 library already installed to proceed

- Execute the install.sh file. This file will install all project dependencies.
  - In order to execute this, you will need to grant execution permission to this file.
    - chmod +x install.sh

- The execution of this hook is based on Jira's data. So you will need to generate an access token on its API
  - Generate your token using https://id.atlassian.com/manage-profile/security/api-tokens
  - Insert your token, user email and server url into api_token, user_email and server variables. These variables are in commit-verify.py file

- Copy commit-msg and commit-verify.py files into .git/hooks inside your project folder
- From inside the .git/hooks file
  - run:
    chmod +x commit-msg
    chmod +x commit-verify.py

    This will grant execution permission to our hooks file