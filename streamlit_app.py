# +
# Required Libraries
import folium
import numpy as np
import pandas as pd
import geopandas as gpd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from folium.plugins import HeatMap
from datetime import datetime

from streamlit_folium import folium_static
from plotly.offline import init_notebook_mode
init_notebook_mode(connected=True)

import warnings
warnings.filterwarnings('ignore')
# -

indiv = pd.read_csv('clean.csv')
df = indiv.drop(columns=['Unnamed: 0'])
pd.set_option('display.max_columns',None)
print(f'shape{indiv.shape}')
df.head()

# **`Clean`**

# +
# Convert Object to columns
df = df.astype({col: 'category' for col in df.select_dtypes(include='object').columns})

# Parse Dates
parse_dates = ['start', 'end', 'dob', 'father_death_date', 'mother_death_date']
df[parse_dates] = df[parse_dates].apply(pd.to_datetime, errors='coerce')

# Extract Year from Event Dates
df["year_of_event"] = pd.to_datetime(df['event_date'], errors='coerce').dt.year
df["month_of_event"] = pd.to_datetime(df['event_date'], errors='coerce').dt.month
# -
# **`Streamlit App`**

# +
# Streamlit App Configuration
st.set_page_config(layout='wide', page_title="Maternal & Child Health Dashboard", page_icon="👶")

