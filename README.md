# SecureCloud Management SDK for python

python interface SDK for SecureCloud Management API

## Prerequisites
- PyCrypto >= 2.6
	- https://pypi.python.org/pypi/pycrypto
	- For windows pre-compiled version at http://www.voidspace.org.uk/python/modules.shtml#pycrypto

## SCLIB Configuration

- There are 2 path for default configuration file
	- /etc/sclib.config
	- put `.sclib.config` file in your home folder
		- ~/.sclib.config (for Linux)
		- c:\Users\ `<user name>` \ .sclib.config (for Windows)

Config sample:
*********************
	[connection]
	MS_HOST = https://ms.cloud9.identum.com:7443/broker/API.svc/v3.5
	MS_BROKER_PATH = /broker/API.svc/v3.5/
	MS_BROKER_NAME = bobby
	MS_BROKER_PASSPHASE = <your passphase>

	[authentication]
	AUTH_NAME = bobby_chien@trendmicro.com
	AUTH_PASSWORD = <your password>
*********************

## Unit Test

### Configuration:
	/tests/unit/test.cfg

### Testing:
	cd tests/unit/
	python -m unittest discover

