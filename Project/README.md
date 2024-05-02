# Pattern recognition WEB and API

This is a full-stack project for the subject of pattern recognition. The project is split into 3 parts:
- **backend** - API and DB for feature set creation/deletion and execution of exploratory data analysis using PCA and hierarchical clustering
- **frontend** - Interface for hosting a SPA and a wrapper for various web requests done from the frontend 
- **nginx** - Reverse proxy and load balancer for the backend and frontend and serving static files (CSS/JS)

For each part, there is a separate README file with more detailed information in the respective folder.


## Running the code

You can run the project by running the following command in the root of the project:
```
docker compose build
docker compose up -d
```
To stop the project, run the following command in the root of the project:
```
docker compose down
```

The dashboard can be accessed on the following URL: [http://localhost:5000/recognition-web/v1/dashboard](http://localhost:5000/recognition-web/v1/dashboard)


## Basic project architecture

The project uses a microservices architecture with docker compose to run the services. It creates **4 containers** that are interconnected with **2 networks**. The containers are:
- **db** - Postgres database for storing the feature sets (Network: __db-api__)
- **recognition-api** - API for creating/deleting feature sets and running exploratory data analysis (Network: __db-api__, __api-nginx__)
- **recognition-web** - SPA for the dashboard and a wrapper for the API requests (Network: __web-nginx__)
- **recognition-nginx** - Reverse proxy and load balancer for the backend and frontend and serving static files (CSS/JS) (Network: __web-nginx__, __api-nginx__)

## Dependencies used

Bellow is a list of dependencies used in the project by each part of the project:
- **Backend** (API and DB)
    - API (Docker image: python:3.11-alpine)
        - __Python__ (Version: >=3.9, <3.12)
        - __asyncio__ (Version: ^3.4.3)
        - __aiohttp__ (Version: ^3.8.1)
        - __asyncpg__ (Version: ^0.26.0)
        - __aiohttp-sqlalchemy__ (Version: ^0.34.0)
        - __SQLAlchemy__ (Version: ^1.4.39)
        - __numpy__ (Version: ^1.17.3)
        - __scikit-learn__ (Version: ^1.2.0)
        - __pytest__ (Version: ^6.2.5)
        - __pytest-asyncio__ (Version: ^0.16.0)
        - __testcontainers__ (Version: ^3.0.0)
    - DB (Docker image: postgres:15.1)
        - __Postgres__ (Version: 15.1)

- **Frontend** (Docker image: python:3.11-alpine)
    - __Python__ (Version: >=3.9, <3.12)
    - __asyncio__ (Version: ^3.4.3)
    - __aiohttp__ (Version: ^3.8.1)

- **Nginx**
    - __Nginx__ (Version: 1.23)

## References

[1] Markelle Kelly, Rachel Longjohn, Kolby Nottingham, The UCI Machine Learning Repository, https://archive.ics.uci.edu