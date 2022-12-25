import pandas as pd
import streamlit as st
from urllib.error import HTTPError
import re

GEOGRAPHIES = {
    'Metro': 'Metro & US',
    'State': 'State',
    'County': 'County',
    'City': 'City',
    'Zip': 'Zip Code',
    'Neighborhood': 'Neighborhood'
}

AVAILABLE_METRICS = {
    # Format: link_suffix = (detailed_metric_name, short_metric_name)
    'zhvi/{geography}_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month': (
        'ZHVI All Homes (SFR, Condo/Co-op) Time Series, Smoothed, Seasonally Adjusted($)',
        'Overall'
    ),
    # TODO: Enable these
    # '': 'ZHVI All Homes (SFR, Condo/Co-op) Time Series, Raw, Mid-Tier ($)',
    # 'uc_sfrcondo_tier_0.67_1.0_sm_sa_month': 'ZHVI All Homes- Top Tier Time Series ($)',
    # 'uc_sfrcondo_tier_0.0_0.33_sm_sa_month': 'ZHVI All Homes- Bottom Tier Time Series ($)',
    'zhvi/{geography}_zhvi_uc_sfr_tier_0.33_0.67_sm_sa_month': (
        'ZHVI Single-Family Homes Time Series ($)',
        'Single Family'
    ),
    'zhvi/{geography}_zhvi_uc_condo_tier_0.33_0.67_sm_sa_month': (
        'ZHVI Condo/Co-op Time Series ($)',
        'Condo/Co-Op'
    ),
    'zhvi/{geography}_zhvi_bdrmcnt_1_uc_sfrcondo_tier_0.33_0.67_sm_sa_month': (
        'ZHVI 1-Bedroom Time Series ($)',
        '1 Bedroom'
    ),
    'zhvi/{geography}_zhvi_bdrmcnt_2_uc_sfrcondo_tier_0.33_0.67_sm_sa_month': (
        'ZHVI 2-Bedroom Time Series ($)',
        '2 Bedroom'
    ),
    'zhvi/{geography}_zhvi_bdrmcnt_3_uc_sfrcondo_tier_0.33_0.67_sm_sa_month': (
        'ZHVI 2-Bedroom Time Series ($)',
        '3 Bedroom'
    ),
    'zhvi/{geography}_zhvi_bdrmcnt_4_uc_sfrcondo_tier_0.33_0.67_sm_sa_month': (
        'ZHVI 2-Bedroom Time Series ($)',
        '4 Bedroom'
    ),
    'zhvi/{geography}_zhvi_bdrmcnt_5_uc_sfrcondo_tier_0.33_0.67_sm_sa_month': (
        'ZHVI 2-Bedroom Time Series ($)',
        '5+ Bedroom'
    ),
    'zori/{geography}_zori_sm_month': (
        'ZORI',
        'Rent Index'
    )
}
st.write()

METRIC_NAME = 'ZHVI'
TIME_NAME = 'Month'
TIME_PATTERN = re.compile("\d{4}-\d{2}-\d{2}")

DTYPE_OVERRIDES = {
    'RegionID': 'int32',
    'SizeRank': 'int32',
    # 'RegionName': 'category',
    'RegionType': 'category',
    'StateName': 'category',
    'State': 'category',
    # 'City': 'category',
    'Metro': 'category',
    'CountyName': 'category',
}


def infer_zillow_file_link(geography, zhvi_metric):
    return f"https://files.zillowstatic.com/research/public_csvs/{zhvi_metric.format(geography=geography)}.csv"


def read_zillow_file_from_link(link):

    df = pd.read_csv(link)
    float_cols = df.select_dtypes(include='float64').columns
    df[float_cols] = df[float_cols].astype('float32')
    return df


def find_categorical_columns_zhvi_wide(zhvi_wide):
    cols_list = zhvi_wide.columns.to_list()
    month_start_index = next(i for i, item in enumerate(cols_list) if re.search(TIME_PATTERN, item))
    categorical = zhvi_wide.columns[:month_start_index].to_list()
    return categorical


def melt_df(zhvi_wide):
    categorical = find_categorical_columns_zhvi_wide(zhvi_wide)
    months_of_interest = zhvi_wide.columns[len(categorical):].to_list()

    zhvi_melted = zhvi_wide.melt(
        id_vars=categorical,
        value_vars=months_of_interest,
        var_name=TIME_NAME,
        value_name=METRIC_NAME
    )
    zhvi_melted = zhvi_melted.dropna(subset=METRIC_NAME)
    zhvi_melted = zhvi_melted.astype({
        TIME_NAME: 'category',
        METRIC_NAME: 'float32'
    })
    zhvi_melted = zhvi_melted.reset_index(drop=True)
    return zhvi_melted


@st.experimental_singleton
def read_zillow_file_from_geography_and_metric_wide(geography, zhvi_metric):
    link = infer_zillow_file_link(geography, zhvi_metric)
    try:
        df_wide = read_zillow_file_from_link(link)
    except HTTPError as err:
        if err.code == 404:
            return None  # If not found, return None
        else:
            raise err
    return df_wide


def read_zillow_file_from_geography_and_metric(geography, zhvi_metric, region_id):
    df_wide = read_zillow_file_from_geography_and_metric_wide(geography, zhvi_metric)

    if df_wide is not None:
        # Cast dtypes if possible
        overrideable_dtype_columns = set(df_wide.columns) & DTYPE_OVERRIDES.keys()
        dtypes = {k: v for k, v in DTYPE_OVERRIDES.items() if k in overrideable_dtype_columns}
        overrideable_dtype_columns = list(overrideable_dtype_columns)
        df_wide[overrideable_dtype_columns] = df_wide[overrideable_dtype_columns].astype(dtypes)

        # Filter before melting as melting greatly increases memory usage
        df_wide = df_wide[df_wide['RegionID'] == region_id]

        # Melt to prepare for plotly
        df_melted = melt_df(df_wide)

        return df_melted
    else:
        st.warning(f"Note: Metric '{AVAILABLE_METRICS[zhvi_metric][0]}' not available for geography '{geography}'")
        return df_wide


def read_zillow_files_from_geography_wide(geography):
    dfs = {
        t2: read_zillow_file_from_geography_and_metric_wide(geography, m)
        for m, (t1, t2) in AVAILABLE_METRICS.items()
    }
    return dfs


def read_zillow_files_from_geography(geography, region_id):
    dfs = {
        t2: read_zillow_file_from_geography_and_metric(geography, m, region_id)
        for m, (t1, t2) in AVAILABLE_METRICS.items()
    }
    return dfs
