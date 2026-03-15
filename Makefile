PYTHON=python3

.PHONY: brief portfolio wallet holdings watchtoday signal audit alpha futures check test test-live api bridge-api bridge-live square-draft square-publish diary-morning diary-night daily-post install-diary-cron

brief:
	$(PYTHON) src/main.py brief BNB

portfolio:
	$(PYTHON) src/main.py portfolio

wallet:
	$(PYTHON) src/main.py wallet 0x1234567890ab

holdings:
	$(PYTHON) src/main.py holdings 0x1234567890ab

watchtoday:
	$(PYTHON) src/main.py watchtoday

signal:
	$(PYTHON) src/main.py signal DOGE

audit:
	$(PYTHON) src/main.py audit BNB

alpha:
	$(PYTHON) src/main.py alpha

futures:
	$(PYTHON) src/main.py futures BTC

api:
	uvicorn src.api:app --host 0.0.0.0 --port 8000

bridge-api:
	uvicorn src.bridge_api:app --host 0.0.0.0 --port 8010

bridge-live:
	bash -lc 'set -a && source .env && set +a && .venv/bin/python -m uvicorn src.bridge_api:app --host 127.0.0.1 --port 8010'

square-draft:
	$(PYTHON) src/square_cli.py token BNB

square-publish:
	$(PYTHON) src/square_cli.py token BNB --publish

diary-morning:
	$(PYTHON) src/square_diary.py morning-diary

diary-night:
	$(PYTHON) src/square_diary.py night-diary

daily-post: diary-night

install-diary-cron:
	bash scripts/install_square_diary_cron.sh

check:
	$(PYTHON) -m py_compile src/*.py src/analyzers/*.py src/formatters/*.py src/models/*.py src/services/*.py src/utils/*.py tests/*.py

test:
	$(PYTHON) tests/run_tests.py

test-live:
	LIVE_TESTS=1 $(PYTHON) tests/run_tests.py
