import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# https://www.zillow.com/research/data/
DATA_ROOT = Path('./data')

# TODO: Check against census data https://www.unitedstateszipcodes.org/rankings/price_to_rent_ratio/
def naive_ptr_by_metro():
    zhvi_metro = pd.read_csv(DATA_ROOT / 'Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv')
    zhvi_metro = zhvi_metro.set_index('RegionID')
    zori_metro = pd.read_csv(DATA_ROOT / 'Metro_zori_sm_month.csv')
    zori_metro = zori_metro.set_index('RegionID')
    zhvi_metro_trimmed = zhvi_metro.loc[zori_metro.index]
    categorical = zori_metro.columns[:4].to_list()
    months_of_interest = zori_metro.columns[4:].to_list()
    zhvi_metro_trimmed = zhvi_metro_trimmed[categorical + months_of_interest]
    # Naive Price-to-Rent ratio
    ptr_metro = zhvi_metro_trimmed.copy()
    ptr_metro[months_of_interest] /= (zori_metro[months_of_interest] * 12)
    ptr_metro_ca = ptr_metro.loc[ptr_metro['StateName'] == 'CA']
    ptr_metro_melted_ca = ptr_metro_ca.melt(
        id_vars=categorical,
        value_vars=months_of_interest,
        var_name='Month',
        value_name='PTR'
    )
    ptr_metro_melted_ca = ptr_metro_melted_ca.dropna(subset='PTR')

    fig = px.line(ptr_metro_melted_ca, x='Month', y='PTR', color='RegionName')
    fig.show()

def read_single_file(file_name):
    df =  pd.read_csv(DATA_ROOT / file_name)
    df = df.set_index('RegionID')
    return df

def pull_data(prefix='Zip'):
    file_names = [
        f'{prefix}_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv',
        f'{prefix}_zhvf_growth_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv',
        f'{prefix}_zori_sm_month.csv',
    ]
    dfs = tuple(read_single_file(f) for f in file_names)
    return dfs


def melt_df(zhvi):
    categorical = find_categorical_columns(zhvi)
    months_of_interest = zhvi.columns[len(categorical):].to_list()

    zhvi_melted = zhvi.melt(
        id_vars=categorical,
        value_vars=months_of_interest,
        var_name='Month',
        value_name='ZHVI'
    )
    zhvi_melted = zhvi_melted.dropna(subset='ZHVI')
    return zhvi_melted


def pull_all_zhvi_data():
    file_names = [
        'Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv',
        'Zip_zhvi_uc_sfr_tier_0.33_0.67_sm_sa_month.csv',
        'Zip_zhvi_uc_condo_tier_0.33_0.67_sm_sa_month.csv',
        'Zip_zhvi_bdrmcnt_1_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv',
        'Zip_zhvi_bdrmcnt_2_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv',
        'Zip_zhvi_bdrmcnt_3_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv',
        'Zip_zhvi_bdrmcnt_4_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv',
        'Zip_zhvi_bdrmcnt_5_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv',
    ]
    dfs = tuple(read_single_file(f) for f in file_names)
    return dfs

@st.experimental_singleton
def pull_all_zhvi_data_melted():
    dfs = pull_all_zhvi_data()
    dfs_melted = [melt_df(df) for df in dfs]
    return dfs_melted


def find_categorical_columns(zhvi):
    month_start_index = zhvi.columns.to_list().index('2000-01-31')
    categorical = zhvi.columns[:month_start_index].to_list()
    return categorical



def naive_ptr(prefix='Zip'):
    zhvi, _, zori = pull_data('Zip')
    categorical = find_categorical_columns(zhvi)
    months_of_interest = zori.columns[len(categorical):].to_list()

    common_indices = set(zhvi.index) & set(zori.index)
    zhvi_trimmed = zhvi.loc[common_indices]
    zhvi_trimmed = zhvi_trimmed[categorical + months_of_interest]
    zori_trimmed = zori.loc[common_indices]

    ptr_metro = zhvi_trimmed.copy()
    ptr_metro[months_of_interest] /= (zori_trimmed[months_of_interest] * 12)
    ptr_metro_melted = ptr_metro.melt(
        id_vars=categorical,
        value_vars=months_of_interest,
        var_name='Month',
        value_name='PTR'
    )

    ptr_metro_melted = ptr_metro_melted.dropna(subset='PTR')
    return ptr_metro_melted


