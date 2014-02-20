# SecureCloud Management SDK for python

python interface SDK for SecureCloud Management API

## Prerequisites
- PyCrypto >= 2.6
	- https://pypi.python.org/pypi/pycrypto
	- For windows pre-compiled version at http://www.voidspace.org.uk/python/modules.shtml#pycrypto

## Install SCLIB (optional)
- Install sclib package to python

	> python setup.py install

## SCLIB Configuration

- Add sc-sdk-for-python folder into `PYTHONPATH` environment variable

- There are 2 path for default configuration file
	- /etc/sclib.config
	- put `.sclib.config` file in your home folder
		- ~/.sclib.config (for Linux)
		- c:\Users\ `<user name>` \ .sclib.config (for Windows)

Config sample:

	[connection]
	MS_HOST = https://ms.securecloud.com/broker/API.svc/v3.5
	MS_BROKER_NAME = <your broker name>
	MS_BROKER_PASSPHASE = <your passphase>
	SSL_VALIDATION = <Enable/Disable>

	[authentication]
	AUTH_NAME = <your account(email)>
	AUTH_PASSWORD = <your password>
	
Configuration Parameters:
- MS_HOST
URL for the SecureCloud Management API entry point
- MS_BROKER_NAME
Broker name. Please get this broker from Administrator
- MS_BROKER_PASSPHASE
Password of broker name. Please get this from Administrator
- SSL_VALIDATION
Enable/Disable SSL validation. When disabled, SDK will bypass HTTPS (SSL) certificate checking.
- AUTH_NAME
- AUTH_PASSWORD

## Unit Test

### Testing:
	cd tests/unit/
	python -m unittest discover


###Unit Test Result:

Default result folder:

    <sc-sdk-for-python>/tests/unit/result/

Naming Convention:

    Request Message: <result>/<TestClassName>.<TestMethod>/[Request]-<method> <api>.xml
    Response message: <result>/<TestClassName>.<TestMethod>/[Response]-<method> <api>.xml

## Server Certificate Validation

Default certificate file:

    <sc-sdk-for-python>/sclib/cacerts/cacert.pem
	
NOTE:

	Replace cacert.pem file if HTTPS (SSL) certificate is your own certificate.
    
