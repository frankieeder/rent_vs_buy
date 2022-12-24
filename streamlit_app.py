import streamlit as st

st.set_page_config(
    page_title='Rent vs. Buy',
    page_icon='📈',
    layout="wide",
    initial_sidebar_state="collapsed",
    # menu_items=None
)

from plotting import analyze_region
from data.zillow import read_zillow_files_from_geography_wide
from data.zillow import find_categorical_columns_zhvi_wide
from data.zillow import GEOGRAPHIES
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
    st.title("Rent vs. Buy")
    st.header("Comparison Between Regions over Time")
    st.write('Please select a Geography below to select the scale on which you want to compare regions, '
             'then select your regions of interest!')
    st.markdown('---')
    geography = st.selectbox(
        label='Geography',
        options=GEOGRAPHIES.keys(),
        format_func=lambda g: GEOGRAPHIES[g],
    )

    zhvi_dfs = read_zillow_files_from_geography_wide(geography)
    zhvi_df_overall = zhvi_dfs[0]
    zhvi_categorical_columns = find_categorical_columns_zhvi_wide(zhvi_df_overall)
    zhvi_categories_df = zhvi_df_overall[zhvi_categorical_columns]

    # Isolate and sort options for regions
    options_df = zhvi_categories_df.drop_duplicates(subset=['RegionID', 'RegionName']).sort_values('RegionName')
    all_region_ids_series = options_df['RegionID']
    options_df_for_mapping = options_df.set_index('RegionID')
    all_region_ids_to_names = options_df_for_mapping['RegionName'].to_dict()
    # If Neighborhood, we'll need additional information to distinguish colliding RegionNames
    if geography in ['Neighborhood', 'City', 'County']:
        all_region_ids_to_state = options_df_for_mapping['StateName'].to_dict()
        if geography == 'Neighborhood':
            all_region_ids_to_county = options_df_for_mapping['CountyName'].to_dict()
    # Set region default to 102001 (RegionID of US) if using metro (i.e. default view)
    region_default = [102001] if geography == 'Metro' else all_region_ids_series.values[0]

    def region_formatter(region_id):
        """Converts our region_id candidate selections into readable, unique text."""
        region_name = all_region_ids_to_names[region_id]
        if geography == 'Neighborhood':
            state = all_region_ids_to_state[region_id]
            county = all_region_ids_to_county[region_id]
            return f"{region_name}, {county}, {state}"
        elif geography in ['City', 'County']:
            state = all_region_ids_to_state[region_id]
            return f"{region_name}, {state}"
        else:
            return region_name

    region_ids = st.multiselect(
        label=GEOGRAPHIES[geography],
        options=all_region_ids_series,  # Use ID instead of name directly to avoid collisions
        max_selections=len(COLORS),
        default=region_default,
        format_func=region_formatter,
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
