# wd_notification

Microservice to send email or sms notifications according with user preferences

## tl;dr
```shell
git clone https://github.com/leocjj/wd_notification.git
cd wd_notification
chmod +x tests.sh start.sh install_docker.sh
./install_docker.sh
./start.sh
./tests.sh
```

## Install with Docker Compose

Follow the steps below to install Docker and Docker Compose ([Official page](https://docs.docker.com/engine/install/ubuntu/)):
```shell
# Update the apt package index and install packages to allow apt to use a repository over HTTPS:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install the Docker packages.
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# In UBUNTU
sudo update-alternatives --config iptables
# And select the option /usr/sbin/iptables-legacy

# Start docker service and check the status
sudo service docker start
sudo service docker status
# sudo docker run -it hello-world bash

# Check if docker compose is installed
docker compose version
# If not installed do the following
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Check the docker compose version
docker compose version

# Build the compose.yaml file and run the docker compose in the background
sudo docker compose up --detach --build
sudo docker compose config

# To stop the running process
sudo docker compose down
```

### Python/FastAPI application

Project structure:
```
├── compose.yaml
├── Dockerfile
├── requirements.txt
├── app
    ├── main.py
    ├── db_orm.py
    ├── __init__.py

```

.env file

Database credentials are passed as environment variables to the compose file. This is the recommended way to pass sensitive information like credentials to the application and should
be created in the same directory as the compose file with the right permissions.
```shell
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
```

[_compose.yaml_](compose.yaml)


```yaml
services:
  fastapi:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - rabbitmq
    image: notifications_fastapi
    restart: on-failure
    volumes:
      - ./app:/code/app
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  notifications:
    image: notifications_fastapi
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    restart: on-failure
    volumes:
      - ./app/notifications.py:/code/app/notifications.py
    working_dir: /code
    command: python ./app/notifications.py

  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"

  rabbitmq:
    image: rabbitmq:3-management
    hostname: rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
```

## Deploy with docker compose

```shell
# To start the docker service
sudo service docker start
# To Build the compose.yaml file and run the docker compose in the background
sudo docker compose up --detach --build
# To check the running processes
docker compose ps
# To check the logs of the running process
sudo docker compose logs fastapi
# To connect to the running container
sudo docker compose exec fastapi bash
# To stop the running process
sudo docker compose down

# Or just run this bash script
chmod +x start.sh
./start.sh
```

## Expected result
Listing containers must show these containers running and the ports mapping as below:
```
$ docker ps

CONTAINER ID   IMAGE                   COMMAND                  CREATED         STATUS         PORTS
                                                         NAMES
8288bae18df0   notifications_fastapi   "python ./app/notifi…"   7 minutes ago   Up 6 minutes
                                                         wd_notification-notifications-1
112cef26cbc3   notifications_fastapi   "uvicorn app.main:ap…"   7 minutes ago   Up 7 minutes   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp
                                                         wd_notification-fastapi-1
73cec5e6b2b4   rabbitmq:3-management   "docker-entrypoint.s…"   7 minutes ago   Up 7 minutes   4369/tcp, 5671/tcp, 0.0.0.0:5672->5672/tcp, :::5672->5672/tcp, 15671/tcp, 15691-15692/tcp, 25672/tcp, 0.0.0.0:15672->15672/tcp, :::15672->15672/tcp   wd_notification-rabbitmq-1
9c0f20c9fd04   postgres:13             "docker-entrypoint.s…"   7 minutes ago   Up 7 minutes   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp
                                                         wd_notification-postgres-1
```


# TESTS

After the application starts, navigate to each endpoint and you should see the following json responses:
```bash
$ sudo docker compose logs fastapi
fastapi-1  | INFO:     Will watch for changes in these directories: ['/code']
fastapi-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
fastapi-1  | INFO:     Started reloader process [1] using StatReload
fastapi-1  | INFO:     Started server process [8]
fastapi-1  | INFO:     Waiting for application startup.
fastapi-1  | INFO:     Application startup complete.
fastapi-1  | INFO:     172.31.0.1:59390 - "GET / HTTP/1.1" 200 OK

$ sudo docker compose logs notifications
notifications-1  | Rabbitmq not ready. Need to restar this container...
notifications-1  | Rabbitmq not ready. Need to restar this container...
notifications-1  | [*] Waiting for notifications...

$ curl http://127.0.0.1:8000/
  {"Notification API status":"(0) Active"}

$ curl http://127.0.0.1:8000/v1/preferences/1
  {"Error":"user id does not exist, create it with a POST."}

$ curl -X 'POST' 'http://127.0.0.1:8000/v1/preferences/1?email_enabled=true&sms_enabled=true' -H 'accept: application/json' -d ''
  {"user_id":1,"email_enabled":true,"sms_enabled":true}

$ curl http://127.0.0.1:8000/v1/preferences/1
  {"user_id":1,"email_enabled":true,"sms_enabled":true}

$ curl -X 'POST' 'http://127.0.0.1:8000/v1/notifications' -H 'accept: application/json' -d ''
  {"result":"Notification created!"}

$ sudo docker compose logs notifications
  notifications-1  | Rabbitmq not ready. Need to restar this container...
  notifications-1  | Rabbitmq not ready. Need to restar this container...
  notifications-1  | [*] Waiting for notifications...
  notifications-1  | [√] Email jhon@gmail.com
  notifications-1  |     content:
  notifications-1  | Property code: 1
  notifications-1  | house
  notifications-1  | 100000
  notifications-1  |
  notifications-1  |
  notifications-1  | Property code: 2
  notifications-1  | apartment
  notifications-1  | 50000
  notifications-1  |
  notifications-1  |
  notifications-1  | Property code: 3
  notifications-1  | office
  notifications-1  | 200000
  notifications-1  |
  notifications-1  |
  notifications-1  | [√] SMS 555-123-4567
  notifications-1  |     content:
  notifications-1  | Property code: 1
  notifications-1  | house
  notifications-1  | 100000
  notifications-1  |
  notifications-1  |
  notifications-1  | Property code: 2
  notifications-1  | apartment
  notifications-1  | 50000
  notifications-1  |
  notifications-1  |
  notifications-1  | Property code: 3
  notifications-1  | office
  notifications-1  | 200000
  notifications-1  |

# Or just run this bash script
chmod +x tests.sh
./tests.sh
```

## RabbitMQ

To access the RabbitMQ management interface, navigate to `http://localhost:15672/` in your web browser. The default username and password are `guest` and `guest`, respectively.

## License
[Gnu Public License](https://www.gnu.org/licenses/gpl-3.0.html)

## Tech Stack
[FastAPI](https://fastapi.tiangolo.com/)

[PostgreSQL](https://www.postgresql.org/)

[RabbitMQ](https://www.rabbitmq.com/)

[Docker](https://www.docker.com/)

## Contact
Created by [LeonardoCJ](https://www.linkedin.com/in/leonardocj/) - feel free to contact me!

GitHub: [leocjj](github.com/leocjj)
