import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import json

# Read the data model configuration from the JSON file
with open('data_model.json') as f:
    data_model = json.load(f)

# Transform the raw data
def preprocess_data(data_frame):
    date_columns, age_columns = get_column_names(data_model)

    # Convert dates to datetime
    for column in date_columns:
        data_frame[column] = pd.to_datetime(data_frame[column], format='%Y-%m-%d')

    # Calculate ages
    data_frame["Age at diagnosis in years"] = (data_frame["Date of diagnosis"] - data_frame["Date of birth"]) / np.timedelta64(1, 'Y')
    data_frame["Age at death in years"] = (data_frame["Date of death"] - data_frame["Date of birth"]) / np.timedelta64(1, 'Y')
    data_frame["Survival time in years"] = (data_frame["Date of death"] - data_frame["Date of diagnosis"]) / np.timedelta64(1, 'Y')

    # Round age_columns
    for column in age_columns:
        data_frame[column] = data_frame[column].round(2)
    
# Return categorical and continuous attributes from the data model
def get_attributes_by_type(data_frame):
    categorical_attributes = []
    for key, value in data_model.items():
        if value['__type__'] == 'SeriesDataModelCategorical':
            categorical_attributes.append(value['series_name'])
    continuous_attributes = get_column_names(data_model)[1]
    return categorical_attributes, continuous_attributes

# Return column names used in data preprocessing
def get_column_names(data_model):
    # General columns
    date_columns = []

    for key, value in data_model.items():
        if value['__type__'] == 'SeriesDataModelDate':
            date_columns.append(value['series_name'])

    # Specific columns
    age_columns = ["Age at diagnosis in years", "Age at death in years", "Survival time in years"]

    return date_columns, age_columns

# Count unique values
def count_values(data_frame):
    patient_count = 15000 # data_frame.index.value_counts()
    hospital_count = data_frame['Hospital name'].nunique()

    return patient_count, hospital_count

# Generate pie charts for each categorical attribute
def generate_pie_charts(data_frame, categorical_attributes):
    pie_charts = {}
    for column in categorical_attributes:
        if column in data_frame.columns:
            val_counts = data_frame[column].value_counts()
            val_counts_df = pd.DataFrame({'attribute': val_counts.index, 'value': val_counts.values})

            pie_chart = px.pie(val_counts_df, values='value', names='attribute', title='').to_json()
            pie_charts[column] = json.loads(pie_chart)
    return pie_charts

# Generates histograms for each continuous attribute
def generate_histograms(data_frame, continuous_attributes):
    histograms = {}
    for column in continuous_attributes:
        if column in data_frame.columns:
            hist = px.histogram(data_frame, x=column, nbins=50, title='', labels={'value': 'Count', column: column}).to_json()
            histograms[column] = json.loads(hist)
    return histograms

# Validate the chosen hospitals and attributes for comparison
def validate_inputs(data_frame, chosen_hospitals, attributes_to_be_compared):
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
def generate_comparison_pie_charts(data_frame, chosen_hospitals, attributes_to_be_compared, categorical_attributes):
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
def generate_comparison_histograms(data_frame, chosen_hospitals, attributes_to_be_compared, continuous_attributes):
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