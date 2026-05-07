# LWA developer Makefile
#
# Common commands for the engine surfaces. Targets are intentionally
# minimal so they layer on top of the existing repo without conflicting
# with the deploy/ci configs in lwa-backend/nixpacks.toml or
# lwa-web/railway.toml.
#
# Usage:
#   make help
#   make smoke-engines                 # curl loop over /engines
#   make engine-cli ENGINE=brain       # run the local Python CLI
#   make engine-service ENGINE=brain   # boot a single-engine service on :8001
#   make backend-compile
#   make backend-test
#   make web-typecheck
#   make web-build

API_BASE ?= http://localhost:8000
ENGINE   ?= operator_admin
PORT     ?= 8001

.PHONY: help smoke-engines engine-cli engine-service \
        backend-compile backend-test web-typecheck web-build web-lint

help:
	@echo "LWA Make targets:"
	@echo "  smoke-engines           Run scripts/smoke_engines.sh against $$API_BASE."
	@echo "  engine-cli ENGINE=<id>  Run the local engine demo CLI (no server needed)."
	@echo "  engine-service ENGINE=<id> [PORT=8001]"
	@echo "                          Boot one engine via app.services.engine_service_app."
	@echo "  backend-compile         python3 -m compileall app (lwa-backend)."
	@echo "  backend-test            pytest engine + service tests (lwa-backend)."
	@echo "  web-typecheck           tsc --noEmit (lwa-web)."
	@echo "  web-build               next build (lwa-web)."
	@echo "  web-lint                next lint (lwa-web)."

smoke-engines:
	API_BASE=$(API_BASE) ./scripts/smoke_engines.sh

engine-cli:
	cd lwa-backend && python3 scripts/engine_demo.py $(ENGINE) '$(PAYLOAD)'

engine-service:
	cd lwa-backend && \
	  LWA_ENGINE_SERVICE_ID=$(ENGINE) \
	  uvicorn app.services.engine_service_app:app --host 0.0.0.0 --port $(PORT)

backend-compile:
	cd lwa-backend && python3 -m compileall -q app

backend-test:
	cd lwa-backend && python3 -m pytest \
	  tests/test_engines.py \
	  tests/test_engine_service_runtime.py \
	  tests/test_engine_service_app.py -q

web-typecheck:
	cd lwa-web && npm run type-check

web-build:
	cd lwa-web && npm run build

web-lint:
	cd lwa-web && npm run lint
