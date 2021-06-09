import csv
import boto3
import io

s3 = boto3.resource('s3')
obj = s3.Object('psy454', 'results_v2.csv')
with io.StringIO() as buffer:
	obj.put(Body=buffer.getvalue())