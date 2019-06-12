PYTHON_CMD:=source venv/bin/activate && source .secrets && python3

all: venv check

venv:
	python3 -m venv venv
	source venv/bin/activate && pip3 install https://github.com/CSCfi/tauhka/archive/v0.0.1.zip

.secrets:
	cp .secrets.template .secrets
	nano .secrets

chromedriver:
	#curl -O https://chromedriver.storage.googleapis.com/75.0.3770.8/chromedriver_mac64.zip
	curl -O https://chromedriver.storage.googleapis.com/74.0.3729.6/chromedriver_mac64.zip
	unzip chromedriver_mac64.zip

clean:
	rm -f chromedriver
	rm -f chromedriver_*.zip
	rm -f *-networktraffic.json
	rm -fr __pycache__
	rm -rf venv

check: .secrets venv chromedriver
	$(PYTHON_CMD) -m unittest discover

my_datasets: .secrets venv chromedriver
	$(PYTHON_CMD) -m unittest -k my_datasets
