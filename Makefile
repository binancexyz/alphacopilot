PYTHON=python3

.PHONY: token wallet watchtoday signal check test

token:
	$(PYTHON) src/main.py token BNB

wallet:
	$(PYTHON) src/main.py wallet 0x1234567890ab

watchtoday:
	$(PYTHON) src/main.py watchtoday

signal:
	$(PYTHON) src/main.py signal DOGE

check:
	$(PYTHON) -m py_compile src/main.py src/config.py src/analyzers/*.py src/formatters/*.py src/models/*.py src/services/*.py src/utils/*.py tests/*.py

test:
	$(PYTHON) tests/run_tests.py
