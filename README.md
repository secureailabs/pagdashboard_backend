# pagdashboard_backend

## Instructions
Clone the repository in your local terminal 
    
    $ git clone git@github.com:secureailabs/pagdashboard_backend.git

## Install dependencies 
    pip install -r requirements.txt

## TO RUN THE DEV SERVER LOCALLY
1. Create a python virtual environment
    
    
    virtualenv env 
    
2. Activate the python virtual environment
    

    cd backend
    
    source env/bin/activate

3. In your local terminal of the "backend" directory, run:
    

    uvicorn main:app --reload


4. In a separate terminal of the "backend" directory, run: 
    
    streamlit run app.py