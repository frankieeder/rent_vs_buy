import pandas as pd
import streamlit as st
import io

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


def infer_zhvi_zillow_file_link(geography, zhvi_metric):
    return f"https://files.zillowstatic.com/research/public_csvs/zhvi/{geography}_zhvi_{zhvi_metric}.csv"


def read_zillow_file_from_link(link):
    df = pd.read_csv(link)
    float_cols = df.select_dtypes(include='float64').columns
    df[float_cols] = df[float_cols].astype('float32')
    return df


def find_categorical_columns_zhvi_wide(zhvi_wide):
    month_start_index = zhvi_wide.columns.to_list().index('2000-01-31')  # TODO: This might be sketchy
    categorical = zhvi_wide.columns[:month_start_index].to_list()
    return categorical


def melt_df(zhvi_wide):
    categorical = find_categorical_columns_zhvi_wide(zhvi_wide)
    months_of_interest = zhvi_wide.columns[len(categorical):].to_list()

    zhvi_melted = zhvi_wide.melt(
        id_vars=categorical,
        value_vars=months_of_interest,
        var_name='Month',
        value_name='ZHVI'
    )
    zhvi_melted = zhvi_melted.dropna(subset='ZHVI')
    zhvi_melted = zhvi_melted.astype({
        'Month': 'category',
        'ZHVI': 'float32'
    })
    zhvi_melted = zhvi_melted.reset_index(drop=True)
    return zhvi_melted


@st.experimental_singleton
def read_zillow_file_from_geography_and_metric_wide(geography, zhvi_metric):
    link = infer_zhvi_zillow_file_link(geography, zhvi_metric)
    df_wide = read_zillow_file_from_link(link)
    return df_wide


def read_zillow_file_from_geography_and_metric(geography, zhvi_metric):
    df_wide = read_zillow_file_from_geography_and_metric_wide(geography, zhvi_metric)
    # st.write(f"Total Wide: {df_wide.memory_usage().sum()}")
    # st.write(df_wide.memory_usage())
    # st.write(df_wide.dtypes)
    # buffer = io.StringIO()
    # df_wide.info(buf=buffer)
    # st.text(buffer.getvalue())

    overrideable_dtype_columns = set(df_wide.columns) & DTYPE_OVERRIDES.keys()
    dtypes = {k: v for k, v in DTYPE_OVERRIDES.items() if k in overrideable_dtype_columns}
    overrideable_dtype_columns = list(overrideable_dtype_columns)
    df_wide[overrideable_dtype_columns] = df_wide[overrideable_dtype_columns].astype(dtypes)


    # st.write(f"Total Wide w/ Types: {df_wide.memory_usage().sum()}")
    # st.write(df_wide.memory_usage())
    # st.write(df_wide.dtypes)
    # buffer = io.StringIO()
    # df_wide.info(buf=buffer)
    # st.text(buffer.getvalue())
    df_melted = melt_df(df_wide)

    # st.write(f"Total Melt: {df_melted.memory_usage().sum()}")
    # st.write(df_melted.memory_usage())
    # st.write(df_melted.dtypes)
    # buffer = io.StringIO()
    # df_melted.info(buf=buffer)
    # st.text(buffer.getvalue())
    # TODO: Cast dtypes to categorical if needed to preserve space. Wide data may help for this too.
    return df_melted


def read_zillow_files_from_geography_wide(geography):
    dfs = tuple(read_zillow_file_from_geography_and_metric_wide(geography, m) for m in ZHVI_METRICS.keys())
    return dfs


def read_zillow_files_from_geography(geography):
    dfs = tuple(read_zillow_file_from_geography_and_metric(geography, m) for m in ZHVI_METRICS.keys())
    return dfs
