Setting Up the Local Environment
================================

This guide walks you through setting up the local development environment for Open Beheer, which consists of a Django backend and a React (Vite) frontend.

Prerequisites
-------------

Make sure the following tools are installed:

* `Python`_ – check the ``Dockerfile`` for the required version.
* `uv`_.
* Python `Virtualenv`_ and `Pip`_
* `PostgreSQL`_
* `Node.js`_
* `npm`_ – check the ``frontend/.nvmrc`` file for the required version.
* `Redis`_

.. _Python: https://www.python.org/
.. _Virtualenv: https://virtualenv.pypa.io/en/stable/
.. _Pip: https://packaging.python.org/en/latest/tutorials/installing-packages/#ensure-pip-setuptools-and-wheel-are-up-to-date
.. _PostgreSQL: https://www.postgresql.org/
.. _Node.js: https://nodejs.org/
.. _npm: https://www.npmjs.com/
.. _Redis: https://redis.io/
.. _uv: https://docs.astral.sh/uv/


Database Setup (PostgreSQL)
---------------------------

Create the `openbeheer` role and database:

.. code-block:: bash

   sudo -u postgres psql

Inside the PostgreSQL shell (``openbeheer`` is the user/password/database name used by default by the development server):

.. code:: sql

   CREATE ROLE openbeheer WITH LOGIN PASSWORD 'openbeheer';
   ALTER ROLE openbeheer CREATEDB;
   CREATE DATABASE openbeheer OWNER openbeheer;

You can adjust the password or database name as needed, but make sure it matches your backend's ``.env``.

Clone the Repository
--------------------

Start by cloning the repository:

.. code-block:: bash

   git clone git@bitbucket.org:maykinmedia/openbeheer.git
   cd openbeheer

Backend Setup (Django)
----------------------

1. **Navigate to the backend directory**:

   .. code-block:: bash

      cd backend

2. **Create and activate a virtual environment**:

   .. code-block:: bash

      python -m venv env
      source env/bin/activate

3. **Install Python dependencies**:

   .. code-block:: bash

      uv pip install -r requirements/dev.txt

4. **Create a `.env` file** and configure environment variables. See :doc:`environment-variables` for details.

   You can use the provided example as a starting point:

   .. code-block:: bash

      cp dotenv.dev.example .env

5. **Apply migrations**:

   .. code-block:: bash

      src/manage.py migrate

6. **Create a superuser** (optional, but recommended):

   .. code-block:: bash

      src/manage.py createsuperuser

8. **Run the development server**:

   .. code-block:: bash

      src/manage.py runserver

.. _example_auto_config: 

Automatic configuration
-----------------------

For development, you can configure the backend to use the external applications provided as 
docker compose by using the following setup-configuration file:

.. literalinclude:: ../../backend/src/openbeheer/config/setup_configuration/fixtures/data.yaml

This can be loaded by doing (from the backend folder):

.. code:: bash

   src/manage.py setup_configuration --yaml-file src/openbeheer/config/setup_configuration/fixtures/data.yaml

Frontend Setup (React)
----------------------

1. **Navigate to the frontend directory**:

   .. code-block:: bash

      cd ../frontend

2. **Install frontend dependencies**:

   .. code-block:: bash

      npm install

3. **Create a `.env` file** and configure environment variables. See :doc:`environment-variables` for details.

   You can use the provided example as a starting point:

   .. code-block:: bash

      cp .env.example .env

4. **Start the frontend development server**:

   .. code-block:: bash

      npm run dev

This will usually be available at ``http://localhost:5173/``. The Django backend runs at ``http://localhost:8000/`` by default.

Next Steps
----------

- Refer to :doc:`environment-variables` for a complete breakdown of required configuration.

Running end-to-end tests
========================

The E2E tests use pytest instead of the Django test framework (based on unittest). They make use of the libraries
``pytest-django`` and ``pytest-playwright``.

We currently use the ``sync`` interface of Playwright, which is a wrapper around the ``async`` API that abstracts
``asyncio`` usage. Since under the hood Playwright remains asynchronous, it needs to be run with the environment variable 
``DJANGO_ALLOW_ASYNC_UNSAFE=yes`` (see `this issue`_ for more details).

.. _this issue: https://github.com/microsoft/playwright-pytest/issues/29

To run the tests locally, you first need to build the frontend. This can be done 
with the script ``backend/bin/setup_e2e.sh``. This will build the frontend with the environment
variable ``MYKN_API_URL=""`` and then symlink the ``index.html`` and the javascript/css assets into the templates
and the static folders of the backend respectively. You can skip the building step with the environment variable ``SKIP_BUILD=yes``.

Then, set the environment variable ``E2E_TESTS=yes``. This will tell the backend to use the ``index.html`` as 
the template on the root page instead of the ``master.html``.

Finally, run the e2e tests from the ``backend/`` folder with (possible browsers are ``firefox|chromium|webkit``):

.. code:: bash

   pytest -k e2e --headed --browser=firefox src/

TL;DR
-----

#. From ``backend/``, run ``./bin/setup_e2e.sh``.
#. Set environment variables ``E2E_TESTS=yes`` and ``DJANGO_ALLOW_ASYNC_UNSAFE=yes``.
#. Run tests from ``backend/`` with ``pytest -k e2e --headed --browser=firefox src/``.

Adding tests
------------

Make sure that the tests are decorated with ``@pytest.mark.e2e``:

.. code:: python

   import pytest

   @pytest.mark.e2e
   def test_some_feature(page, runner):
      ...


This marker is used to discover all the E2E tests.