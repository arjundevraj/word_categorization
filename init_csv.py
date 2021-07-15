import csv
import boto3
import io

available_list = []
for i in range(101, 901):
	available_list.append(int(i))
print(available_list)
print(len(available_list))
s3 = boto3.resource('s3')
obj = s3.Object('psy454', 'available_lists_v2.csv')
with io.StringIO() as buffer:
	writer = csv.writer(buffer)
	writer.writerow(available_list)
	obj.put(Body=buffer.getvalue())