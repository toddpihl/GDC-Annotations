#!/usr/bin/python
import requests
import json
import sys
	
legacy_url = "https://gdc-api.nci.nih.gov/legacy/"
standard_url = "https://gdc-api.nci.nih.gov/"
	
def basic_gdc_api_post(legacy,endpoint,query_json):
	#Sends the json and returns the result, nothing else
	#Note that for a POST, headers must be a dictionary, not json
	url = ""
	if legacy:
		url = legacy_url + endpoint
	else:
		url = standard_url + endpoint
	params = json.dumps(query_json)
	headers = {"content-type" : "application/json"}
	
	response = requests.post(url,headers=headers,data=params)
	return response
	
	
def query_gdc_api(legacy, endpoint,query_json):
	url = ""
	if legacy:
		url = legacy_url + endpoint
	else:
		url = standard_url + endpoint
	params = {"filters" : json.dumps(query_json)}
	#print params
	response = requests.get(url,params=params)
	return response
	
def query_gdc_limited_fields(legacy, endpoint, query_json, return_fields):
	url = ""
	if legacy:
		url = legacy_url + endpoint
	else:
		url = standard_url + endpoint
	params = {
		"fields" : return_fields,
		"filters" : json.dumps(query_json)
	}
	#print params
	response = requests.get(url,params=params)
	return response
	
		
def build_basic_json_query(operator,field,value):
	query = {
		"op" : operator,
		"content" : {
			"field" : field,
			"value" : [value]
		}
	}
	
	return query
	
def build_basic_json_query_with_start(operator,field,value,page,size):
	query = {
		"op" : operator,
		"from" : page,
		"fields" : "submitter_id",
		"size" : size,
		"content" : {
			"field" : field,
			"value" : [value]
		}
	}
	
	return query
	

def build_complex_json_query(operator,field,value):
	query = {
		"op" : "and",
		"content" : [{
			"op" : operator,
			"content" : {
				"field" : field,
				"value" : [value]
			}
		}]
	}
	#print query
	return query
		
