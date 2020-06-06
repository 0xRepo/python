## Description
	Assume we are developping AWS lambda layers that customers can use and configure in their aws account, when they configure their lambda functions. 
	We implement, build and test the layers, and then we deploy them in our AWS production account, in the AWS layer registry. When our customers want to use
	our layers, we need to whitelist the customer's AWS account id to the layer, i.e. we need to add a lambda layer permission to the customer aws account id.

	Note that we regularly update the layers with fixes and functionality. Also we have multiple different layers, one for each version of python supported by AWS (eg 3.6, 3.7, 3.8). Therefore the AWS layer registry has multiple layers each with multiple versions. When we add a lambda layer permission for a customer account id, we add the permission to all our types of layers, but only to the latest version for each type.

## Task
	Code a tool in python, that takes the following as input:
	* a customer aws account id
	* an aws region, and 
	* an aws profile
	
	Goal: adds permission to access the lambda layers, for the customer aws account id. 
	
	Note that the profile is the profile the person running the script has, and is to ensure that the person running the tool has the right privileges to run the tool. 


## Requirements
tox
boto3
jinja2
