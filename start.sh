#!/bin/bash

sudo docker compose down
sudo service docker start
sudo docker compose up --detach --build
sleep 10
curl http://127.0.0.1:8000/
sleep 15
echo "\n"
sudo docker compose logs notifications
echo "Check the logs above to see if the notifications service is running,"
echo "if not, chech again in 10 seconds with:"
echo "sudo docker compose logs notifications"