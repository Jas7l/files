# Test Automation Framework Makefile

.PHONY: help install setup-playwright clean run-all run-api run-ui run-smoke report

help:
	@echo "Restaurant Service Test Automation Framework"
	@echo ""
	@echo "Available commands:"
	@echo "  make install          - Install test dependencies"
	@echo "  make setup-playwright - Install Playwright browsers"
	@echo "  make clean            - Clean test artifacts"
	@echo "  make run-all          - Run all tests"
	@echo "  make run-api          - Run API tests"
	@echo "  make run-ui           - Run UI tests"
	@echo "  make run-smoke        - Run smoke tests"
	@echo "  make run-parallel     - Run tests in parallel"
	@echo "  make run-playwright   - Run Playwright UI tests"
	@echo "  make run-selenium     - Run Selenium UI tests"
	@echo "  make report           - Generate and open Allure report"
	@echo "  make logs             - Show recent test logs"
	@echo "  make lint             - Run code linting"
	@echo "  make watch            - Auto-run tests on changes"
	@echo "  make dev-setup        - Complete development setup"
	@echo ""
	@echo "File Storage Service Commands:"
	@echo "  make test-env-up      - Start test environment (Docker)"
	@echo "  make test-env-down    - Stop and clean test environment"
	@echo "  make test-env-clean   - Force clean test environment"
	@echo "  make test-files       - Run file storage API tests"
	@echo "  make test-files-smoke - Run smoke tests for file storage"
	@echo "  make test-files-debug - Run tests with debug output"

install:
	pip install -r requirements-test.txt
	@echo "Dependencies installed successfully"

setup-playwright:
	playwright install
	playwright install-deps
	@echo "Playwright browsers installed successfully"

clean:
	rm -rf allure-results allure-report
	rm -rf logs/test_*.log
	rm -rf storage/*
	rm -rf .pytest_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup completed"

run-all:
	pytest -v --tb=short
	@echo "All tests completed"

run-api:
	pytest api -v --tb=short
	@echo "API tests completed"

run-ui:
	pytest ui -v --tb=short
	@echo "UI tests completed"

run-smoke:
	pytest -m smoke -v --tb=short
	@echo "Smoke tests completed"

run-regression:
	pytest -m regression -v --tb=short
	@echo "Regression tests completed"

run-parallel:
	pytest -n auto -v --tb=short
	@echo "Parallel test execution completed"

run-playwright:
	pytest ui/playwright -v --tb=short
	@echo "Playwright UI tests completed"

run-selenium:
	pytest ui/selenium -v --tb=short
	@echo "Selenium UI tests completed"

run-headless:
	HEADLESS_MODE=true pytest -n auto -v --tb=short
	@echo "Headless tests completed"

report:
	allure serve allure-results
	@echo "Allure report generated and opened"

logs:
	@if [ -d logs ]; then \
		ls -lt logs/test_*.log | head -5; \
	else \
		echo "No logs directory found"; \
	fi

lint:
	@echo "Running code quality checks..."
	@command -v flake8 >/dev/null 2>&1 || { echo "flake8 not installed"; exit 1; }
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "Linting completed"

watch:
	pytest-watch -n auto

dev-setup: install setup-playwright
	@echo "Development environment setup completed"

test-env-up:
	@echo "🐳 Starting test environment..."
	docker-compose -f docker-compose.test.yml up -d
	@echo "Waiting for services to be ready..."
	sleep 5
	@echo "✅ Test environment is ready"
	@echo "  API: http://localhost:8020"
	@echo "  DB: localhost:5443"
	@echo "  Redis: localhost:6378"

test-env-down:
	@echo "🛑 Stopping test environment..."
	docker-compose -f docker-compose.test.yml down -v
	@echo "✅ Test environment stopped and cleaned"

test-env-clean:
	@echo "🧹 Force cleaning test environment..."
	docker-compose -f docker-compose.test.yml down -v
	docker volume prune -f
	@echo "✅ Cleanup completed"
