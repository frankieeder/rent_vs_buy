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
    )

    zhvi_dfs = read_zillow_files_from_geography(geography)

    options_df = zhvi_dfs[0][['RegionID', 'RegionName']]
    options_df = options_df.drop_duplicates().sort_values('RegionName')
    all_region_ids_series = options_df['RegionID']
    all_region_ids_to_names = options_df.set_index('RegionID')['RegionName'].to_dict()
    # Set region default to 102001 (RegionID of US) if using metro (i.e. default view)
    region_default = [102001] if geography == 'Metro' else all_region_ids_series.values[0]
    region_ids = st.multiselect(
        label=GEOGRAPHIES[geography],
        options=all_region_ids_series,  # Use ID instead of name directly to avoid collisions
        max_selections=3,
        default=region_default,
        format_func=lambda r: all_region_ids_to_names[r]
    )
    fig = go.Figure()
    with st.spinner('Loading...'):
        for i, region_id in enumerate(region_ids):
            traces = analyze_region(geography, region_id, colors=COLORS[i])
            fig.add_traces(traces)
        st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    page_names_to_funcs = {
        # "Main Page": main_page,
        "Compare Zips": compare_regions,
    }

    selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
    page_names_to_funcs[selected_page]()
