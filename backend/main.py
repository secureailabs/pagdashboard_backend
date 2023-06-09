from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware; 
import pandas as pd
from typing import Dict
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/fetch_and_clean_data/")
async def fetch_and_clean_data():
    global data_frame
    data_frame = pd.read_csv('data_demo_2.csv', index_col=0)
    data_frame["Date of birth"] = pd.to_datetime(data_frame["Date of birth"], format='%Y-%m-%d')
    data_frame["Date of diagnosis"] = pd.to_datetime(data_frame["Date of diagnosis"], format='%Y-%m-%d')
    data_frame["Date of death"] = pd.to_datetime(data_frame["Date of death"], format='%Y-%m-%d')
    data_frame["Age at diagnosis in years"] = (data_frame["Date of diagnosis"] - data_frame[
        "Date of birth"]) / np.timedelta64(1, 'Y')
    data_frame["Age at death in years"] = (data_frame["Date of death"] - data_frame["Date of birth"]) / np.timedelta64(
        1, 'Y')
    data_frame["Survival time in years"] = (data_frame["Date of death"] - data_frame[
        "Date of diagnosis"]) / np.timedelta64(1, 'Y')
    data_frame["Age at diagnosis in years"] = data_frame["Age at diagnosis in years"].round(2)
    data_frame["Age at death in years"] = data_frame["Age at death in years"].round(2)
    data_frame["Survival time in years"] = data_frame["Survival time in years"].round(2)
    return data_frame

@app.get("/stats")
async def get_stats() -> Dict[str, int]:
    stats = {
        "Patients": 15000,
        "Hospitals": 8,
        "Researchers": 20,
        "Queries": 1537,
        "Compute (hrs)": 60
    }
    return stats

@app.get("/graphs")
async def get_graph_data():
    data_frame = await fetch_and_clean_data()

    categorical_attributes = ["Sex", "Rurality", "Race", 'Socioeconomic', 'Ethnicity']
    continuous_attributes = ["Age at diagnosis in years", "Age at death in years", "Survival time in years"]
    
    pie_charts = {}
    bar_charts = {}

    # # For debugging
    # print(f"Dataframe Columns: {data_frame.columns}")
    # print(f"Categorical Attributes: {categorical_attributes}")
    # print(f"Continuous Attributes: {continuous_attributes}")

    for column in categorical_attributes:
            if column in data_frame.columns:
                pie_charts[column] = dict(data_frame[column].value_counts())

    # All data returned from the endpoint is JSON serializable --> frontend receive this data as a JSON object
    for column, counts in pie_charts.items():
        pie_charts[column] = {key: int(value) for key, value in counts.items()}

    for column in continuous_attributes:
            if column in data_frame.columns:
                bar_charts[column] = dict(data_frame[column].value_counts())
    
    for column, counts in bar_charts.items():
        bar_charts[column] = {key: int(value) for key, value in counts.items()}
        
    return {"pie_charts": pie_charts, "bar_charts": bar_charts}