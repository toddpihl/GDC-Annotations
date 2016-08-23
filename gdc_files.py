#!/usr/bin/python
import requests
import json

#import urllib
#import urllib2

legacy_url = "https://gdc-api.nci.nih.gov/legacy/"
standard_url = "https://gdc-api.nci.nih.gov/"
status_endpoint = "status"
files_endpoint = "files"
cases_endpoint = "cases"
cases_query = "?field=submitter_id&value=TCGA-KC-A7FE"

f = {
	"op" : "=",
	"content" : {
		"field" : "submitter_id",
		"value" : ["TCGA-KC-A7FE"]
	}
}

params = {"filters" : json.dumps(f)}

#print json.dumps(params, indent=2)

response = requests.get(legacy_url + cases_endpoint,params=params)

print json.dumps(response.json(), indent=2)
