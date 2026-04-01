@echo off

set target=%1

if "%target%"=="install" goto install
if "%target%"=="lint" goto lint
echo invalid argument %target%
exit /b 1


:install
@REM sync and update git submodules
echo syncing git submodules
git submodule sync
git submodule update --init --recursive
if %errorlevel% neq 0 exit /b %errorlevel%

@REM install meta requirements system-wide
echo installing requirements
pip --disable-pip-version-check install --force-reinstall -r requirements.txt
if %errorlevel% neq 0 exit /b %errorlevel%

@REM install pre-commit hooks when not in CI
if "%CI%"=="" (
    pre-commit install
    if %errorlevel% neq 0 exit /b %errorlevel%
)

@REM install packages from lock file in local virtual environment
echo installing package
pipenv install --dev
if %errorlevel% neq 0 exit /b %errorlevel%

xcopy /s /e /y /i translations .venv\var\instance\translations
if %errorlevel% neq 0 exit /b %errorlevel%

pipenv run python ./site/mex_invenio/scripts/merge_translations.py .venv\var\instance
if %errorlevel% neq 0 exit /b %errorlevel%

cd site\mex_invenio
set INVENIO_INSTANCE_PATH=..\..\.venv\var\instance
npm install
if %errorlevel% neq 0 exit /b %errorlevel%
npm run convert-po
if %errorlevel% neq 0 exit /b %errorlevel%
set INVENIO_INSTANCE_PATH=
cd ..\..

pipenv run pybabel compile --directory=.venv\var\instance\translations --domain=ui
if %errorlevel% neq 0 exit /b %errorlevel%

xcopy /s /e /y /i static .venv\var\instance\static
if %errorlevel% neq 0 exit /b %errorlevel%

xcopy /s /e /y /i assets .venv\var\instance\assets
if %errorlevel% neq 0 exit /b %errorlevel%

pipenv run invenio collect
if %errorlevel% neq 0 exit /b %errorlevel%

pipenv run invenio webpack buildall
exit /b %errorlevel%


:lint
@REM run the linter hooks from pre-commit on all files
echo linting all files
pre-commit run --all-files
exit /b %errorlevel%
