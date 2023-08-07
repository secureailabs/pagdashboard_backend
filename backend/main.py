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
async def get_stats() :
    patient_count = count_values(data_frame)[0]
    hospital_count = count_values(data_frame)[1]

    columnData_Dep = [
        { 'label': 'Patients', 'value': patient_count },
        { 'label': 'Hospitals', 'value': hospital_count },
        { 'label': 'Researchers', 'value': 20 },
        { 'label': 'Queries', 'value': 1537 },
        { 'label': 'Compute', 'value': 60 }
    ]
    # Change this part later (Researchers, Queries, Compute)
    return {"data": columnData_Dep }
    # {"Patients": patient_count, "Hospitals": hospital_count, "Researchers": 20, "Queries": 1537, "Compute (hrs)": 60}

# Generate pie charts and histograms from the data
@app.get("/graphs")
async def get_graph_data() -> Dict[str, Any]:
    # Define the categories of attributes
    categorical_attributes, continuous_attributes = get_attributes_by_type(data_frame)

    pie_charts, histograms = {}, {}
    pie_charts.update(generate_pie_charts(data_frame, categorical_attributes))
    histograms.update(generate_histograms(data_frame, continuous_attributes))

    keys = pie_charts.keys()
    pieChartData = []

    for key in keys:
      vals = []
      for i in range(len(pie_charts[key]['data'][0]['labels'])):
        vals.append({
          'label': pie_charts[key]['data'][0]['labels'][i],
          'value': pie_charts[key]['data'][0]['values'][i]
        })
      data = {
        'label' : key,
        'data' : vals
      }
      pieChartData.append(data)

    keys = [ 'Age at diagnosis in years', 'Age at death in years', 'Survival time in years' ]

    histogramData = [
      {
        'label': 'Age at diagnosis in years',
        'data': [
          { 'range': '20-30', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 20, 30) },
          { 'range': '30-40', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 30, 40) },
          { 'range': '40-50', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 40, 50) },
          { 'range': '50-60', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 50, 60) },
          { 'range': '60-70', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 60, 70) },
          { 'range': '70+', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 70, 150) }
        ]
      },
      {
        'label': 'Age at death in years',
        'data': [
          { 'range': '20-30', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 20, 30) },
          { 'range': '30-40', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 30, 40) },
          { 'range': '40-50', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 40, 50) },
          { 'range': '50-60', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 50, 60) },
          { 'range': '60-70', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 60, 70) },
          { 'range': '70+', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 70, 150) }
          ]
      },
      {
        'label': 'Survival time in years',
        'data': [
          { 'range': '0-1', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 0, 1) },
          { 'range': '1-2', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 1, 2) },
          { 'range': '2-3', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 2, 3) },
          { 'range': '3-4', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 3, 4) },
          { 'range': '4-5', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 4, 5) },
          { 'range': '5+', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 5, 150) }
        ]
      }
    ]
          
    return {"pie_charts": pieChartData, "histograms": histogramData}

# Generate comparison visualizations for the chosen hospitals and attributes
@app.get("/compare/")
async def compare_metrics(chosen_hospitals: List[str], attributes_to_be_compared: List[str]) -> Dict[str, Any]:
    validate_inputs(data_frame, chosen_hospitals, attributes_to_be_compared)

    categorical_attributes, continuous_attributes = get_attributes_by_type(data_frame)

    pie_charts, histograms = {}, {}
    pie_charts.update(generate_comparison_pie_charts(data_frame, chosen_hospitals, attributes_to_be_compared, categorical_attributes))
    histograms.update(generate_comparison_histograms(data_frame, chosen_hospitals, attributes_to_be_compared, continuous_attributes))

    keys = pie_charts.keys()
    pieChartData = []

    for key in keys:
      vals = []
      for i in range(len(pie_charts[key]['data'][0]['labels'])):
        vals.append({
          'label': pie_charts[key]['data'][0]['labels'][i],
          'value': pie_charts[key]['data'][0]['values'][i]
        })
      data = {
        'label' : key,
        'data' : vals
      }
      pieChartData.append(data)

    keys = [ 'Age at diagnosis in years', 'Age at death in years', 'Survival time in years' ]

    histogramData = [
      {
        'label': 'Age at diagnosis in years',
        'data': [
          { 'range': '20-30', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 20, 30) },
          { 'range': '30-40', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 30, 40) },
          { 'range': '40-50', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 40, 50) },
          { 'range': '50-60', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 50, 60) },
          { 'range': '60-70', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 60, 70) },
          { 'range': '70+', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 70, 150) }
        ]
      },
      {
        'label': 'Age at death in years',
        'data': [
          { 'range': '20-30', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 20, 30) },
          { 'range': '30-40', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 30, 40) },
          { 'range': '40-50', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 40, 50) },
          { 'range': '50-60', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 50, 60) },
          { 'range': '60-70', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 60, 70) },
          { 'range': '70+', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 70, 150) }
          ]
      },
      {
        'label': 'Survival time in years',
        'data': [
          { 'range': '0-1', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 0, 1) },
          { 'range': '1-2', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 1, 2) },
          { 'range': '2-3', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 2, 3) },
          { 'range': '3-4', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 3, 4) },
          { 'range': '4-5', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 4, 5) },
          { 'range': '5+', 'value': count_unique(histograms[keys[0]]['data'][0]['x'], 5, 150) }
        ]
      }
    ]

    return {"pie_charts": pie_charts, "histograms": histograms}

def count_unique(values, lower, higher):
  count = 0
  for i in values:
    if i >= lower and i < higher:
      count += 1
  return count