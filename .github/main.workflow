
workflow "Build and Test" {
  on = "push"
  resolves = [
    "Test",
  ]
}

action "Install" {
  uses = "nolanbconaway/python-actions@master"
  args = "
  curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python && \
  poetry config settings.virtualenvs.in-project true && \
  poetry install && \
  source .venv/bin/activate \
  "
}

action "Lint" {
  uses = "nolanbconaway/python-actions@master"
  args = "
  black mta_realtime test --check --verbose && \
  pydocstyle mta_realtime test --verbose  && \
  pylint mta_realtime test -d C0303 -d C0412 -d C0330 \
  "
  needs = ["Poetry"]
}

action "Test" {
  uses = "nolanbconaway/python-actions@master"
  args = "pytest . -v"
  needs = ["Lint"]
}