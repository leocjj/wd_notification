# wd_notification

Microservice to send email or sms notifications according with user preferences

## Use with Docker Compose

Follw the steps below to install Docker and Docker Compose ([Official page](https://docs.docker.com/engine/install/ubuntu/)):
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

Database credentials are passed as environment variables to the compose file. This is the recommended way to pass sensitive information like credentials to the application.
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
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672

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
    ports:
      - "5672:5672"
      - "15672:15672"
```

## Deploy with docker compose

```shell
# To start the docker service
sudo service docker start
# To check the running processes
docker compose ps
# To Build the compose.yaml file and run the docker compose in the background
sudo docker compose up --detach --build
# To stop the running process
sudo docker compose down
# To check the logs of the running process
sudo docker compose logs -f
# To connect to the running container
sudo docker compose exec fastapi bash
```
## Expected result
Listing containers must show these containers running and the ports mapping as below:
```
$ docker ps

CONTAINER ID   IMAGE                     COMMAND                  CREATED          STATUS          PORTS
                                        NAMES
b208a284cffb   wd_notification-fastapi   "uvicorn app.main:ap…"   24 minutes ago   Up 24 minutes   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp
                                        wd_notification-fastapi-1
5a1f062ea92b   rabbitmq:3-management     "docker-entrypoint.s…"   24 minutes ago   Up 24 minutes   4369/tcp, 5671/tcp, 0.0.0.0:5672->5672/tcp, :::5672->5672/tcp, 15671/tcp, 15691-15692/tcp, 25672/tcp, 0.0.0.0:15672->15672/tcp, :::15672->15672/tcp   wd_notification-rabbitmq-1
2ed5b07ac3b4   postgres:13               "docker-entrypoint.s…"   24 minutes ago   Up 24 minutes   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp
                                        wd_notification-postgres-1
```

After the application starts, navigate to each endpoint and you should see the following json responses:
```
$ curl http://127.0.0.1:8000/
{"Notification API status": "Active"}

$ curl http://127.0.0.1:8000/v1/preferences/1
{"Error":"user id does not exist, create it with a POST."}

$ curl -X 'POST' 'http://127.0.0.1:8000/v1/preferences/1?email_enabled=true&sms_enabled=true' -H 'accept: application/json' -d ''
{"user_id":1,"email_enabled":true,"sms_enabled":true}

$ curl http://127.0.0.1:8000/v1/preferences/1
{"user_id":1,"email_enabled":false,"sms_enabled":true}

$ curl -X 'POST' 'http://127.0.0.1:8000/v1/notifications' -H 'accept: application/json' -d ''
{"message":"Notification created successfully!"}
```
