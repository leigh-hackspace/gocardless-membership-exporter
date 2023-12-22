.venv:
	python3 -m pip install poetry
	python3 -m poetry install --with test,github

lint: .venv
	python3 -m poetry run ruff --output-format=github --select=E9,F63,F7,F82 --target-version=py37 .
	python3 -m poetry run ruff --output-format=github --target-version=py37 .
