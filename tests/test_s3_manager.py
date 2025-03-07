import pytest
from unittest.mock import patch
from click.testing import CliRunner
from mex_invenio.scripts.s3_manager import manage_s3_files


@pytest.fixture
def mock_s3_client():
    with patch("boto3.client") as mock:
        yield mock


class MockResult:
    """A simple class to simulate Click's Result object"""

    def __init__(self, exit_code=0, output=""):
        self.exit_code = exit_code
        self.output = output


def run_manage_s3_files(args):
    runner = CliRunner()
    result = runner.invoke(manage_s3_files, args)
    return result


def test_manage_s3_files_with_yes(load_env, mock_s3_client):
    result = run_manage_s3_files(["--checkLastDownload", "yes"])
    assert result.exit_code == 0, f"Failed with error: {result.output}"


def test_manage_s3_files_with_no(load_env, mock_s3_client):
    result = run_manage_s3_files(["--checkLastDownload", "no"])
    assert result.exit_code == 0, f"Failed with error: {result.output}"


def test_manage_s3_files_without_param(load_env, mock_s3_client):
    result = run_manage_s3_files([])
    assert result.exit_code == 0, f"Failed with error: {result.output}"


def test_manage_s3_files_invalid_param(load_env, mock_s3_client):
    result = run_manage_s3_files(["--checkLastDownload", "invalid"])
    assert result.exit_code == 2, "Invalid parameter should return a non-zero exit code"
