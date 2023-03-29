# SIPETA Backend

API for Sistem Informasi Pengelolaan Tugas Akhir

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

### Setting Up Your Users

-   To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

-   To create a **superuser account**, use this command:

        $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    $ mypy sipeta_backend

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

## Development Guide

1. Make sure Python 3 is already installed and accessible through `python` or `python3`, you can make sure using this command
```sh
which python3 # for UNIX based
where python3 # for Windows
```

2. Clone this repository in your local computer

3. Install pre-commit
```sh
pre-commit install
```

4. Create a virtual environment using `venv`, for example
```sh
python3 -m venv venv
source venv/bin/activate # your virtual env is active now
```

5. Install the needed requirements to your virtual environment
```sh
pip3 install -r requirements/local.txt
```

6. Create a file named `.env` and copy the content from `.env.template`
```sh
cat .env.template > .env
```

7. Open the `.env` file and edit these values
```
DJANGO_SECRET_KEY # can be generated from https://djecrety.ir
DATABASE_NAME
DATABASE_URL
```

8. Start a postgresql server locally according to how you set above variables (username, password, etc.)

9. Run the database migrations
```sh
python3 manage.py makemigrations
python3 manage.py migrate
```

10. Create cache table
```sh
python3 manage.py createcachetable
```

11. Run the application (Done!)
```sh
python3 manage.py runserver
```

## Deployment

The following details how to deploy this application.
