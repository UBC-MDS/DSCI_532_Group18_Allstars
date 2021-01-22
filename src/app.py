import pandas as pd
import altair as alt
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import os
import dash_bootstrap_components as dbc
from vega_datasets import data


current_directory = os.path.dirname(__file__)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config["suppress_callback_exceptions"] = True
server = app.server

#reading the csv file
df = pd.read_csv(
    os.path.join(current_directory, "../data/processed/happiness_merge_all.csv")
)
#getting numeric columns to be shown in dropdown menu
numeric_columns = list(df.columns)[2:]
#getting region names to be shown in dropdown menu
region_names = list(df["Regional indicator"].unique())

def plot_1_1(country_ids=df.copy()):
    world = data.world_110m()
    world_map = alt.topo_feature(data.world_110m.url, 'countries')
    
    country_ids.dropna(subset=['id'])
    country_ids = country_ids[country_ids['Ladder score'] != "mo"].sort_values(by="Ladder score", ascending = False)
    country_ids = country_ids.reset_index(drop = True)
    country_ids['Hapiness World Rank'] = pd.Series(range(1,101))
    
    map_click = alt.selection_multi()
    chart = (
    (alt.Chart(world_map).mark_geoshape().transform_lookup(
        lookup='id',
        from_=alt.LookupData(country_ids, 'id', ['Country', 'Hapiness World Rank']))
     .encode(tooltip=['Country:N', 'Hapiness World Rank:Q'], 
             color='Hapiness World Rank:Q',
             opacity=alt.condition(map_click, alt.value(1), alt.value(0.2)))
     .add_selection(map_click)
     .project('equalEarth', scale=90))
    )
    return chart.to_html()

def plot_2_1(column_name, region="Western Europe", df=df.copy()):
    """[Creates the bar plot for the selected region and feature]

    Parameters
    ----------
    column_name : [str] 
        [selected feature]
    region : str, optional
        [the region of World], by default "Western Europe"
    df : [pandas data frame], optional
        [data frame to be used in bar plot], by default df.copy()

    Returns
    -------
    [altair chart]
        [altair chart to html]
    """
    region_df = df[df["Regional indicator"] == region]
    chart = (
        alt.Chart(region_df)
        .mark_bar(color="darkslategray")
        .encode(
            x=alt.X(column_name),
            y=alt.Y("Country", sort="-x", title=""),
        )
    )
    return chart.to_html()

def plot_1_2(region = 'Western Europe', df = df.copy()):
    """[Creates two connected altair charts, one for happiness score and other for population density for countries in selected region]

    Parameters
    ----------
    region : str, optional
        [the region of the World], by default 'Western Europe'
    df : [pandas data frame], optional
        [data frame to be used in bar plot], by default df.copy()

    Returns
    -------
    [altair chart]
        [combined altair charts with added selection by union]
    """
    region_df = df[df['Regional indicator']==region]
    sorted_df = region_df.sort_values(by=['Ladder score'])

    click = alt.selection_multi(fields = ['Country'], resolve = 'union')
    
    base = alt.Chart(sorted_df).transform_calculate(
        xmin="datum.lowerwhisker",
        xmax="datum.upperwhisker"
    ).add_selection(click)

    points = base.mark_point(shape = "diamond").encode(
        x = 'Ladder score',
        y = alt.Y('Country', sort = '-x'),
        size = alt.condition(click, alt.value(15), alt.value(2))
        )

    chart = base.mark_errorbar().encode(
        y = alt.Y('Country', sort = alt.EncodingSortField(field="Ladder score", order = "descending")),
        x = alt.X('xmin:Q', scale = alt.Scale(zero = False), title='Happiness Score'),
        x2 = 'xmax:Q',
        color = alt.condition(click, 'Country', alt.value('lightgray')),
        size = alt.condition(click, alt.value(7), alt.value(1))
        )

    error_chart = (chart + points)

    density_chart = (
        alt.Chart(region_df)
        .mark_bar()
        .encode(
            x = alt.X('Density (P/Km²)'),
            y = alt.Y('Country', sort='-x', title=""),
            color = 'Country',
            opacity = alt.condition(click, alt.value(1), alt.value(0.1)))).add_selection(click)
    
    combined_chart = (error_chart | density_chart)
    return combined_chart.to_html()


app.layout = dbc.Container([
    dbc.Row([

        dbc.Col([
            html.H1("Immigration Agency"),
            dcc.Dropdown(
                id="region",
                value="Western Europe",
                options=[{"label": name, "value": name} for name in region_names],
            ),
            dcc.Dropdown(
                id="column_name",
                value="Ladder score",
                options=[{"label": name, "value": name} for name in numeric_columns],
            )

        ]),
        dbc.Col([
            dbc.Row([
                html.Iframe(
                    id="figure_1_1",
                    style={"border-width": "0", "width": "100%", "height": "600px"},
                    srcDoc=plot_1_1(),
                )                
            ]),
            dbc.Row([
                html.Iframe(
                    id="figure_0",
                    style={"border-width": "0", "width": "100%", "height": "600px"},
                    srcDoc=plot_2_1(column_name="Ladder score", region="Western Europe"),
                )
            ])
        ]),
        dbc.Col([
            dbc.Row([
                html.Iframe(
                    id="figure_1_2",
                    style={"border-width": "0", "width": "100%", "height": "600px"},
                    srcDoc=plot_1_2(region="Western Europe"),
                )
            ])

        ])
    ])
])



@app.callback(
    Output("figure_0", "srcDoc"),
    Output("figure_1_2", "srcDoc"),
    Input("column_name", "value"),
    Input("region", "value"),
) 


def update_output(col_name, region):
    return plot_2_1(col_name, region), plot_1_2(region)


if __name__ == "__main__":
    app.run_server(debug=True)