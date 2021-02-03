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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config["suppress_callback_exceptions"] = True
server = app.server
app.title = 'Immigration Agency'

#reading the csv file
df = pd.read_csv(
    os.path.join(current_directory, "../data/processed/happiness_merge_all.csv")
)

#getting columns as preferences to be shown in dropdown menu
preferences = ['Ladder score',
 'Logged GDP per capita',
 'Social support',
 'Healthy life expectancy',
 'Freedom to make life choices',
 'Generosity',
 'Perceptions of corruption',
 'Population (2020)',
 'Density (P/Km²)',
 'Land Area (Km²)',
 'Migrants (net)',
 'Cost of Living Index',
 'Rent Index',
 'Cost of Living Plus Rent Index',
 'Groceries Index',
 'Restaurant Price Index',
 'Local Purchasing Power Index']

#getting region names to be shown in dropdown menu
region_names = list(df["Regional indicator"].unique())
region_names.append("Top 20 Countries")

def worldmap(region = "Top 20 Countries", order = "all", country_ids=df.copy()):
    """[Create worldmap for country happiness scores]
    Parameters
    ----------
    country_ids : [pandas dataframe], optional
        [dataframe to be used in worldmap plot], by default df.copy()
    Returns
    -------
    [altair chart]
        [altair chart to html]
    """  
    world = data.world_110m()
    world_map = alt.topo_feature(data.world_110m.url, 'countries')
    country_ids.dropna(subset=['id'])
    country_ids = country_ids[country_ids['Ladder score'] != "mo"].sort_values(by="Ladder score", ascending = False)
    country_ids = country_ids.reset_index(drop = True)
    country_ids['Hapiness World Rank'] = pd.Series(range(1,101))
    if region != "Top 20 Countries" and order != "all":
        country_ids = country_ids[country_ids["Regional indicator"]==region]

    chart = (
    (alt.Chart(world_map, title="World Happiness Ranking").mark_geoshape().transform_lookup(
        lookup='id',
        from_=alt.LookupData(country_ids, 'id', ['Country', 'Hapiness World Rank']))
     .encode(tooltip=['Country:N', 'Hapiness World Rank:Q'], 
             color='Hapiness World Rank:Q'
            )
     .configure_legend(orient='bottom')
     .configure_title(fontSize=20)
     .project('equalEarth', scale=90))
    )
    return chart.to_html()

def selection_barplot(column_name, region="Top 20 Countries", order = "asc", df=df.copy()):
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
    if region == "Top 20 Countries":
        region_df = df
    else:
        region_df = df[df["Regional indicator"] == region]
    
    sorted_df_pre = region_df.sort_values(by=[column_name])
    
    if order =="asc":
        sorting = "x"
        sorted_df_pre = region_df.sort_values(by=[column_name])
    else:
        sorting = "-x"
        sorted_df_pre = region_df.sort_values(by=[column_name], ascending = False)
    
    sorted_df_pre = sorted_df_pre.head(20)
    chart = (
        alt.Chart(sorted_df_pre, title="Countries within the Region, Ranked by Your Preference")
        .mark_bar()
        .encode(
            x=alt.X(column_name),
            y=alt.Y("Country", sort=sorting, title=""),
            color=alt.Color(column_name, scale = alt.Scale(scheme='tealblues', reverse=True), legend = None),
            tooltip=column_name
        ).interactive().configure_title(fontSize=16)
    )
    return chart.to_html()

