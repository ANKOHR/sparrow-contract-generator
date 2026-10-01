import json
import pytest
from sparrow_contract_generator.fixtures import generate
from sparrow_contract_generator.cli import read_input

@pytest.fixture
def dataset(tmp_path):
    generate(tmp_path)
    return tmp_path, read_input(tmp_path)
