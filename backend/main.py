from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Dict, List, Any
import json

# Import functions from utils.py
from utils import preprocess_data, get_attributes_by_type, count_values, generate_pie_charts, generate_histograms, validate_inputs, generate_comparison_pie_charts, generate_comparison_histograms

app = FastAPI()

# Configure CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def load_data():
    global data_frame, data_model
    try:
        # Load the data from a CSV file
        data_frame = pd.read_csv('data_demo_2.csv', index_col=0)
        
        # Read the data model configuration from the JSON file
        with open('data_model.json') as f:
            data_model = json.load(f)
        
        # Preprocess the data
        preprocess_data(data_frame)
    except FileNotFoundError:
        raise Exception("Data file not found")
    except pd.errors.ParserError:
        raise Exception("Error parsing the data file")

# Return the cleaned dataframe
@app.get("/fetch_and_clean_data/")
async def fetch_and_clean_data() -> Any:
    return data_frame

# Return a dictionary of statistics
@app.get("/stats")
async def get_stats() -> Dict[str, int]:
    patient_count = count_values(data_frame)[0]
    hospital_count = count_values(data_frame)[1]

    # Change this part later (Researchers, Queries, Compute)
    return {"Patients": patient_count, "Hospitals": hospital_count, "Researchers": 20, "Queries": 1537, "Compute (hrs)": 60}

# Generate pie charts and histograms from the data
@app.get("/graphs")
async def get_graph_data() -> Dict[str, Any]:
    # Define the categories of attributes
    categorical_attributes, continuous_attributes = get_attributes_by_type(data_frame)

    pie_charts, histograms = {}, {}
    pie_charts.update(generate_pie_charts(data_frame, categorical_attributes))
    histograms.update(generate_histograms(data_frame, continuous_attributes))
    
    return {"pie_charts": pie_charts, "histograms": histograms}

# Generate comparison visualizations for the chosen hospitals and attributes
@app.get("/compare/")
async def compare_metrics(chosen_hospitals: List[str], attributes_to_be_compared: List[str]) -> Dict[str, Any]:
    validate_inputs(data_frame, chosen_hospitals, attributes_to_be_compared)

    categorical_attributes, continuous_attributes = get_attributes_by_type(data_frame)

    pie_charts, histograms = {}, {}
    pie_charts.update(generate_comparison_pie_charts(data_frame, chosen_hospitals, attributes_to_be_compared, categorical_attributes))
    histograms.update(generate_comparison_histograms(data_frame, chosen_hospitals, attributes_to_be_compared, continuous_attributes))

    return {"pie_charts": pie_charts, "histograms": histograms}