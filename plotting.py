from data.zillow import read_zillow_files_from_geography, TIME_NAME, METRIC_NAME
import plotly.express as px
import plotly.graph_objects as go

BEDROOM_PLOT_ORDER = [
    '1 Bedroom',
    '2 Bedroom',
    '3 Bedroom',
    '4 Bedroom',
    '5+ Bedroom',
]

METRIC_PLOT_ORDER = [
    *BEDROOM_PLOT_ORDER,
    'Single Family',
    'Condo/Co-Op',
    'Overall',
    'Rent Index'
]  # TODO: Can use this if needed to abstract region analysis code into loop


def analyze_region(
        geography: str,
        region_id: int,
        colors=px.colors.sequential.ice_r
):
    dfs = read_zillow_files_from_geography(geography, region_id)

    rent = dfs['Rent Index']

    overall = dfs['Overall']
    single_family = dfs['Single Family']
    condo = dfs['Condo/Co-Op']

    region_name = overall['RegionName'].values[0]

    bedrooms = {b: dfs[b] for b in BEDROOM_PLOT_ORDER}
    traces_buy = []
    traces_rent = []

    # TODO: Lots of shared params between go.Scatter calls, could be abstracted.

    # Bedrooms
    for i, (bedroom_name, bedroom_df) in enumerate(bedrooms.items()):
        traces_buy.append(go.Scatter(
            x=bedroom_df['Month'],
            y=bedroom_df['ZHVI'],
            mode='lines',
            name=bedroom_name,
            line=dict(color=colors[i+2], width=0.5),
            fill='tonexty' if i > 0 else None,
            legendgroup=str(region_id),
        ))

    default_buy_color = colors[2]
    # Single Family
    traces_buy.append(go.Scatter(
        x=single_family['Month'],
        y=single_family['ZHVI'],
        mode='lines',
        name='Single Family',
        line=dict(color=default_buy_color, width=1, dash='dash'),
        legendgroup=str(region_id),
    ))

    traces_buy.append(go.Scatter(
        x=condo['Month'],
        y=condo['ZHVI'],
        mode='lines',
        name='Condo/Co-Op',
        line=dict(color=default_buy_color, width=1, dash='dot'),
        legendgroup=str(region_id),
    ))

    if rent is not None:
        traces_rent.append(go.Scatter(
            x=rent['Month'],
            y=rent['ZHVI'],
            mode='lines',
            name='Rent Index',
            line=dict(color=colors[1], width=1.5),
            legendgroup=str(region_id),
            legendgrouptitle_text=str(region_name),
        ))

    traces_buy.append(go.Scatter(
        x=overall['Month'],
        y=overall['ZHVI'],
        mode='lines',
        name='Overall',
        line=dict(color=default_buy_color, width=1.5),
        legendgroup=str(region_id),
        legendgrouptitle_text=str(region_name),
    ))
    return traces_buy, traces_rent
