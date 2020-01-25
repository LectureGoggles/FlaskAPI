# FlaskAPI

## How to run
```bash
# Using pipenv
pipenv install
pipenv run flask run
# Using venv
pipenv lock -r >> requirements.txt
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
flask run
--OR--
gunicorn --bind=0.0.0.0 --timeout 600 app:create_app
```
