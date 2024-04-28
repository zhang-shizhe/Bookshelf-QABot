# Bookshelf-QABot


## test api

To test your FastAPI application, you can use a variety of tools and methods. Here are the basic steps and an example using curl from the command line and Python's requests library. You will also need to run your FastAPI server locally.

1. Run Your FastAPI Server
Before you can test your API, you need to ensure your server is running. You typically run your FastAPI application with a command like:

```bash
uvicorn main:app --reload
```
Here, main should be replaced with the name of your Python script that contains your FastAPI application (e.g., app.py) and app is the name of the FastAPI instance.

2. Testing with curl
You can use the curl command in your terminal to send a request to your API:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "prompt": "What is the capital of France?",
  "model": "gpt-3.5-turbo",
  "temperature": 0.1,
  "include_history": false,
  "api_key": "your_api_key_here"
}'
```
Replace "your_api_key_here" with your actual API key if needed.

3. Testing with Python requests
Alternatively, you can use Python's requests library to test your API. Here’s how you might write a script to do this:

```python
import requests

url = 'http://127.0.0.1:8000/'
data = {
    "prompt": "What is the capital of France?",
    "model": "gpt-3.5-turbo",
    "temperature": 0.1,
    "include_history": False,
    "api_key": "your_api_key_here"
}

response = requests.post(url, json=data)
print(response.text)
```
Again, substitute "your_api_key_here" with your actual API key.