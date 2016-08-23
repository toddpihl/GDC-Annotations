#!/usr/bin/python

import GDC_Stuff as gdc
import json
import requests
import sys
import datetime

def getTCGAProjects():
	# Get a listing of all the projects and only grab the TCGA projects
	# Yes, this is a dumb way of doing it, but there doesn't appear to be a query to get just TCGA studies
	projects = []
	page = 1
	pfrom = 1
	pages = 1
	size = 10
	url = ""
	
	while page <= pages:
		url = "https://gdc-api.nci.nih.gov/projects?from=" + str(pfrom) + "&sort=project.project_id:asc&pretty=true"
		response = requests.get(url)
		data = response.json()
		pages = data['data']['pagination']['pages']
		for project in data['data']['hits']:
			project_id = project['project_id']
			if "TCGA-" in project_id:
				projects.append(project_id)
		page += 1
		pfrom = pfrom + size
	
	return projects
	
def getPatientsByProject(project_id):
	id_list = []
	page = 1
	pages = 1
	pfrom = 1
	retry = 1
	size = 100
	while page <= pages:
		if retry <= 3:
			query = {
				"fields": "submitter_id",
				"size" : size,
				"from" : pfrom,
				"filters": {"content": {"field": "project.project_id", "value": [project_id]}, "op": "="}
			}
		
			response = gdc.basic_gdc_api_post(False,"cases",query)

			if response.status_code == requests.codes.ok:
				data = response.json()
				pages = data['data']['pagination']['pages']
		
				#print "Page %s of %s" % (str(page), pages)
				for response in data['data']['hits']:
					patient_id = response['submitter_id']
					id_list.append(patient_id)
			
				page += 1
				pfrom = pfrom + size
			else:
					print "Bad request: %s" % (str(response.status_code))
					print query
					retry += 1
		else:
			print "Connection issues, failed too many times"
			sys.exit()
		
	return id_list


def getCaseAnnotations(patient):
	#only get approved annotations, ignore the rescinded
	annoList = []
	anno = {"status" :"n/a","category" : "n/a","classification" : "n/a","notes" : "n/a","entity_submitter_id" : "n/a"}
	
	query = {
		"fields" : "status,category,classification,notes,entity_submitter_id",
		"filters" : {
			"op": "and",
			"content": [{
				"op" : "=",
				"content" : {"field": "case_submitter_id", "value": [patient]}
				},
				{
				"op" : "=",
				"content" : {"field" : "status", "value" : ["Approved"]}
				}
			]}
	}
	
	response = gdc.basic_gdc_api_post(False,"annotations", query)
	data = response.json()
	
	count = data['data']['pagination']['count']
	if count > 0:
		#print query
		#print json.dumps(response.json(), indent = 2)
		# data->hits is a list!
		anno = {"status" :"n/a","category" : "n/a","classification" : "n/a","notes" : "n/a","entity_submitter_id" : "n/a"}
		for annotation in data['data']['hits']:
			#All of the if statements here were added because GDC legacy annotations don't always have all the fields
			#and that was causing parsing failures
			if 'status' in annotation:
				anno['status'] = annotation['status']
			if 'category' in annotation:
				anno['category'] = annotation['category']
			if 'classification' in annotation:
				anno['classification'] = annotation['classification']
			if 'notes' in annotation:
				anno['notes'] = annotation['notes']
			if 'entity_submitter_id' in annotation:
				anno['entity_submitter_id'] = annotation['entity_submitter_id']
			annoList.append(anno)
	else:
		annoList.append(anno)
		
	return annoList
	

def main():
	#projects = getTCGAProjects()
	projects = ["TCGA-GBM"]
	print "Found %s projects" % (str(len(projects)))
	for project in projects:
		print project
		filename = project + "_annotations.txt"
		annofile = open(filename,"w")
		patientList = getPatientsByProject(project)
		#print "Project %s has %s patients" % (project, str(len(patientList)))
		annofile.write("Patient\tAnnotated Barcode\tStatus\tClassification\tCategory\tNotes\n")
		for patient in patientList:
			# l will be a list of hashes
			l = getCaseAnnotations(patient)
			for a in l:
				annofile.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (patient,a['entity_submitter_id'],a['status'],a['classification'],a['category'],a['notes']))
		annofile.close()
	

if __name__ == '__main__':
	main()
