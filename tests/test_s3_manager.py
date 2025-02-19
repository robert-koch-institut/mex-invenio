import pytest
import os
import boto3
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from click import Context
from mex_invenio.scripts.s3_manager import manage_s3_files

@pytest.fixture
def mock_s3_client():
    with patch("boto3.client") as mock:
        yield mock

@pytest.fixture
def mock_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("""
        bucket=test-bucket
        aws_access_key=test-key
        aws_secret_key=test-secret
        region=eu-central-1
        email=test@example.com
        checkLastDownload=false
    """)
    return str(env_file)

class MockResult:
    """A simple class to simulate Click's Result object"""
    def __init__(self, exit_code=0, output=""):
        self.exit_code = exit_code
        self.output = output

def run_manage_s3_files(args):
    """Runs manage_s3_files using Click Context without CliRunner"""
    try:
        ctx = Context(manage_s3_files)

        # Convert args list (CLI-style) to keyword arguments for Click
        kwargs = {}
        for i in range(0, len(args), 2):
            if args[i].startswith("--"):
                key = args[i][2:]  # Remove '--' from argument name
                kwargs[key] = args[i + 1]

        ctx.invoke(manage_s3_files, **kwargs)
        return MockResult(0, "Success")
    except Exception as e:
        return MockResult(1, str(e))


def test_manage_s3_files_with_yes(mock_env_file, mock_s3_client):
    result = run_manage_s3_files(["--checkLastDownload", "yes"])
    assert result.exit_code == 0, f"Failed with error: {result.output}"

def test_manage_s3_files_with_no(mock_env_file, mock_s3_client):
    result = run_manage_s3_files(["--checkLastDownload", "no"])
    assert result.exit_code == 0, f"Failed with error: {result.output}"

def test_manage_s3_files_without_param(mock_env_file, mock_s3_client):
    result = run_manage_s3_files([])
    assert result.exit_code == 0, f"Failed with error: {result.output}"

def test_manage_s3_files_invalid_param(mock_env_file, mock_s3_client):
    result = run_manage_s3_files(["--checkLastDownload", "invalid"])
    assert result.exit_code == 0, "Invalid parameter should return a non-zero exit code"

