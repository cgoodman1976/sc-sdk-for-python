# SecureCloud Management SDK for python

python interface SDK for SecureCloud Management API

## Prerequisites
- PyCrypto >= 2.6
	- https://pypi.python.org/pypi/pycrypto
	- For windows pre-compiled version at http://www.voidspace.org.uk/python/modules.shtml#pycrypto
	
## SCLIB Installation (optional)
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
	MS_HOST = https://ms.cloud9.identum.com:7443/broker/API.svc/v3.5
	MS_BROKER_PATH = /broker/API.svc/v3.5/
	MS_BROKER_NAME = <your broker name>
	MS_BROKER_PASSPHASE = <your passphase>

	[authentication]
	AUTH_NAME = <your account(email)>
	AUTH_PASSWORD = <your password>

## Unit Test

### Testing:
	cd tests/unit/
	python -m unittest discover

