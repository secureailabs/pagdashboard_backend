# pagdashboard_backend

## Instructions
Clone the repository in your local terminal 
    
    $ git clone git@github.com:secureailabs/pagdashboard_backend.git

## Install dependencies 
    $ pip install -r requirements.txt

## TO RUN THE DEV SERVER LOCALLY
Create a python virtual environment
    
    $ cd backend

    $ virtualenv env 
    
Activate the python virtual environment
    
    $ source env/bin/activate

In your local terminal of the "backend" directory, run:

    $ uvicorn main:app --reload


In a separate terminal of the "backend" directory, run: 
    
    $ streamlit run app.py