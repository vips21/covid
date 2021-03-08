# covid App

#### Pre-requisites
    Python 3.7
    Any Email service account like Mailgun, Sendgrid

#### Installation 
    Create environment with Python 3.7
    python3.7 -m virtualenv MyEnv
    source MyEnv/bin/activate
    cd covid_stats
    pip install -r requirements.txt

#### configuration for 3rd party services
    All the services will be installed from requirements.txt

#### create superuser
    python manage.py createsuperuser

#### To view admin
    go to localhost:8000/admin

#### For API swagger
    go to localhost:8000/api/doc/
    