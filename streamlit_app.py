import streamlit as st

st.set_page_config(
    page_title='Rent vs. Buy',
    page_icon='📈',
    layout="wide",
    initial_sidebar_state="collapsed",
    # menu_items=None
)

from main import analyze_zip, pull_all_zhvi_data_melted
from data.zillow import read_zillow_files_from_geography
import plotly.graph_objects as go
import plotly.express as px


COLORS = [
    px.colors.sequential.ice_r,
    px.colors.sequential.Oryel,
    px.colors.sequential.PuRd,
]


def main_page():
    st.write('Welcome')


def compare_zips():
    st.write('Compare Zips...')
    zhvi_dfs = read_zillow_files_from_geography('Zip')

    all_zips = zhvi_dfs[0]['RegionName'].unique()
    zip_codes = st.multiselect(
        label='Zip Code',
        options=all_zips,
        max_selections=3,
        default=[90210],
    )
    fig = go.Figure()
    with st.spinner('Loading...'):
        for i, zip_code in enumerate(zip_codes):
            traces = analyze_zip(int(zip_code), colors=COLORS[i])
            fig.add_traces(traces)
        st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    page_names_to_funcs = {
        # "Main Page": main_page,
        "Compare Zips": compare_zips,
    }

    selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
    page_names_to_funcs[selected_page]()
