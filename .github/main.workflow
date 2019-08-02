
workflow "Build and Test" {
  on = "push"
  resolves = ["Test"]
}

action "Install" {
  uses = "nolanbconaway/python-actions@master"
  args = "pip install poetry && poetry install && poetry shell && which python"
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
  args = "pylint mta test -d C0303 -d C0412 -d C0330"
  needs = ["Install"]
}

action "Test" {
  uses = "nolanbconaway/python-actions@master"
  args = "pytest . -v"
  needs = ["Black", "Pydocstyle", "Pylint"]
}