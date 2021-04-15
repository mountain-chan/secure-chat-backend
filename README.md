# secure-chat-backend
API for secure chat application with RSA

# Manually 
## Installation

- Database: MySQL 8.0.23 [https://dev.mysql.com/downloads/installer/](https://dev.mysql.com/downloads/installer/)
- Python 3.7: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)

## Initial database
```
python migrate/init_db.py
```

## Run code
```
python main.py
```


# Docker 
## Installation

- Get Docker: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
- Install docker for Ubuntu 18.04: [https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)
- Install docker compose for Linux: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

## Starting
```
cd secure-chat-backend
```
```
docker-compose up --build -d
```
