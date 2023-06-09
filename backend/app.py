import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Display the titles
st.set_page_config(page_title="PAG Administrative Dashboard", page_icon=":tada:", layout="wide")
st.title("PAG Administrative Dashboard")

# Make a GET request to the /stats/ endpoint
response = requests.get('http://localhost:8000/stats/')
stats = response.json()

# Display the stats
for column_name, unique_count in stats.items():
    st.write(f'{column_name}: {unique_count}')

st.subheader("Data Summary")

# Make a GET request to the /graphs/ endpoint
response = requests.get('http://localhost:8000/graphs/')

# # For debugging 
# print("Status code:", response.status_code)
# print("Response text:", response.text)

graphs = response.json()

# Generate and display pie charts for each categorical attribute
for attribute, values in graphs['pie_charts'].items():
    st.markdown("#### " + attribute)

    # Convert the values into a DataFrame
    df = pd.DataFrame(list(values.items()), columns=['attribute', 'value'])
    fig = px.pie(df, values='value', names='attribute', title='')
    st.plotly_chart(fig)

colors = ["orange", "blue", "green"]

# Generate and display bar charts for each categorical attribute
for index, (attribute, values) in enumerate(graphs['bar_charts'].items()):
    st.markdown("#### " + attribute)

    # Convert the values into a DataFrame
    df = pd.DataFrame(list(values.items()), columns=['attribute', 'value'])

    fig = px.histogram(df, x='attribute', y='value', title='', 
                       labels={'value': 'Population Count', 'attribute': attribute},
                       color_discrete_sequence=[colors[index]])  # use color index

    fig.update_layout(bargap=0.1)  # Adjust the gap size. 0 means no gap, 1 means maximum gap
    fig.update_layout(yaxis_title="Population Count")
    st.plotly_chart(fig)