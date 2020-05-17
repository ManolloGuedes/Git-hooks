# Git Hooks

This project was made as part of two articles about Git Hooks. With this tutorial, two Git Hooks was created: post-rewrite and commit-msg.

The post-rewrite hook gives us the capabillity to discover duplicate commits.

The commit-message hook creates an acreates a commit message analysis flow that uses Jira's API data as input. 

## Articles
* [Git hooks, what are they, and how to use them to discover duplicate commits?](https://www.linkedin.com/pulse/git-hooks-what-how-use-them-discover-duplicate-candido-guedes/)
* Integrating Jira and Git Hook to automate the validation of commit messages (in proccess)

## Getting Started

The step-by-step installation instructions of each hook are inside of its folder on README.md files.

You basically needs: 
- download both commit/src/commit-msg, commit/src/commit-verify.py, install.sh, and requirements.txt files to use commit-msg hook.
  - execute the install.sh file to install all requirentements present inside requirements.txt file
- download rebase/src/post-rewrite file to use post-rewrite hook.
- put these files inside the .git/hooks folder present in your project folder.
- grant execution permission to both post-rewrite, commit-msg and commit-verify.py files.

## Built With

* [Git Hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) - Git Hooks terminology
* [Shell Script](https://www.gnu.org/software/bash/manual/html_node/Shell-Scripts.html) - programming language used to create both hooks
* [Python 3](https://www.python.org/download/releases/3.0/) - programming language used to create the validation commit message program called by the commit-msg hook
* [Jira API](https://developer.atlassian.com/cloud/jira/platform/rest/v2/) - Atlassian API to access Jira's information
* [requests](https://requests.readthedocs.io/en/master/) - HTTP library for Python
