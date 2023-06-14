from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware; 
import pandas as pd
from typing import Dict, List, Any
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import json

app = FastAPI()

# Configure CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/fetch_and_clean_data/")
async def fetch_and_clean_data():
    try:
        # Load the data from a CSV file
        global data_frame
        data_frame = pd.read_csv('data_demo_2.csv', index_col=0)
        
         # Convert dates to datetime format
        data_frame["Date of birth"] = pd.to_datetime(data_frame["Date of birth"], format='%Y-%m-%d')
        data_frame["Date of diagnosis"] = pd.to_datetime(data_frame["Date of diagnosis"], format='%Y-%m-%d')
        data_frame["Date of death"] = pd.to_datetime(data_frame["Date of death"], format='%Y-%m-%d')

        # Calculate ages and survival time
        data_frame["Age at diagnosis in years"] = (data_frame["Date of diagnosis"] - data_frame[
            "Date of birth"]) / np.timedelta64(1, 'Y')
        data_frame["Age at death in years"] = (data_frame["Date of death"] - data_frame["Date of birth"]) / np.timedelta64(
            1, 'Y')
        data_frame["Survival time in years"] = (data_frame["Date of death"] - data_frame[
            "Date of diagnosis"]) / np.timedelta64(1, 'Y')
        
        # Round ages and survival time to 2 decimal places
        data_frame["Age at diagnosis in years"] = data_frame["Age at diagnosis in years"].round(2)
        data_frame["Age at death in years"] = data_frame["Age at death in years"].round(2)
        data_frame["Survival time in years"] = data_frame["Survival time in years"].round(2)
        return data_frame
    
    except FileNotFoundError:
        return {"error": "Data file not found."}
    except pd.errors.ParserError:
        return {"error": "Error parsing the data file."}


@app.get("/stats")
# Return a hard-coded dictionary of statistics
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
    # Fetch and clean the data
    data_frame = await fetch_and_clean_data()

    # Define the categories of attributes
    categorical_attributes = ["Sex", "Rurality", "Race", 'Socioeconomic', 'Ethnicity']
    continuous_attributes = ["Age at diagnosis in years", "Age at death in years", "Survival time in years"]
    
    # Initialize empty dictionaries to store pie charts and histograms
    pie_charts = {}
    histograms = {}
    
    # Generate pie charts for each categorical attribute
    for column in categorical_attributes:
        if column in data_frame.columns:
            val_counts = data_frame[column].value_counts()
            val_counts_df = pd.DataFrame({'attribute': val_counts.index, 'value': val_counts.values})

            # Convert pie chart object into a JSON format string
            pie_chart = px.pie(val_counts_df, values='value', names='attribute', title='').to_json()

            # Convert the JSON string into a Python object (dict)
            pie_charts[column] = json.loads(pie_chart)

    # Generate histograms for each continuous attribute
    for column in continuous_attributes:
        if column in data_frame.columns:
            hist = px.histogram(data_frame, x=column, nbins=50, title='', labels={'value': 'Count', column: column}).to_json()
            histograms[column] = json.loads(hist)

    return {"pie_charts": pie_charts, "histograms": histograms}

@app.get("/compare/")
async def compare_metrics(chosen_hospitals: List[str], attributes_to_be_compared: List[str]) -> Dict[str, Any]:
    try:
        # Ensure at least two and at most three hospitals are chosen for comparison
        if len(chosen_hospitals) < 2:
            return {"error": "You need to select at least two hospitals for comparison."}
        if len(chosen_hospitals) > 3:
            return {"error": "You can select a maximum of three hospitals for comparison."}
        
        # Ensure at least one attribute is chosen for comparison
        if len(attributes_to_be_compared) == 0:
            return {"error": "You need to select at least one attribute for comparison."}
        
        # Fetch and clean the data
        data_frame = await fetch_and_clean_data()

        # Check if the chosen hospitals are available in the dataframe
        available_hospitals = data_frame['Hospital name'].unique().tolist()
        for hospital in chosen_hospitals:
            if hospital not in available_hospitals:
                return {"error": f"The hospital '{hospital}' is not available."}

        # Check if the chosen attributes are available in the dataframe
        available_attributes = data_frame.columns.tolist()
        for attribute in attributes_to_be_compared:
            if attribute not in available_attributes:
                return {"error": f"The attribute '{attribute}' is not available."}

        # Define the categories of attributes
        categorical_attributes = ["Sex", "Rurality", "Race", 'Socioeconomic', 'Ethnicity']
        continuous_attributes = ["Age at diagnosis in years", "Age at death in years", "Survival time in years"]

        # Initialize empty dictionaries to store pie charts and histograms
        pie_charts = {}
        histograms = {}

        # Generate pie charts for categorical attributes and histograms for continuous attributes
        for attribute in attributes_to_be_compared:
            if attribute in categorical_attributes:
                for hospital in chosen_hospitals:
                    hospital_df = data_frame[data_frame['Hospital name'] == hospital]
                    val_counts = hospital_df[attribute].value_counts()
                    val_counts_df = pd.DataFrame({'attribute': val_counts.index, 'value': val_counts.values})
                    pie_chart = px.pie(val_counts_df, values='value', names='attribute', title=f'{hospital} - {attribute}').to_json()
                    pie_charts[f'{hospital}_{attribute}'] = json.loads(pie_chart)
            elif attribute in continuous_attributes:
                data = []
                shared_bins = np.histogram_bin_edges(data_frame[data_frame['Hospital name'].isin(chosen_hospitals)][attribute], bins=50)
                for hospital in chosen_hospitals:
                    hist, _ = np.histogram(data_frame[data_frame['Hospital name'] == hospital][attribute], bins=shared_bins)
                    
                    # Create a histogram for each hospital
                    data.append(go.Histogram(x=shared_bins[:-1], y=hist, name=hospital, histnorm='percent', opacity=0.75))
                layout = go.Layout(title=f'{attribute} comparison', barmode='stack', bargap=0.1, xaxis=dict(title=attribute, range=[0, 'auto']), yaxis=dict(title='Population Count'))
                fig = go.Figure(data=data, layout=layout)
                histograms[f'{attribute}_comparison'] = json.loads(fig.to_json())
        return {"pie_charts": pie_charts, "histograms": histograms}
    except Exception as e:
        return {"error": str(e)}