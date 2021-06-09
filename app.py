from flask import Flask, render_template, jsonify, request
import csv
import os
import boto3
import io

app = Flask(__name__)

@app.route('/')
def home():
	return render_template("experiment.html")

@app.route('/consent.html')
def consent():
	return render_template("consent.html")

@app.route('/get-list', methods=['GET'])
def get_list():
	num = cvs_num()
	if num == -1:
		return "Something wrong happened", 500
	parent_dir = os.path.dirname(os.path.abspath(__file__))
	filename = os.path.join(parent_dir, 'stimuli/stim_list_' + str(num) + '.csv')
	stim_list = []
	with open(filename, 'r') as f:
		for rec in csv.reader(f, delimiter=","):
			for x in rec:
				stim_list.append(int(x))
	return jsonify({"resp": stim_list, "num": num})

@app.route('/save-data', methods=['POST'])
def save_data():
	num = int(request.form["num"])
	results_raw = request.form.getlist("results[]")
	results = [int(x) for x in results_raw]
	results.insert(0, num)
	print(results)

	all_results = []
	s3 = boto3.resource('s3')
	obj = s3.Object('psy454', 'results_v2.csv')
	with io.StringIO(obj.get()['Body'].read().decode('utf-8')) as fp:
		reader = csv.reader(fp)
		for row in reader:
			all_results.append(row)
	
	all_results.append(results)
	with io.StringIO() as buffer:
		writer = csv.writer(buffer)
		for result in all_results:
			writer.writerow(result)
		obj.put(Body=buffer.getvalue())
	return "OK"

@app.route('/exit-early', methods=['POST'])
def exit_early():
	num = int(request.form["num"])
	s3 = boto3.resource('s3')
	obj = s3.Object('psy454', 'available_lists_v2.csv')
	available_list = []
	with io.StringIO(obj.get()['Body'].read().decode('utf-8')) as fp:
		reader = csv.reader(fp)
		for row in reader:
			for item in row:
				available_list.append(int(item))

	available_list.append(num)
	available_list = sorted(available_list)
	with io.StringIO() as buffer:
		writer = csv.writer(buffer)
		writer.writerow(available_list)
		obj.put(Body=buffer.getvalue())
	return "OK"

def cvs_num():
	s3 = boto3.resource('s3')
	obj = s3.Object('psy454', 'available_lists_v2.csv')
	available_list = []
	with io.StringIO(obj.get()['Body'].read().decode('utf-8')) as fp:
		reader = csv.reader(fp)
		for row in reader:
			for item in row:
				available_list.append(int(item))
	if len(available_list) == 0:
		return -1
	curr = min(available_list)
	print(available_list)
	print(curr)
	available_list.remove(curr)
	with io.StringIO() as buffer:
		writer = csv.writer(buffer)
		writer.writerow(available_list)
		obj.put(Body=buffer.getvalue())
	return curr


if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)