.PHONY: install run run-stdio preview clean

install:
	uv sync

NAMESPACE ?= mcp-servers
BROKER_URL ?= http://localhost:8080
ADDR ?= :8899

run:
	uv run mcp-gateway-admin --transport http --addr $(ADDR) --namespace $(NAMESPACE) --broker-url $(BROKER_URL)

run-stdio:
	uv run mcp-gateway-admin

preview:
	uv run fastmcp dev apps server.py:main

clean:
	rm -rf __pycache__ tools/__pycache__ *.egg-info dist .eggs .venv
