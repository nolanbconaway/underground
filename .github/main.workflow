
workflow "Build, Lint, Test" {
  on = "push"
  resolves = ["Pytest"]
}

action "Install" {
  uses = "nolanbconaway/python-actions@master"
  args = "pip install poetry && poetry install --extras cli && poetry shell && which python"
}

action "Black" {
  uses = "nolanbconaway/python-actions@master"
  args = "black mta test --check --verbose"
  needs = ["Install"]
}

action "Pydocstyle" {
  uses = "nolanbconaway/python-actions@master"
  args = "pydocstyle mta test --verbose"
  needs = ["Install"]
}

action "Pylint" {
  uses = "nolanbconaway/python-actions@master"
  args = "pylint mta test -d C0303,C0412,C0330,E1120"
  needs = ["Install"]
}

action "Pytest" {
  uses = "nolanbconaway/python-actions@master"
  args = "pytest . -v"
  needs = ["Black", "Pydocstyle", "Pylint"]
}