import streamlit as st
import requests
import plotly.graph_objs as go

# Display the titles
st.set_page_config(page_title="PAG Administrative Dashboard", page_icon=":tada:", layout="wide")
st.title("PAG Administrative Dashboard")

# Make a GET request to the /stats/ endpoint
response = requests.get('http://localhost:8000/stats/')
stats = response.json()

# Display the stats
for column_name, unique_count in stats.items():
    st.write(f'{column_name}: {unique_count}')

# Subheader 
st.subheader("Data Summary")

# Make a GET request to the /graphs/ endpoint
response = requests.get('http://localhost:8000/graphs/')
graphs = response.json()

# Display the pie charts
for attribute, pie_chart_data in graphs['pie_charts'].items():
    st.markdown("#### " + attribute)
    fig = go.Figure(pie_chart_data)
    st.plotly_chart(fig)

# Display the histograms
for attribute, histogram_data in graphs['histograms'].items():
    st.markdown("#### " + attribute)
    fig = go.Figure(histogram_data)
    fig.update_layout(bargap=0.1)
    st.plotly_chart(fig)

# Define the request parameters
request_params = {
    "chosen_hospitals": ["Saint Jacob Clinic", "Mercy General Hospital"],
    "attributes_to_be_compared": ["Sex", "Age at diagnosis in years"]
}

# Make a GET request to the /compare/ endpoint
response = requests.get('http://localhost:8000/compare/', json=request_params)
# print("Response: ", response.text)

# In case the server doesn't return any data, initialize empty dictionary
if response.text:
    comparison_metrics = response.json()
else:
    comparison_metrics = {}

# Display the piecharts and histograms for chosen hospitals and attributes
if 'detail' in comparison_metrics:
    st.error(f"Error in comparison metrics API response: {comparison_metrics['detail']}")
else:
    for key, figure_json in comparison_metrics["pie_charts"].items():
        st.markdown(f'#### {key}')
        fig = go.Figure(data=figure_json["data"], layout=figure_json["layout"])
        st.plotly_chart(fig)

    for key, figure_json in comparison_metrics["histograms"].items():
        st.markdown(f'#### {key}')
        fig = go.Figure(data=figure_json["data"], layout=figure_json["layout"])
        st.plotly_chart(fig)