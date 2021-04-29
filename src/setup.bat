@ECHO OFF
ECHO Setting up virtual environment...
py -m venv venv
ECHO Installing requirements...
CALL venv\Scripts\activate
pip install -r requirements.txt
ECHO Setup complete, running app...
CALL run