#!/usr/bin/env python3
################################################################################
#
# Script to save the issues of jira in elasticsearch
#
################################################################################

# region Import packages
import sys
import math
from datetime import datetime
from elasticsearch import Elasticsearch
from jira import JIRA
# endregion

# region Settings
gProjects = [
    'BTVTMDEV',
]

gProjectsIndex = 'projects'
gProjectIssuesIndex = 'projects_issues'

# connect to the elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

options = {
    'server': 'https://jira.critical.pt'
}
# jira = JIRA(options, basic_auth=(sys.argv[1], sys.argv[2]))
#jira = JIRA(options, basic_auth=("svc-areabtkpistats", "N7vBbK2fBWf72fPcbmyy!")) #old user
jira = JIRA(options, basic_auth=("cd-btcpro", "W64nRz3Btk8kgNNPge6r"))
# endregion


# region Functions
# Get value with verifications
def get_value_from_object(var_object, var_propriety):
    if var_propriety in var_object:
        if var_object[var_propriety] != None:
            if 'value' in var_object[var_propriety]:
                return var_object[var_propriety]['value']
            elif 'name' in var_object[var_propriety]:
                return var_object[var_propriety]['name']
            else:
                return var_object[var_propriety]

    return 'NULL'


# Parse array from jira
def get_array_from_object(var_object, var_propriety):
    var_array = []

    if var_propriety in var_object:
        if var_object[var_propriety] != None:
            for var in var_object[var_propriety]:
                if 'name' in var:
                    var_array.append(var['name'])
                else:
                    var_array.append(var)

    return var_array if len(var_array) > 0 else 'NULL'


# Parse string (from jira format) to date
def parse_to_date(string_date):
    date = 0

    if string_date != '' and string_date != 'NULL':
        date = int(datetime.strptime(
            string_date[:-9], "%Y-%m-%dT%H:%M:%S"
        ).timestamp())

    return date
# endregion


# region Save issues
gDateNow = int(datetime.now().timestamp())

# Get issues
for project in gProjects:
    maxResults = 50
    startAt = 0
    updateLastHours = 0
    projectDocId = 0

    # region Get project's last update date
    search_resp = es.search(
        index=gProjectsIndex, body={
            'query': {'bool': {'filter': [{'term': {'key': project}}]}}}
    )

    # Get last update date
    if search_resp['hits']['total']['value'] >= 1:
        projectDocId = search_resp['hits']['hits'][0]['_id']
        updateLastHours = search_resp['hits']['hits'][0]['_source']['last_update']
        updateLastHours = 0 if updateLastHours == None else updateLastHours
    # If project not exists create a new
    else:
        temp = es.index(
            index=gProjectsIndex,
            body={
                'key': project,
                'last_update': 0
            }
        )
        projectDocId = temp['_id']
        print(f'Project {project} created!')

    print(projectDocId)

    # Transform in hours to search
    updateLastHours = math.ceil((gDateNow-updateLastHours)/60/60)
    print(updateLastHours)
    # endregion

    # Get all pagination
    while True:
        # Search issues
        response = jira.search_issues(
            f'project={project} and updated>=-{updateLastHours}h',
            maxResults=maxResults,
            startAt=startAt,
            fields='project,components,versions,fixVersions,created,updated,resolutiondate,issuetype,priority,customfield_11832,customfield_14833,customfield_15130,status,resolution,labels,customfield_14734,customfield_14630',
            json_result='true'
        )

        for issue in response['issues']:
            body = {
                "project": project,
                "key": issue['key'],
                "creation_date": parse_to_date(issue['fields']['created']),
                "update_date": parse_to_date(issue['fields']['updated']),
                "closing_date": parse_to_date(get_value_from_object(issue['fields'], 'resolutiondate')),
                "type": get_value_from_object(issue['fields'], 'issuetype'),
                "priority": get_value_from_object(issue['fields'], 'priority'),
                "affects_versions": get_array_from_object(issue['fields'], 'versions'),
                "fix_version": get_array_from_object(issue['fields'], 'fixVersions'),
                "components": get_array_from_object(issue['fields'], 'components'),
                "epic": {
                    "status": get_value_from_object(issue['fields'], 'customfield_11832'),
                    "type": get_value_from_object(issue['fields'], 'customfield_14833')
                },
                "sil": get_value_from_object(issue['fields'], 'customfield_15130'),
                "status": get_value_from_object(issue['fields'], 'status'),
                "resolution": get_value_from_object(issue['fields'], 'resolution'),
                "labels": get_array_from_object(issue['fields'], 'labels'),
                "defect_source": get_value_from_object(issue['fields'], 'customfield_14734'),
                "quality_time": get_value_from_object(issue['fields'], 'customfield_14630')
            }

            # check if doc exist
            query_body = {
                'query': {
                    'bool': {
                        'filter': [
                            {'term': {'key': issue['key']}},
                            {'term': {
                                'project': project
                            }}
                        ]
                    }
                }
            }
            search_resp = es.search(index=gProjectIssuesIndex, body=query_body)

            # If doc exist update
            if (search_resp['hits']['total']['value'] >= 1):
                es.update(
                    index=gProjectIssuesIndex,
                    id=search_resp['hits']['hits'][0]['_id'],
                    body={'doc': body}
                )
                print(f"{issue['key']}: Updated!")
            # Else create a new one
            else:
                es.index(
                    index=gProjectIssuesIndex,
                    body=body
                )
                print(f"{issue['key']}: Created!")

        # Check pagination
        startAt += maxResults
        if len(response['issues']) < maxResults:
            break

    # region Update project's last update
    es.update(
        index=gProjectsIndex,
        id=projectDocId,
        body={
            'doc': {
                'last_update': gDateNow
            }
        }
    )
    print(f'Project {project} updated!')
    # endregion
# endregion
