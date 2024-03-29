#Create an Oracle Object Storage Bucket and create a readme.txt file in it in response to an event
#Author: Samir Shah, Credit: Greg Verstraeten  
import io
import logging
import json
import os
import sys
import datetime
from fdk import response
from oci.object_storage.models import CreateBucketDetails

import oci.object_storage

def handler(ctx, data: io.BytesIO=None):
    signer = oci.auth.signers.get_resource_principals_signer()
    try:
        body = json.loads(data.getvalue())
        resourceName = body["data"]["resourceName"]
        eventType = body["eventType"]
        source = body["source"]
        logging.info('***eventType:' + eventType + ' resourceName:' + resourceName)
    except Exception as e:
        error = "Error receiving JSON input:" + e
        raise Exception(error)
    resp = create_bucket(signer,eventType,resourceName)
    return response.Response(
        ctx,
        response_data=json.dumps(body),
        headers={"Content-Type": "application/json"}
    )

def put_object(signer, bucketName, objectName, content):
    client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    try:
        object = client.put_object(os.environ.get("OCI_NAMESPACE"), bucketName, objectName, json.dumps(content))
        output = "Success: Put object '" + objectName + "' in bucket '" + bucketName + "'"
    except Exception as e:
        output = "Failed: " + str(e.message)
    response = { "state": output }
    return response

def create_bucket(signer, eventType, resourceName):
	currentDT = datetime.datetime.now()
	objectName = 'readme.txt'
	content = 'Generated by automated event based function. This bucket is Oracle confidential.'
	client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
	request = CreateBucketDetails()
	request.compartment_id = signer.compartment_id
	request.name = resourceName+'-fnGenBucket-'+currentDT.strftime("%Y-%m-%d-%H-%M-%S") #bucketName
	namespace = os.environ.get("OCI_NAMESPACE")
	try:
		bucket = client.create_bucket(namespace, request)
		output = "Success creating the bucket!" 
		put_object(signer, request.name, objectName, content)
	except Exception as e:
		output = "Failed to create bucket:" + str(e.message)
	response = { "state": output }
	return response
