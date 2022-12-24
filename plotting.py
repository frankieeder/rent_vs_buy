from data.zillow import read_zillow_files_from_geography
import plotly.express as px
import plotly.graph_objects as go


def analyze_region(
        geography: str,
        region_id: int,
        colors=px.colors.sequential.ice_r
):
    unfiltered = read_zillow_files_from_geography(geography)
    filtered = [df.loc[df['RegionID'] == region_id] for df in unfiltered]
    overall = filtered.pop(0)
    single_family = filtered.pop(0)
    condo = filtered.pop(0)

    region_name = overall['RegionName'].values[0]

    bedrooms = filtered
    traces = []

    # TODO: Lots of shared params between go.Scatter calls, could be abstracted.

    # Bedrooms
    for i, bedroom_df in enumerate(bedrooms):
        traces.append(go.Scatter(
            x=bedroom_df['Month'],
            y=bedroom_df['ZHVI'],
            mode='lines',
            name=f'{i + 1} Bedroom',
            line=dict(color=colors[i+2], width=0.5),
            fill='tonexty' if i > 0 else None,
            legendgroup=str(region_id),
        ))

    default_color = colors[1]
    # Single Family
    traces.append(go.Scatter(
        x=single_family['Month'],
        y=single_family['ZHVI'],
        mode='lines',
        name='Single Family',
        line=dict(color=default_color, width=1, dash='dash'),
        legendgroup=str(region_id),
    ))

    traces.append(go.Scatter(
        x=condo['Month'],
        y=condo['ZHVI'],
        mode='lines',
        name='Condo/Co-Op',
        line=dict(color=default_color, width=1, dash='dot'),
        legendgroup=str(region_id),
    ))

    traces.append(go.Scatter(
        x=overall['Month'],
        y=overall['ZHVI'],
        mode='lines',
        name='Overall',
        line=dict(color=default_color, width=1.5),
        legendgroup=str(region_id),
        legendgrouptitle_text=str(region_name),
    ))
    return traces
