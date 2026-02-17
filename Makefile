.PHONY: install clean run-prep run-analysis test docker-build docker-run-prep

install:
	pip install -e .

clean:
	rm -rf build/ dist/ *.egg-info
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -exec rm -f {} +

run-prep:
	python src/main.py --task prep

run-analysis:
	python src/main.py --task analyze

test:
	pytest tests/

docker-build:
	docker build -t sentiment-analysis:latest .

docker-run-prep:
	docker run -v $(PWD)/data:/app/data -v $(PWD)/logs:/app/logs sentiment-analysis:latest --task prep
