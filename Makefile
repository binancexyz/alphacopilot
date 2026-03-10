PYTHON=python3

.PHONY: token wallet watchtoday signal check test runtime-demo api bridge-api square-draft square-publish diary-morning diary-night education-post market-open builder-post ecosystem-post motivation-post install-diary-cron

token:
	$(PYTHON) src/main.py token BNB

wallet:
	$(PYTHON) src/main.py wallet 0x1234567890ab

watchtoday:
	$(PYTHON) src/main.py watchtoday

signal:
	$(PYTHON) src/main.py signal DOGE

runtime-demo:
	$(PYTHON) src/runtime_demo.py token BNB examples/payloads/token-bnb.json

api:
	uvicorn src.api:app --host 0.0.0.0 --port 8000

bridge-api:
	uvicorn src.bridge_api:app --host 0.0.0.0 --port 8010

square-draft:
	$(PYTHON) src/square_cli.py token BNB

square-publish:
	$(PYTHON) src/square_cli.py token BNB --publish

diary-morning:
	$(PYTHON) src/square_diary.py morning-diary

education-post:
	$(PYTHON) src/square_diary.py education-1

market-open:
	$(PYTHON) src/square_diary.py market-open

builder-post:
	$(PYTHON) src/square_diary.py builder-1

ecosystem-post:
	$(PYTHON) src/square_diary.py ecosystem-1

motivation-post:
	$(PYTHON) src/square_diary.py motivation-1

diary-night:
	$(PYTHON) src/square_diary.py night-diary

install-diary-cron:
	bash scripts/install_square_diary_cron.sh

check:
	$(PYTHON) -m py_compile src/main.py src/runtime_demo.py src/config.py src/api.py src/bridge_api.py src/square_cli.py src/analyzers/*.py src/formatters/*.py src/models/*.py src/services/*.py src/utils/*.py tests/*.py

test:
	$(PYTHON) tests/run_tests.py