# Title and Custom Theme
st.markdown("""
    <style>
        body {
            background-color: #f8f9fa;
            color: #333;
        }
        .main-title {
            font-size: 40px;
            font-weight: bold;
            text-align: center;
            color: #4e79a7;
        }
        .section-title {
            font-size: 24px;
            color: #f28e2b;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Maternal & Child Health Outcomes Analysis</h1>", unsafe_allow_html=True)



# +
# Sidebar Filters
st.sidebar.image('logoCISM.png', use_column_width=True)
st.sidebar.title('Outcomes Analysis')
st.sidebar.subheader('Filters')

# Age Range Filter
age_min, age_max = int(df['age'].min()), int(df['age'].max())
age_filter = st.sidebar.slider('Select Age Range:', min_value=age_min, max_value=age_max, value=(age_min, age_max))

# Year Filter
year_min, year_max = int(df['year_of_event'].min()), int(df['year_of_event'].max())
year_filter = st.sidebar.slider('Select Year Range:', min_value=year_min, max_value=year_max, value=(year_min, year_max))

# Gender Filter (Ensure no NaN values and consistent data type)
clean_gender = df['gender'].dropna().unique().tolist()
selected_gender = st.sidebar.multiselect('Select Gender:', options=clean_gender, default=clean_gender)
# -

# Filter Data Based on User Selection
filtered_df = df[
    (df['age'] >= age_filter[0]) & (df['age'] <= age_filter[1]) &
    (df['year_of_event'] >= year_filter[0]) & (df['year_of_event'] <= year_filter[1]) &
    (df['gender'].isin(selected_gender))
]

# Visualizations with Enhanced Styling
st.markdown("<h2 class='section-title'>Data Visualizations</h2>", unsafe_allow_html=True)

# Container for layout
container = st.container()
col1, col2 = container.columns(2)

# +
# # 1. Number of Pregnancies per Mother
# fig1 = px.histogram(filtered_df, x='fertility_nr_pregnancies', color='mother_name', 
#                     title='Number of Pregnancies per Mother', 
#                     labels={'fertility_nr_pregnancies': 'Pregnancies', 'mother_name': 'Mother'}, 
#                     nbins=20, color_discrete_sequence=px.colors.qualitative.Pastel)
# fig1.update_layout(title_font=dict(size=20, color='#4e79a7'))
# col1.plotly_chart(fig1, use_container_width=True)

fig1 = px.box(filtered_df, y='fertility_nr_pregnancies', 
              title='Distribution of Number of Pregnancies per Mother', 
              labels={'fertility_nr_pregnancies': 'Number of Pregnancies'}, 
              color_discrete_sequence=['#4e79a7'])
fig1.update_layout(title_font=dict(size=20, color='#4e79a7'))
col1.plotly_chart(fig1, use_container_width=True)


fig2 = px.scatter(filtered_df, x='fertility_nr_livebirths', y='fertility_nr_stillbirths', 
                  color='fertility_has_prev_pregnancies',
                  title='Live Births vs. Stillbirths (By Previous Pregnancies)',
                  labels={'fertility_nr_livebirths': 'Live Births', 'fertility_nr_stillbirths': 'Stillbirths', 'fertility_has_prev_pregnancies': 'Has Previous Pregnancies'},
                  color_discrete_sequence=px.colors.qualitative.T10)
fig2.update_layout(title_font=dict(size=20, color='#f28e2b'))
col2.plotly_chart(fig2, use_container_width=True)

# 3. Analysis of Twin Outcomes & 4. Analysis of Miscarriages and Abortions
col3, col4 = st.columns(2)

fig3 = px.box(filtered_df, y='fertility_nr_twin_outcomes', color='gender',
              title='Twin Outcomes Distribution by Gender',
              labels={'fertility_nr_twin_outcomes': 'Number of Twin Outcomes'},
              color_discrete_sequence=px.colors.qualitative.Dark24)
fig3.update_layout(title_font=dict(size=20, color='#e15759'))
col3.plotly_chart(fig3, use_container_width=True)

outcome_types = filtered_df[['fertility_nr_livebirths', 'fertility_nr_stillbirths', 'fertility_nr_miscarriages', 'fertility_nr_abortions']]
outcome_totals = outcome_types.sum().reset_index()
outcome_totals.columns = ['Outcome Type', 'Total Count']

fig4 = px.bar(outcome_totals, x='Outcome Type', y='Total Count',
              color='Outcome Type', title='Distribution of Pregnancy Outcomes',
              labels={'Total Count': 'Total Count', 'Outcome Type': 'Type of Outcome'},
              color_discrete_sequence=px.colors.qualitative.Prism)
fig4.update_layout(title_font=dict(size=20, color='#76b7b2'))
col4.plotly_chart(fig4, use_container_width=True)

# 5. Total Live Births: Boys vs. Girls & 6. Analysis of Multiple Births (Twins, Triplets, Quadruplets)
col5, col6 = st.columns(2)

fig5 = px.bar(filtered_df, x='fertility_nr_alive_boys', y='fertility_nr_alive_girls', 
              color='gender', 
              title='Total Live Births: Boys vs. Girls',
              labels={'fertility_nr_alive_boys': 'Boys', 'fertility_nr_alive_girls': 'Girls'},
              barmode='group', color_discrete_sequence=px.colors.qualitative.Safe)
fig5.update_layout(title_font=dict(size=20, color='#59a14f'))
col5.plotly_chart(fig5, use_container_width=True)

fig6 = px.box(filtered_df, y=['fertility_nr_twins_alive', 'fertility_nr_triplet_outcomes', 'fertility_nr_quadr_outcomes'],
              title='Distribution of Multiple Birth Outcomes',
              labels={'value': 'Count', 'variable': 'Type of Outcome'},
              color_discrete_sequence=px.colors.qualitative.Vivid)
fig6.update_layout(title_font=dict(size=20, color='#e15759'))
col6.plotly_chart(fig6, use_container_width=True)

# 7. Education and Fertility Relationship & 8. Work Regime and Pregnancy Outcomes
col7, col8 = st.columns(2)

fig7 = px.box(filtered_df, x='has_education', y='fertility_nr_pregnancies',
              title='Fertility vs. Education Status',
              labels={'has_education': 'Education', 'fertility_nr_pregnancies': 'Number of Pregnancies'},
              color_discrete_sequence=['#17becf'])
fig7.update_layout(title_font=dict(size=20, color='#ff7f0e'))
col7.plotly_chart(fig7, use_container_width=True)

fig8 = px.histogram(filtered_df, x='work_regime', y='fertility_nr_livebirths',
                    title='Work Regime and Live Birth Outcomes',
                    labels={'work_regime': 'Work Regime', 'fertility_nr_livebirths': 'Live Births'},
                    color='work_regime', color_discrete_sequence=px.colors.qualitative.Prism)
fig8.update_layout(title_font=dict(size=20, color='#9467bd'))
col8.plotly_chart(fig8, use_container_width=True)

# 9. ID Documentation Impact on Birth Registrations & 10. Trend Over Years: Total Pregnancies
col9, col10 = st.columns(2)

fig9 = px.pie(filtered_df, names='has_id_card', values='fertility_nr_livebirths',
              title='Impact of ID Documentation on Birth Registrations',
              color_discrete_sequence=px.colors.qualitative.Set3)
fig9.update_layout(title_font=dict(size=20, color='#bcbd22'))
col9.plotly_chart(fig9, use_container_width=True)

yearly_trend = filtered_df.groupby('year_of_event')['fertility_nr_pregnancies'].sum().reset_index()
fig10 = px.line(yearly_trend, x='year_of_event', y='fertility_nr_pregnancies',
                title='Total Pregnancies Trend Over Years',
                labels={'year_of_event': 'Year', 'fertility_nr_pregnancies': 'Total Pregnancies'},
                color_discrete_sequence=['#1f77b4'])
fig10.update_layout(title_font=dict(size=20, color='#4e79a7'))
col10.plotly_chart(fig10, use_container_width=True)

# 11. Monthly Trend Analysis
col11, _ = st.columns([1, 0.1])  # Just one plot in this row, center it

monthly_trend = filtered_df.groupby('month_of_event')['fertility_nr_pregnancies'].sum().reset_index()
fig11 = px.line(monthly_trend, x='month_of_event', y='fertility_nr_pregnancies',
                title='Total Pregnancies Trend Over Months',
                labels={'month_of_event': 'Month', 'fertility_nr_pregnancies': 'Total Pregnancies'},
                color_discrete_sequence=['#ff7f0e'])
fig11.update_xaxes(tickvals=np.arange(1, 13), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
fig11.update_layout(title_font=dict(size=20, color='#4e79a7'))
col11.plotly_chart(fig11, use_container_width=True)

# Footer Information
st.sidebar.info("By: Nelio Lino Nhacolo")

# Display Raw Data
if st.sidebar.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(filtered_df.head(100))
# -

# !streamlit run streamlit_app.py


