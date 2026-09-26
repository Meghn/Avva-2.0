# imports the class that represents your whole web application
from fastapi import FastAPI

# creates the application instance. 
# Uvicorn will point at this `app` object to run the server.
app = FastAPI()

# a decorator that registers the function below it to handle 
# GET requests to the path "/health"
# This is how FastAPI maps URLs to code
@app.get("/health")
# FastAPI automatically converts the returned Python dict 
# into a JSON response ({"status": "ok"}) with a 200 OK status.
def health():
    return {"status": "ok"}