def naive_ptr_by_zip():
    naive_ptr_melted = naive_ptr('Zip')
    naive_ptr_melted = naive_ptr_melted.loc[naive_ptr_melted['CountyName'] == 'Riverside County']
    fig = px.line(naive_ptr_melted, x='Month', y='PTR', color='RegionName',
                  hover_data=['City', 'Metro', 'CountyName'])
    fig.show()


def analyze_zip(zip_code):
    unfiltered = pull_all_zhvi_data_melted()
    filtered = [df.loc[df['RegionName'] == zip_code] for df in unfiltered]
    color_map = {
        'overall': px.colors.sequential.ice_r[6],
        'single_family': px.colors.sequential.ice_r[6],
        'condo': px.colors.sequential.ice_r[6],
        '1_br': px.colors.sequential.ice_r[0],
        '2_br': px.colors.sequential.ice_r[1],
        '3_br': px.colors.sequential.ice_r[2],
        '4_br': px.colors.sequential.ice_r[3],
        '5_br': px.colors.sequential.ice_r[4],
    }
    overall = filtered.pop(0)
    single_family = filtered.pop(0)
    condo = filtered.pop(0)

    bedrooms = filtered
    fig = go.Figure()
    # Bedrooms
    for i, bedroom_df in enumerate(bedrooms):
        fig.add_trace(go.Scatter(
            x=bedroom_df['Month'],
            y=bedroom_df['ZHVI'],
            mode='lines',
            name=f'{i + 1} Bedroom',
            line=dict(color=px.colors.sequential.ice_r[i+4], width=0.5),
            fill='tonexty' if i > 0 else None,
            legendgroup=zip_code,
        ))

    default_color = px.colors.sequential.ice_r[2]
    # Single Family
    fig.add_trace(go.Scatter(
        x=single_family['Month'],
        y=single_family['ZHVI'],
        mode='lines',
        name='Single Family',
        line=dict(color=default_color, width=0.5, dash='dash'),
        legendgroup=zip_code,
    ))

    fig.add_trace(go.Scatter(
        x=condo['Month'],
        y=condo['ZHVI'],
        mode='lines',
        name='Condo/Co-Op',
        line=dict(color=default_color, width=0.5, dash='dot'),
        legendgroup=zip_code,
    ))

    fig.add_trace(go.Scatter(
        x=overall['Month'],
        y=overall['ZHVI'],
        mode='lines',
        name='Overall',
        line=dict(color=default_color, width=0.5),
        legendgroup=zip_code,
    ))
    return fig


    for name, df in zip(color_map.keys(), filtered):
        df['name'] = name
        if name == 'single_family':
            df['line_marker'] = 'dash'
        elif name == 'condo':
            df['line_marker'] = 'dot'
        else:
            df['line_marker'] = 'line'
    concatenated = pd.concat(filtered)
    fig = px.line(
        concatenated,
        x='Month',
        y='ZHVI',
        color='name',
        color_discrete_map=color_map,
        line_dash='line_marker'
    )
    return fig


def home_prices_by_zip():
    zhvi, zhvi_fc, _ = pull_data('Zip')
    categorical = find_categorical_columns(zhvi)
    months_of_interest = zhvi.columns[len(categorical):].to_list()
    zhvi_cropped = zhvi.loc[zhvi['City'] == 'Palm Springs']
    zhvi_melted = zhvi_cropped.melt(
        id_vars=categorical,
        value_vars=months_of_interest,
        var_name='Month',
        value_name='ZHVI',
    )
    fig = px.line(zhvi_melted, x='Month', y='ZHVI', color='RegionName',
                  hover_data=['City', 'Metro', 'CountyName'])
    fig.show()
    x = 2


# naive_ptr_by_zip()

