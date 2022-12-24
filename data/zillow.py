import pandas as pd
import streamlit as st

GEOGRAPHIES = {
    'Metro': 'Metro & US',
    'State': 'State',
    'County': 'County',
    'City': 'City',
    'Zip': 'Zip Code',
    'Neighborhood': 'Neighborhood'
}

ZHVI_METRICS = {
    'uc_sfrcondo_tier_0.33_0.67_sm_sa_month': 'ZHVI All Homes (SFR, Condo/Co-op) Time Series, Smoothed, Seasonally Adjusted($)',
    # TODO: Enable these
    # '': 'ZHVI All Homes (SFR, Condo/Co-op) Time Series, Raw, Mid-Tier ($)',
    # 'uc_sfrcondo_tier_0.67_1.0_sm_sa_month': 'ZHVI All Homes- Top Tier Time Series ($)',
    # 'uc_sfrcondo_tier_0.0_0.33_sm_sa_month': 'ZHVI All Homes- Bottom Tier Time Series ($)',
    'uc_sfr_tier_0.33_0.67_sm_sa_month': 'ZHVI Single-Family Homes Time Series ($)',
    'uc_condo_tier_0.33_0.67_sm_sa_month': 'ZHVI Condo/Co-op Time Series ($)',
    'bdrmcnt_1_uc_sfrcondo_tier_0.33_0.67_sm_sa_month': 'ZHVI 1-Bedroom Time Series ($)',
    'bdrmcnt_2_uc_sfrcondo_tier_0.33_0.67_sm_sa_month': 'ZHVI 2-Bedroom Time Series ($)',
    'bdrmcnt_3_uc_sfrcondo_tier_0.33_0.67_sm_sa_month': 'ZHVI 3-Bedroom Time Series ($)',
    'bdrmcnt_4_uc_sfrcondo_tier_0.33_0.67_sm_sa_month': 'ZHVI 4-Bedroom Time Series ($)',
    'bdrmcnt_5_uc_sfrcondo_tier_0.33_0.67_sm_sa_month': 'ZHVI 5+ Bedroom Time Series ($)',
}


def infer_zhvi_zillow_file_link(geography, zhvi_metric):
    return f"https://files.zillowstatic.com/research/public_csvs/zhvi/{geography}_zhvi_{zhvi_metric}.csv"


def read_zillow_file_from_link(link):
    df = pd.read_csv(link)
    df = df.set_index('RegionID')
    return df


def find_categorical_columns(zhvi):
    month_start_index = zhvi.columns.to_list().index('2000-01-31')  # TODO: This might be sketchy
    categorical = zhvi.columns[:month_start_index].to_list()
    return categorical


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


@st.experimental_singleton
def read_zillow_file_from_geography_and_metric(geography, zhvi_metric):
    link = infer_zhvi_zillow_file_link(geography, zhvi_metric)
    df = read_zillow_file_from_link(link)
    # TODO: Is there an efficient way to separate this out if we need the underlying wide files?
    df_melted = melt_df(df)
    # TODO: Cast dtypes to categorical if needed to preserve space. Wide data may help for this too.
    return df_melted


def read_zillow_files_from_geography(geography):
    dfs = tuple(read_zillow_file_from_geography_and_metric(geography, m) for m in ZHVI_METRICS.keys())
    return dfs
