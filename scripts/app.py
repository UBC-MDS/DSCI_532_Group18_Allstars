import pandas as pd
import altair as alt
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import os

current_directory = os.path.dirname(__file__)

app = dash.Dash(__name__, assets_folder='assets')
app.config['suppress_callback_exceptions'] = True
server = app.server

app.title = 'Immigration Agency'
df = pd.read_csv(os.path.join(current_directory, '../data/happiness_merge_all.csv'))
numeric_columns = list(df.columns)[2:]

def plot_altair(column_name, region = 'Western Europe' ,df = df.copy()):
    region_df = df[df['Regional indicator']==region]
    chart = alt.Chart(region_df).mark_bar(color = 'darkslategray').encode(
        x = alt.X(column_name),
        y = alt.Y('Country', sort = '-x', title = ''),
        )
    return chart.to_html()

region_names = list(df['Regional indicator'].unique())

app.layout = html.Div([
    html.H1('Immigration Agency'),
    dcc.Dropdown(
        id = 'region', value = 'Western Europe',
        options=[
            {'label': name, 'value': name} for name in region_names]),

    dcc.Dropdown(
        id = 'column_name', value = 'Ladder score',
        options=[
            {'label': name, 'value': name} for name in numeric_columns]),
    
    html.Iframe(
        id = 'figure_0',
        style={'border-width': '0', 'width': '100%', 'height': '600px'},
        srcDoc = plot_altair(column_name = 'Ladder score', region = 'Western Europe'))])

@app.callback(
    Output('figure_0', 'srcDoc'),
    Input('column_name', 'value'),
    Input('region', 'value')
)

def update_output(col_name, region):
    return plot_altair(col_name, region)

if __name__ == '__main__':
    app.run_server(debug=True)