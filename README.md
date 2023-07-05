# Async API for movies Service

## Core Stack

- FastAPI
- PostgreSQL
- Elasticsearch
- Redis
- Pytest & aiohttp

## About

The project follows a microservice architecture. This particular service *(Movies Service)* is responsible for implementing API endpoints to access data from the data warehouse. It utilizes Elasticsearch as the data source and Redis as a caching.

The ETL **data warehouse service** is a separate service. It is responsible for continuously extracting, transforming and loading data from `PostgreSQL` into the `Elasticsearch` DB.

**Auth Service** is an implicit dependency for this service, as some API endpoints may require authentication. The authentication is based on `JWT` tokens. Instead of constantly querying the authentication service for each user access attempt, the service validates the provided `JWT` token using a shared secret with the authentication service. This approach allows the service to authenticate users without needing to interact with the authentication service every time.

**Services interaction scheme:**

![services-integration_schema.svg](resources/services-integration.svg)

## Requirements

1. [**ETL & data warehouse service**](https://github.com/vogelfenx/etl_postgres_to_elasticsearch)

1. [**Auth Service**](https://github.com/vogelfenx/auth-service-api)

## Installation & Launching

0. Before running this service, start the dependent services specified in the [requirements](#Requirements).

1. Configure & activate virtual environment using provided `requirements.txt` or `Pipfile`.

1. Configure environment in `./fastapi-solutions/.env`

   - Use `.env.sample` to set expected environment in `.env`

1. Use `docker-compose` to launch project:

   ```bash
   docker-compose up
   ```

1. The service is available on `localhost: 80`.

## Tests

Tests are written using `pytest` and `aiohttp` libraries.

### Configuration:

1. Configure & activate virtual environment using provided `requirements.txt`.

   ```sh
   pip install -r ./fastapi-solution/tests/functional/requirements.txt
   ```

1. Setup environment in the file `fastapi-solution/tests/.env`

   - Use `fastapi-solution/tests/.env.sample` to set expected environment in `.env`

### Tests launch:

1. Build & Run Test docker-compose `docker-compose.test.yaml`

   ```sh
   docker-compose -f docker-compose.test.yaml up --build
   ```

2. Run tests:

   ```sh
   pytest fastapi-solution/tests --docker-compose=docker-compose.test.yaml --docker-compose-no-build --use-running-containers -v
   ```

## Debugging

### Project debugging
1. Configure launcher `.vscode\launch.json`

   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: Remote Attach",
         "type": "python",
         "request": "attach",
         "port": 5678,
         "host": "localhost",
         "pathMappings": [
           {
             "localRoot": "${workspaceFolder}/fastapi-solution",
             "remoteRoot": "/opt/app"
           }
         ]
       }
     ]
   }
   ```

1. Launch debugging docker-compose `docker-compose.debug.yaml`

   ```sh
   docker-compose -f docker-compose.debug.yaml up --build
   ```

1. Launch the before configured launcher (remote attach)
1. The service is available on `localhost:8000`

### Tests debugging

1. Setup configuration in VsCode Settings:

   ```json
   {
     "python.testing.pytestArgs": [
       "--rootdir",
       "fastapi-solution/tests",
       "--docker-compose=docker-compose.test.yaml",
       "--docker-compose-no-build",
       "--use-running-containers",
       "-v"
     ],
     "python.analysis.extraPaths": ["fastapi-solution/src/"],
     "python.testing.unittestEnabled": false,
     "python.testing.pytestEnabled": true,
   }
   ```
