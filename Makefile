PYTHON=python3

.PHONY: token wallet watchtoday signal check test runtime-demo api bridge-api square-draft square-publish

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

check:
	$(PYTHON) -m py_compile src/main.py src/runtime_demo.py src/config.py src/api.py src/bridge_api.py src/square_cli.py src/analyzers/*.py src/formatters/*.py src/models/*.py src/services/*.py src/utils/*.py tests/*.py

test:
	$(PYTHON) tests/run_tests.py
