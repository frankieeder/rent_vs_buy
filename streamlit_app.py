import streamlit as st

st.set_page_config(
    page_title='Rent vs. Buy',
    page_icon='📈',
    layout="wide",
    initial_sidebar_state="collapsed",
    # menu_items=None
)

from plotting import analyze_region
from data.zillow import read_zillow_files_from_geography, GEOGRAPHIES
import plotly.graph_objects as go
import plotly.express as px


COLORS = [
    px.colors.sequential.ice_r,
    px.colors.sequential.Oryel,
    px.colors.sequential.PuRd,
]


def main_page():
    st.write('Welcome')


def compare_regions():
    st.write('Compare Regions...')
    geography = st.selectbox(
        label='Geography',
        options=GEOGRAPHIES.keys(),
        format_func=lambda g: GEOGRAPHIES[g],
        index=4,
    )

    zhvi_dfs = read_zillow_files_from_geography(geography)

    all_regions = zhvi_dfs[0]['RegionName'].unique()  # TODO: Should probably base on ID not Name to avoid collision
    regions = st.multiselect(
        label=GEOGRAPHIES[geography],
        options=all_regions,
        max_selections=3,
        default=[90210],  # TODO: Needs to be updated
    )
    fig = go.Figure()
    with st.spinner('Loading...'):
        for i, region in enumerate(regions):
            traces = analyze_region(geography, (region), colors=COLORS[i])
            fig.add_traces(traces)
        st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    page_names_to_funcs = {
        # "Main Page": main_page,
        "Compare Zips": compare_regions,
    }

    selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
    page_names_to_funcs[selected_page]()
