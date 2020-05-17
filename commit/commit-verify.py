# !/usr/bin/python3

import sys
import re
import subprocess
from datetime import datetime
from enum import Enum
import requests
from requests.auth import HTTPBasicAuth
import json
import signal
import time

# To get your api token you just need to access https://id.atlassian.com/manage-profile/security/api-tokens and create one
api_token = 'YOUR_GENERATED_API_TOKEN' 
user_email = 'EMAIL_USED_ON_ATLASSIAN'

server = 'YOUR_SERVER_ON_JIRA'
api_url = 'rest/api/2/issue/'

# API connection time out
time_out = 5


MESSAGE_REGEX='(JIRA-[0-9]+|Merge)'

blocked_branchs=['develop', 'master', 'release']

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



class TimeOutException(Exception):
	pass



class JiraFieldsEnum(Enum):
	"""
	Used Fields ID on Jira Project
	These codes are generated automatically when you create a Jira project. It might don't exists in your context or even use different ids
	"""
	DEVELOPER='customfield_14741'
	CODE_REVIEWER='customfield_14742'
	REVIEWER='customfield_14743'
	JIRA_PARENT='parent'
	KEY='key'
	FIELDS='fields'
	DISPLAY_NAME='displayName'
	EMAIL_ADRESS='emailAddress'



class JiraUser:
	def __init__(self, object):
		if object is not None:
			self.name = object[JiraFieldsEnum.DISPLAY_NAME.value]
			if JiraFieldsEnum.EMAIL_ADRESS.value in object.keys():
				self.email = object[JiraFieldsEnum.EMAIL_ADRESS.value]
		else: 
			pass



class JiraIssue:
	def __init__(self, object):
		fields = object[JiraFieldsEnum.FIELDS.value]
		self.key = object[JiraFieldsEnum.KEY.value]
		self.developer = JiraUser(fields[JiraFieldsEnum.DEVELOPER.value])
		self.code_reviewer = JiraUser(fields[JiraFieldsEnum.CODE_REVIEWER.value])
		self.reviewer = JiraUser(fields[JiraFieldsEnum.REVIEWER.value])

		if JiraFieldsEnum.JIRA_PARENT.value in fields.keys():
			parent_attr = fields[JiraFieldsEnum.JIRA_PARENT.value]
			self.parent = build_issue_from_jira(parent_attr[JiraFieldsEnum.KEY.value])
		else:
			self.parent = None



def log(message, style):
	now = datetime.now()
	current_time = now.strftime("%H:%M:%S")
	
	print(style + '[' + current_time + '] ' + message + bcolors.ENDC)



def connect_and_get_issue(issue_number):
	"""
	This function connect to jira api using user_email and api_token variables.
	Once connected, use this connection to get the issue and return it.
	Args:
			string: Jira's key
	Returns:
			object: Jira's issue
	"""

	signal.alarm(time_out)

	auth = HTTPBasicAuth(user_email, api_token)
	headers = {
		'Accept': 'application/json'
	}

	url = server + api_url + issue_number


	response = requests.request(
		'GET',
		url,
		headers=headers,
		auth=auth
	)

	signal.alarm(0)
	return json.loads(response.text)



def get_current_branch_name():
	"""Gets the current GIT branch name.
	Returns:
		string: The current branch name.
	"""
	branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
	return branch_name.decode("utf-8").rstrip()


def build_issue_from_jira(key):
	try:
		response_issue = connect_and_get_issue(key)
		issue = JiraIssue(response_issue)
		return issue
	except:
		raise



def give_commit_decision_to_user(message):
	choice = input(bcolors.BOLD + message + bcolors.ENDC)
	if choice.lower() == 'y':
		log('Proceeding with the commit ...', bcolors.OKBLUE)
		return True
	else:
		log('Aborting commit ...', bcolors.FAIL)
		return False



def is_merge(message):
	matches = re.findall(MESSAGE_REGEX, message)
	return matches and matches[0] == 'Merge'



def valid_commit_jira(message):
	"""
	This function uses the commit message and verify if it is doing a merge or a simple commit. 
	If it is a simple commit the following analysis will be done:
		- Is there a Jira's issue number in the commit's message?
			- It's not allowed to commit without this number
		- Is this issue a subtask?
			-	It's not recommended to commit on a subtask

	Args:
		string: commit message
	"""
	matches = re.findall(MESSAGE_REGEX, message)
	
	if matches and matches[0]:
		if matches[0] != 'Merge':
			log('Committing on issue: {0}'.format(matches[0]), bcolors.WARNING)

			try:		
				issue = build_issue_from_jira(matches[0])

				if issue.parent:
					log('Warning: Committing subtasks is not recommended. Current activity has the issue {0} as parent'.format(issue.parent.key), bcolors.WARNING)
					
					message_decision = 'Are you sure you want to continue the commit using the code {0}? (y/n)'.format(matches[0])
					return give_commit_decision_to_user(message_decision)
			except:
				message_decision = 'It will not be possible to analyze based on Jira. Do you want to continue with the commit anyway? (y/n)'
				return give_commit_decision_to_user(message_decision)
		else:
			return True
	else:
		log('ERROR: Aborting commit. Your commit message does not contain the Jira\'s issue number.', bcolors.FAIL)
		return False

	return True



def valid_commit_message(message):
	"""
	Function to validate the commit message.
	Args:
		message (str): The message to validate.
	Returns:
		bool: True for valid messages, False otherwise.
	"""
	current_branch = get_current_branch_name()
	log('Actual branch: {0}'.format(current_branch), bcolors.WARNING)

	if not is_merge(message) and current_branch in blocked_branchs:
		log('ERROR: Unable to commit to branch {0}'.format(current_branch), bcolors.FAIL)
		return False

	if not re.match(MESSAGE_REGEX, message):
		log('ERROR: Aborting commit. Your commit message does not contain the Jira\'s issue number.', bcolors.FAIL)
		return False

	jiras_code_is_valid = valid_commit_jira(message)
	if not jiras_code_is_valid:
		return False
	
	log('Commit message is valid. Proceeding...', bcolors.OKGREEN)
	return True



def alarm_handler(signum, frame):
	"""
	Call back function to be used on the signal timer
	"""
	log('The server is taking too long to respond.', bcolors.WARNING)
	raise TimeOutException()



def main():
  """Main function."""
  message_file = sys.argv[1]
  try:
    txt_file = open(message_file, 'r')
    commit_message = txt_file.read()
  finally:
    txt_file.close()

  if not valid_commit_message(commit_message):
    sys.exit(1)

  sys.exit(0)

signal.signal(signal.SIGALRM, alarm_handler)

main()
