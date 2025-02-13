import pytest
import os
import boto3
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
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

def run_manage_s3_files(args):
    runner = CliRunner()
    result = runner.invoke(manage_s3_files, args)
    return result

def test_manage_s3_files_with_yes(mock_env_file, mock_s3_client):
    result = run_manage_s3_files(["--checkLastDownload", "yes"])
    assert result.exit_code == 0, f"Failed with error: {result.output}"

def test_manage_s3_files_with_no(mock_env_file, mock_s3_client):
    result = run_manage_s3_files(["--checkLastDownload", "no"])
    assert result.exit_code == 0, f"Failed with error: {result.output}"

def test_manage_s3_files_without_param(mock_env_file, mock_s3_client):
    result = run_manage_s3_files([])
    assert result.exit_code == 0, f"Failed with error: {result.output}"
