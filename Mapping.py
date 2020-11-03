#!/usr/bin/env python3
################################################################################
#
# Script to create the data structure in elasticsearch
#
################################################################################

# import Elasticsearch package
from elasticsearch import Elasticsearch

gProjectsIndex = 'projects'
gProjectIssuesIndex = 'projects_issues'

# connect to the elastic cluster
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# projects
if (es.indices.exists(gProjectsIndex)):
    es.indices.delete(gProjectsIndex)

resp = es.indices.create(
    index=gProjectsIndex,
    body={
        "mappings": {
            "properties": {
                "key": {
                    "type": "keyword"
                },
                "last_update": {
                    "type": "date",
                    "format": "epoch_second"
                }
            }
        }
    }
)
print(resp)

# issues
if (es.indices.exists(gProjectIssuesIndex)):
    es.indices.delete(gProjectIssuesIndex)

resp = es.indices.create(
    index=gProjectIssuesIndex,
    body={
        "mappings": {
            "properties": {
                "project": {
                    "type": "keyword"
                },
                "key": {
                    "type": "keyword"
                },
                "creation_date": {
                    "type": "date",
                    "format": "epoch_second"
                },
                "update_date": {
                    "type": "date",
                    "format": "epoch_second"
                },
                "closing_date": {
                    "type": "date",
                    "format": "epoch_second"
                },
                "type": {
                    "type": "keyword",
                    "null_value": "NULL"
                },
                "priority": {
                    "type": "keyword",
                    "null_value": "NULL"
                },
                "affects_versions": {
                    "type": "keyword",
                    "null_value": "NULL"
                },
                "fix_version": {
                    "type": "keyword",
                    "null_value": "NULL"
                },
                "components": {
                    "type": "keyword",
                    "null_value": "NULL"
                },
                "epic": {
                    "properties": {
                        "status": {
                            "type": "keyword",
                            "null_value": "NULL"
                        },
                        "type": {
                            "type": "keyword",
                            "null_value": "NULL"
                        }
                    }
                },
                "sil": {
                    "type": "keyword",
                    "null_value": "NULL"
                },
                "status": {
                    "type": "keyword",
                    "null_value": "NULL"
                },
                "resolution": {
                    "type": "keyword",
                    "null_value": "NULL"
                },
                "labels": {
                    "type": "keyword",
                    "null_value": "NULL"
                },
                "defect_source": {
                    "type": "keyword",
                    "null_value": "NULL"
                },
                "quality_time": {
                    "type": "keyword",
                    "null_value": "NULL"
                }
            }
        }
    }
)
print(resp)
