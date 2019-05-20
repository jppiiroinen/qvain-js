PYTHON_CMD:=source venv/bin/activate && source .secrets && python

all:

venv:
	python3 -m venv venv

.secrets:
	cp .secrets.template .secrets
	nano .secrets

chromedriver:
	#curl -O https://chromedriver.storage.googleapis.com/75.0.3770.8/chromedriver_mac64.zip
	curl -O https://chromedriver.storage.googleapis.com/74.0.3729.6/chromedriver_mac64.zip
	unzip chromedriver_mac64.zip

clean:
	rm chromedriver
	rm chromedriver_*.zip

check: .secrets venv chromedriver
	$(PYTHON_CMD) cscqvain*.py
