import requests
import sys

def get_city():

	url = "http://127.0.0.1:5000/yelp/variables/city"

	r = requests.get(url)

	cities = r.json()['city']
	end = False

	while not end:

		print '\n'
		print "[",
		for city in cities:
			print str(city) + '; ',
		print "]"
		print '\n'
		city = input('Please select and insert one city from the list above with double quotes around (for example: "Mesa"):\n') 
		print '\n'
		if city in cities:
			end = True

	return city


def get_attribute_pair():

	url = "http://127.0.0.1:5000/yelp/variables/attributes"
	r = requests.get(url)
	attributes = r.json()['attributes']
	end = False

	attribute_list = []

	while not end:

		print '\n'

		attributes = [str(attribute) for attribute in attributes]
		print "[",
		for attribute in attributes:
			print attribute + '; ',
		print "]"
		print '\n'

		attribute_raw = input('Please select and insert one attribute from the list above with double quotes around (for example: "Parking"):\n') #"'Parking'"
		
		print '\n'

		if attribute_raw in attributes:
			attribute_mod = "'" + attribute_raw + "'"
			attribute_list.append(attribute_mod)

			attribute = ','.join(attribute_list)
			url = "http://127.0.0.1:5000/yelp/variables/attributes" + "?attribute=" + attribute
			r = requests.get(url)
			output = r.json()

			if 'error_code' in output:
				if output['error_code'] == '22023':
					end = True
				else:
					print 'Error: ', output['error_msg']
					sys.exit()
			
			# elif len(output['attributes']) == 0:
				# attributes = attributes
			else:
				attributes = output['attributes']

	attribute_return = attribute.replace("'","")
	

	url = "http://127.0.0.1:5000/yelp/variables/attributes" + "?attribute_key=" + attribute
	r = requests.get(url)
	attributes = r.json()['attributes']
	
	end = False

	while not end:
		print '\n'
		print 'You have selected ' + attribute_return
		print '\n'

		attributes = [str(attribute) for attribute in attributes]
		print "[",
		for attribute in attributes:
			print attribute + '; ',
		print "]"
		print '\n'
		
		value = input('Please select and insert one condition for your selected attribute from the list above with double quotes around (for example: "true"):\n')
		print '\n'
		if value in attributes:
			end = True
		
	
	return attribute_return, value


def get_stats(city, attribute_key=None, attribute_value=None):
	if attribute_key:
		url = "http://127.0.0.1:5000/yelp/starstats/" + city + "?attribute_key=" + attribute_key + "&attribute_value=" + attribute_value
	else:
		url = "http://127.0.0.1:5000/yelp/starstats/" + city
	
	r = requests.get(url)
	stats = r.json()
	
	return stats

def get_lr():
	pass





def run_app(function):
	city = get_city()
	attribute_parameter = input('Do you want to give a attribute parameter?(True or False):\n')

	if function == 'stats':
		if attribute_parameter:
			attribute_key, attribute_value = get_attribute_pair()	
			stats = get_stats(city, attribute_key, attribute_value)
			# print stats
			print '\n'
			print 'In ' + stats['city'] + ", for attribute '" + stats['attribute'] + "' , the average star rating is " + str(stats['avg_stars']) + ' and the standard deviation is ' + str(stats['std_stars'])
		else:
			stats = get_stats(city)
			# print stats
			print '\n'
			print 'In ' + stats['city'] + ", for attribute '" + stats['attribute'] + "' , the average star rating is " + str(stats['avg_stars']) + ' and the standard deviation is ' + str(stats['std_stars'])
	elif function == 'linear regression':
		if attribute_parameter:
			attribute_key, attribute_value = get_attribute_pair()			
			print 'linear regression', attribute_key, attribute_value
		else:
			print 'linear regression'



print '\n'
function = input('Do you want to have basic statistics or perform linear regression? ("stats" or "linear regression")\n')

run_app(function)

