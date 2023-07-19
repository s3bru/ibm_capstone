# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

list_launch_sites=list(spacex_df["Launch Site"].unique())
INDEX_LS_ALL=len(list_launch_sites)
launch_sites=[{'label': ls, 'value': i} for i,ls in enumerate(list_launch_sites)]+[{'label': "ALL", 'value': INDEX_LS_ALL}]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                                    options=launch_sites,
                                                     placeholder="Select a launch site",
                                                     style={'width':'80%', 'padding':'3px', 'font-size': '20px', 'text-align-last' : 'center'},
                                                     value=launch_sites[-1]['value']),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(min_payload, max_payload, 1, value=[min_payload, max_payload],id='payload-slider'),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback( Output(component_id='success-pie-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'))

# Add computation to callback function and return graph
def get_pie(index_launch_sites):
    if index_launch_sites==INDEX_LS_ALL:
        df =  spacex_df.groupby("Launch Site").agg(count_success=("class", 'sum')).reset_index()
        fig = px.pie(df, values="count_success", names="Launch Site", hole=.3,title='Number of successful launches for each launch site')
    
    else:
        name_ls=list_launch_sites[index_launch_sites]
        df=spacex_df[spacex_df["Launch Site"]==name_ls]
        df=df.groupby("class").agg(count=("class", 'count')).reset_index()
        labels={0:"Failure",1:"Sucess"}
        df["outcome"]=df["class"].map(labels)
    
        fig = px.pie(df, values="count", names="outcome", hole=.3,title=f'Number of successful / failed launches for launch site {name_ls}')


    
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback( Output(component_id='success-payload-scatter-chart', component_property='figure'),
               [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])

# Add computation to callback function and return graph
def get_scatter(index_launch_sites,payload_range):
    df =  spacex_df

    df= df[df["Payload Mass (kg)"].between(payload_range[0],payload_range[1])]

    if index_launch_sites != INDEX_LS_ALL:
        name_ls=list_launch_sites[index_launch_sites]
        df=df[df["Launch Site"]==name_ls]
              
    df =  df.groupby("Payload Mass (kg)").agg(success_rate=("class", 'mean')).reset_index()
    fig = px.scatter(
        df, x="Payload Mass (kg)", y="success_rate", title='Correlation success rate / payload'
        )


    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
