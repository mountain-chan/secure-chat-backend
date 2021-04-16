# Table of Contents
1. [API documents](#secure-chat-backend)
2. [Run App Manually](#Run App Manually)
3. [Run App With Docker](#Run App With Docker)

#secure-chat-backend
API documents: [https://documenter.getpostman.com/view/9825969/TzJpjL65](https://documenter.getpostman.com/view/9825969/TzJpjL65)

#Run App Manually 
##Installation

* Database: MySQL 8.0.23 [https://dev.mysql.com/downloads/installer/](https://dev.mysql.com/downloads/installer/)
* Python 3.7: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)

##Initial database
```
python migrate/init_db.py
```

##Stating
```
python main.py
```


#Run App With Docker 
##Installation

* Get Docker: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
* Install docker for Ubuntu 18.04: [https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)
* Install docker compose for Linux: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

##Starting
```
cd secure-chat-backend
```
```
docker-compose up --build -d
```

**If you have trouble querying group by then set mode for mysql server as follows:**
```
mysql> SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));
```
