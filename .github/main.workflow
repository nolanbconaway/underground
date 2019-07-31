
workflow "Build and Test" {
  on = "push"
  resolves = [
    "Test",
  ]
}

action "Install" {
  uses = "nolanbconaway/python-actions@master"
  args = "\
  curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python && \
  poetry config settings.virtualenvs.in-project true && \
  poetry install && \
  source .venv/bin/activate \
  which python"
}



action "Test" {
  uses = "nolanbconaway/python-actions@master"
  args = "pytest . -v"
  needs = ["Install"]
}