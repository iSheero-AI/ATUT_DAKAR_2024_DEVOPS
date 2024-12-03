Chat BJ is a conversational agent designed to facilitate access to public and private e-services by providing factual and concise information on the steps to follow when requesting a service online.

A- To launch the application, follow these steps:
### 1- Create a pyth runtime environment
python -m venv <envname>. - Connect to the env <envname>\Scripts\activate.bat

### 2- Install the dependencies in the requirements.txt file 
pip install -r requirements.txt

### 3- Add the env file to the root directory

### 4- launch the application 
uvicorn main:app --port <port> --reload

### 5- Access to api documentation 
http://localhost:<port>/docs