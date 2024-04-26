#!/bin/bash

echo ""
sudo docker compose down
echo ""
sudo service docker start
echo ""
sudo docker compose up --detach --build
echo ""
sleep 10
curl http://127.0.0.1:8000/
sleep 15
echo ""
echo ""
sudo docker compose logs notifications
echo "Check the logs above to see if the notifications service is running,"
echo "if not, chech again in 10 seconds with:"
echo "$ sudo docker compose logs notifications"