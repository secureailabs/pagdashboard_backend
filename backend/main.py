from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Read the data model configuration from the JSON file
with open('data_model.json') as f:
    data_model = json.load(f)

@app.on_event("startup")
async def load_data():
    global data_frame
    try:
        # Load the data from a CSV file
        data_frame = pd.read_csv('data_demo_2.csv', index_col=0)
        preprocess_data()
    except FileNotFoundError:
        raise Exception("Data file not found")
    except pd.errors.ParserError:
        raise Exception("Error parsing the data file")

# Transform the raw data
def preprocess_data():
    date_columns, age_columns, date_pairs = get_column_names()

    # Convert dates to datetime format and calculate ages
    for column, (start_date, end_date) in zip(age_columns, date_pairs):
        data_frame[start_date] = pd.to_datetime(data_frame[start_date], format='%Y-%m-%d')
        data_frame[end_date] = pd.to_datetime(data_frame[end_date], format='%Y-%m-%d')
        data_frame[column] = ((data_frame[end_date] - data_frame[start_date]) / np.timedelta64(1, 'Y')).round(2)

# Return categorical and continuous attributes from the data model
def get_attributes_by_type():
    categorical_attributes = []
    for key, value in data_model.items():
        if value['__type__'] == 'SeriesDataModelCategorical':
            categorical_attributes.append(value['series_name'])
    continuous_attributes = ["Age at diagnosis in years", "Age at death in years", "Survival time in years"]
    return categorical_attributes, continuous_attributes

# Return column names used in data preprocessing
def get_column_names():
    date_columns = ["Date of birth", "Date of diagnosis", "Date of death"]
    age_columns = ["Age at diagnosis in years", "Age at death in years", "Survival time in years"]
    date_pairs = [("Date of birth", "Date of diagnosis"), ("Date of birth", "Date of death"), ("Date of diagnosis", "Date of death")]
    return date_columns, age_columns, date_pairs

# Return the cleaned dataframe
@app.get("/fetch_and_clean_data/")
async def fetch_and_clean_data() -> Any:
    return data_frame

# Return a hard-coded dictionary of statistics
@app.get("/stats")
async def get_stats() -> Dict[str, int]:
    return {"Patients": 15000, "Hospitals": 8, "Researchers": 20, "Queries": 1537, "Compute (hrs)": 60}

# Generate pie charts and histograms from the data
@app.get("/graphs")
async def get_graph_data() -> Dict[str, Any]:
    # Define the categories of attributes
    categorical_attributes, continuous_attributes = get_attributes_by_type()

    pie_charts, histograms = {}, {}
    pie_charts.update(generate_pie_charts(categorical_attributes))
    histograms.update(generate_histograms(continuous_attributes))
    
    return {"pie_charts": pie_charts, "histograms": histograms}

# Generate pie charts for each categorical attribute
def generate_pie_charts(categorical_attributes):
    pie_charts = {}
    for column in categorical_attributes:
        if column in data_frame.columns:
            val_counts = data_frame[column].value_counts()
            val_counts_df = pd.DataFrame({'attribute': val_counts.index, 'value': val_counts.values})

            pie_chart = px.pie(val_counts_df, values='value', names='attribute', title='').to_json()
            pie_charts[column] = json.loads(pie_chart)
    return pie_charts

# Generates histograms for each continuous attribute
def generate_histograms(continuous_attributes):
    histograms = {}
    for column in continuous_attributes:
        if column in data_frame.columns:
            hist = px.histogram(data_frame, x=column, nbins=50, title='', labels={'value': 'Count', column: column}).to_json()
            histograms[column] = json.loads(hist)
    return histograms

# Generate comparison visualizations for the chosen hospitals and attributes
@app.get("/compare/")
async def compare_metrics(chosen_hospitals: List[str], attributes_to_be_compared: List[str]) -> Dict[str, Any]:
    validate_inputs(chosen_hospitals, attributes_to_be_compared)

    categorical_attributes, continuous_attributes = get_attributes_by_type()

    pie_charts, histograms = {}, {}
    pie_charts.update(generate_comparison_pie_charts(chosen_hospitals, attributes_to_be_compared, categorical_attributes))
    histograms.update(generate_comparison_histograms(chosen_hospitals, attributes_to_be_compared, continuous_attributes))

    return {"pie_charts": pie_charts, "histograms": histograms}

# Validate the chosen hospitals and attributes for comparison
def validate_inputs(chosen_hospitals, attributes_to_be_compared):
    if len(chosen_hospitals) < 2 or len(chosen_hospitals) > 3:
        raise Exception("You need to select at least two and maximum three hospitals for comparison.")
    
    if len(attributes_to_be_compared) == 0:
        raise Exception("You need to select at least one attribute for comparison.")

    # Check if the chosen hospitals are available in the dataframe
    available_hospitals = data_frame['Hospital name'].unique().tolist()
    for hospital in chosen_hospitals:
        if hospital not in available_hospitals:
            raise Exception(f"The hospital '{hospital}' is not available.")

    # Check if the chosen attributes are available in the dataframe
    available_attributes = data_frame.columns.tolist()
    for attribute in attributes_to_be_compared:
        if attribute not in available_attributes:
            raise Exception(f"The attribute '{attribute}' is not available.")

# Generates pie charts for categorical attributes
def generate_comparison_pie_charts(chosen_hospitals, attributes_to_be_compared, categorical_attributes):
    pie_charts = {}
    for attribute in attributes_to_be_compared:
        if attribute in categorical_attributes:
            for hospital in chosen_hospitals:
                hospital_df = data_frame[data_frame['Hospital name'] == hospital]
                val_counts = hospital_df[attribute].value_counts()
                val_counts_df = pd.DataFrame({'attribute': val_counts.index, 'value': val_counts.values})
                pie_chart = px.pie(val_counts_df, values='value', names='attribute', title=f'{hospital} - {attribute}').to_json()
                pie_charts[f'{hospital}_{attribute}'] = json.loads(pie_chart)
    return pie_charts

# Generates histograms for continuous attributes
def generate_comparison_histograms(chosen_hospitals, attributes_to_be_compared, continuous_attributes):
    histograms = {}
    for attribute in attributes_to_be_compared:
        if attribute in continuous_attributes:
            data = []
            shared_bins = np.histogram_bin_edges(data_frame[data_frame['Hospital name'].isin(chosen_hospitals)][attribute], bins=50)
            for hospital in chosen_hospitals:
                hist, _ = np.histogram(data_frame[data_frame['Hospital name'] == hospital][attribute], bins=shared_bins)
                data.append(go.Histogram(x=shared_bins[:-1], y=hist, name=hospital, histnorm='percent', opacity=0.75))
            layout = go.Layout(title=f'{attribute} comparison', barmode='stack', bargap=0.1, xaxis=dict(title=attribute, range=[0, 'auto']), yaxis=dict(title='Population Count'))
            fig = go.Figure(data=data, layout=layout)
            histograms[f'{attribute}_comparison'] = json.loads(fig.to_json())
    return histograms