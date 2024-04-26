#!/bin/bash

sudo docker compose logs fastapi
echo "Check the logs above to see if the fastapi service is running."
echo ""
sleep 5

sudo docker compose logs notifications
echo "Check the logs above to see if the notifications service is running."
echo ""
sleep 5

curl http://127.0.0.1:8000/
echo ""
echo "Check the logs above to see if the API is Active."
echo ""
sleep 5

curl http://127.0.0.1:8000/v1/preferences/1
echo ""
echo "Check the logs above to see if the API is returning Error because no preference was created yet."
echo ""
sleep 5

curl -X 'POST' 'http://127.0.0.1:8000/v1/preferences/1?email_enabled=true&sms_enabled=true' -H 'accept: application/json' -d ''
echo ""
echo "Check the logs above to see if the API is returning the preferences, this means it was created successfuly."
echo ""
sleep 5

curl http://127.0.0.1:8000/v1/preferences/1
echo ""
echo "Check the logs above to see if the API is returning the preferences."
echo ""
sleep 5

curl http://127.0.0.1:8000/v1/properties/news
echo ""
echo "Check the logs above to see if the mocked API is returning the news."
echo ""
sleep 5

curl -X 'POST' 'http://127.0.0.1:8000/v1/notifications' -H 'accept: application/json' -d ''
echo ""
echo "Check the logs above to see if the API created notifications."
echo ""
sleep 5

sudo docker compose logs notifications
echo "Check the logs above to see if the notifications service is receiving the news."
echo ""
sleep 5

echo "All tests finished! 🥳"
echo ""