def connected_charts(region = 'Top 20 Countries', df = df.copy()):
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
    if region == "Top 20 Countries":
        region_df = df
    else:
        region_df = df[df['Regional indicator']==region]

    sorted_df = region_df.sort_values(by=['Ladder score'])
    sorted_df = sorted_df.head(20)

    click = alt.selection_multi(fields = ['Country'], resolve = 'union')
    
    base = alt.Chart(sorted_df, title="Ranked by Happiness Scores").transform_calculate(
        xmin="datum.lowerwhisker",
        xmax="datum.upperwhisker"
    ).add_selection(click)

    points = base.mark_point(shape = "diamond").encode(
        x = 'Ladder score',
        y = alt.Y('Country', sort = '-x'),
        size = alt.condition(click, alt.value(15), alt.value(2))
        ).properties(width=270)

    chart = base.mark_errorbar().encode(
        y = alt.Y('Country', title="", sort = alt.EncodingSortField(field="Ladder score", order = "descending")),
        x = alt.X('xmin:Q', scale = alt.Scale(zero = False), title='Happiness Score'),
        x2 = 'xmax:Q',
        color = alt.condition(click, 'Country', alt.value('lightturquoise'), scale = alt.Scale(scheme='tealblues'), legend = None),
        size = alt.condition(click, alt.value(7), alt.value(1))
        ).properties(width=270)

    error_chart = (chart + points)


    density_chart = (
        alt.Chart(sorted_df, title="Ranked by Population Density")
        .mark_bar()
        .encode(
            x = alt.X('Density (P/Km²)'),
            y = alt.Y('Country', sort='-x', title=""),
            color = 'Country',
            opacity = alt.condition(click, alt.value(1), alt.value(0.1)))
        .properties(width=260)    
            ).add_selection(click)
    
    combined_chart = (error_chart | density_chart)
    return combined_chart.to_html()

app.layout = dbc.Container([
    html.H1(
        children='Country Happiness Visualization',
        style={
            'textAlign': 'center',
            'color': 'white',
            'border': '1px solid #d3d3d3', 
            'border-radius': '10px',
            'background-color': 'turquoise'
        }
    ),
    html.H5(
        children="This app is designed to explore world's happiness scores and the ranking of its related matrix to help user make  country specific decisions.",
        style={
            'textAlign': 'center',
            'color': 'black'
        }
    ),    
    html.Br(),

    dbc.Row([
        dbc.Col([
            html.H6("Select a region to explore:"),
            dcc.Dropdown(
                id="region",
                value="Top 20 Countries",
                options=[{"label": name, "value": name} for name in region_names],
            ),
        ]),
        dbc.Col([
            html.H6("Select your preference to rank:"),

            dcc.Dropdown(
                id="column_name",
                value="Cost of Living Index",
                options=[{"label": name, "value": name} for name in preferences],
            )
        ])
    ], id = "topbar"),

    html.Br(),

    dbc.Row([
        dbc.Col([
            html.H6("Click on the worldmap to see happiness score index:"),
            dcc.RadioItems(
                id="order_world",
                options=[
                    {"label": "Show all countries", "value": "all"},
                    {"label": "Show filtered countries", "value": "filtered"}
                ],
                value="all",
                inputStyle={"margin-left": "50px", "margin-right": "10px"},
            ), 
            html.P("Note: Only the countries with data available are showing in world map."), 
            html.Iframe(
                id="figure_1_1", 
                style={"border-width": "0", "width": "100%", "height": "470px", "margin-left":"50px"},
                srcDoc=worldmap(),
                ),     
            ], md=6),
        dbc.Col([
            html.H6("Countries within the selected region with respect to preference:"),
            dcc.RadioItems(
                id="order_top",
                options=[
                    {"label": "Ascending", "value": "asc"},
                    {"label": "Descending", "value": "dsc"}
                ],
                value="asc",
                inputStyle={"margin-left": "100px", "margin-right": "10px"},
            ),
            html.Iframe(
                id="figure_0",
                style={"border-width": "0", "width": "200%", "height": "470px"},
                srcDoc=selection_barplot(column_name="Ladder score", region="Western Europe")
            )
        ])
        ], id = "row_1", no_gutters=True),

    dbc.Row([
        dbc.Col([
            html.H6("Country-to-Country Comparison: click on the plot to make direct comparison between countries:"),
            html.Iframe(
                id="figure_1_2",
                style={"border-width": "0", "width": "80%", "height": "500px"},
                srcDoc=connected_charts(region="Western Europe"),
                )
        ])
    ], id = "row_2")
])

@app.callback(
    Output("figure_0", "srcDoc"),
    Output("figure_1_2", "srcDoc"),
    Output("figure_1_1", "srcDoc"),
    Input("column_name", "value"),
    Input("region", "value"),
    Input("order_top", "value"),
    Input("order_world", "value")
) 
def update_output(col_name, region, order, order_world):
    return selection_barplot(col_name, region, order), connected_charts(region), worldmap(region, order_world)

if __name__ == "__main__":
    app.run_server(debug=True)