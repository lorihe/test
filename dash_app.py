import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output
import requests

from tacticplot import plot, plot2, get_events, formation, formation2

def load_json(url):
    '''
    Load json data from the given URL.
    '''
    response = requests.get(url)
    return response.json()

# Load the URL of match data for World Cup 2023 from Statsbomb
url_WC_2023 = 'https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/72/107.json'
json_data_2023 = load_json(url_WC_2023)

# Sort stage group for user to select match
stage_dict = {}
for match in json_data_2023:
    stage_name = match['competition_stage']['name']
    match_id = str(match['match_id'])
    
    if stage_name not in stage_dict:
        stage_dict[stage_name] = []
    stage_dict[stage_name].append(match_id)

stage_dict['Group Stage'] = sorted(stage_dict['Group Stage'])

# Pair match id and match name for user to select match
match_dict = {str(match["match_id"]): 
    f"{match['home_team']['country']['name']} vs. {match['away_team']['country']['name']}"
    for match in json_data_2023}

match_dict = {key: value.replace('Korea\xa0(South)', 'South Korea') for key, value in match_dict.items()}
match_dict = {key: value.replace('United States of America', 'USA') for key, value in match_dict.items()}

# Get a full list of match ids
match_list = [str(match['match_id']) for match in json_data_2023]

# Get a dictionary with match ids as keys and a tuple of both teams in that match as value
team_dict = {match['match_id']: 
    (match['home_team']['home_team_name'], match['away_team']['away_team_name'])
    for match in json_data_2023}

# Build the app
app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR],
          meta_tags=[{"name": "viewport", "content": "width=device-width,"
                      "initial-scale=1, maximum-scale=1, maximum-scale=1"}])

app.title = "World Cup 2023 Data Visualization"

server = app.server
app.config.suppress_callback_exceptions = True

def description_card():
    '''
    :return: An HTML Div element introducing the app.
    :rtype: dash_html_components.Div
    '''
    return html.Div(
        id="description",
        children=[
            html.H5("Statsbomb Open Data Visualization",
                    style = {"font-size": "24px", "font-weight": "bold", 'color': 'dark-grey'}),
            html.Img(src=app.get_asset_url("statsbomb.png"),
                     style={"width": "60%", "height": "auto", "margin-bottom": "20px",
                            "margin-left": "18px"}),

            html.Div(
                id="intro",
                children="Great appreciation towards Statsbomb for sharing valuable data of the "
                         "Women's World Cup 2023, as part of their commitment to support women's soccer. "
                         "This project visualizes the data with an emphasis on team tactics, aiming to extend "
                         "its usage and recognition.",
                style={"font-size": "14px"}

            ),
            html.Img(src=app.get_asset_url("wc2023.jpg"),
                     style={"width": "100%", "height": "auto", "margin-top": "20px",
                            "margin-bottom": "20px"}),
        ],
    )

def game_select_card():
    '''
    :return: An HTML Div element providing accordion menu for match selection.
    :rtype: dash_html_components.Div
    '''
    return html.Div([
        dbc.Accordion(
          [
            dbc.AccordionItem(
                className= "accordion-title",
                children =
                [
                    html.Button(match_dict[match], id=match, style={'width': '46%', 'font-size': '13px',
                                                                    "margin-left": "-13px", "margin-right": "15px"},
                               className="border-0 bg-light font-weight-light my-0")
                    for match in stage_dict['Group Stage']
                ],
                title="Group Stage"
            ),
            dbc.AccordionItem(
                [
                    html.Button(match_dict[match], id=match, style={'width': '46%', 'font-size': '13px',
                                                                    "margin-left": "-13px", "margin-right": "15px"},
                               className="border-0 bg-light font-weight-light my-0")
                    for match in stage_dict['Round of 16']
                ],
                title="Round of 16"
            ),
            dbc.AccordionItem(
                [
                    html.Button(match_dict[match], id=match, style={'width': '46%', 'font-size': '13px',
                                                                    "margin-left": "-13px", "margin-right": "15px"},
                               className="border-0 bg-light font-weight-light my-0")
                    for match in stage_dict['Quarter-finals']
                ],
                title="Quarter-finals"
            ),
            dbc.AccordionItem(
                [
                    html.Button(match_dict[match], id=match, style={'width': '46%', 'font-size': '13px',
                                                                    "margin-left": "-13px", "margin-right": "15px"},
                               className="border-0 bg-light font-weight-light my-0")
                    for match in stage_dict['Semi-finals']
                ],
                title="Semi-finals"
            ),
            dbc.AccordionItem(
                [
                    html.Button(match_dict[match], id=match, style={'width': '46%', 'font-size': '13px',
                                                                    "margin-left": "-13px", "margin-right": "15px"},
                               className="border-0 bg-light font-weight-light my-0")
                    for match in stage_dict['3rd Place Final']
                ],
                title="3rd Place Final"
            ),
            dbc.AccordionItem(
                [
                    html.Button(match_dict[match], id=match, style={'width': '46%', 'font-size': '13px',
                                                                    "margin-left": "-13px", "margin-right": "15px"},
                               className="border-0 bg-light font-weight-light my-0")
                    for match in stage_dict['Final']
                ],
                title="Final"
            ),
          ], flush = True,
        ),

        html.Div(id="output-div", style={'display': 'none'}),

    ])

# App layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        # First row is the banner
        dbc.Row(
            html.Div([
                html.Div(id="banner1", className="banner ",
                         children=[
                             html.Img(src=app.get_asset_url("github.JPG"),
                                      style={"width":"auto", "height": "20px",  'margin-bottom':"5px", 'margin-left':'73px'})
                         ], style ={"display": "inline-block"}),
                html.Div(id="banner2", className="banner",
                         children=[
                             dbc.NavLink("by Lori He",
                                         href="https://github.com/lorihe/Statsbomb_open_data_utilization",
                                         style={'color': 'honeydew'})
                         ], style ={"display": "inline-block"}),
                ]
            ),
            style={"height": "32px", "background-color": "black", 'margin-bottom': '10px',
                   "z-index": "2"},
        ),

        # Second row is content
        dbc.Row([
            # First column is app description and match selection menu
            dbc.Col(
                html.Div(
                    children= [
                        html.Div(description_card(), style={"width": "90%"}),
                        html.Div(game_select_card(), style={"width": "90%"})
                    ], style = {'margin-left': '40px', 'margin-bottom': '20px'}
                ), xs={'size': 12}, sm={'size': 12}, md={'size': 12},
                   lg={'size': 3}, xl={'size': 3},
                   style = {'margin-right': '-1%'}
            ),

            # Second column shows match overview information
            dbc.Col(
                html.Div(
                    id = 'column',
                    children=[
                        html.H6('a',
                                style={'margin-left': '-19px', 'margin-right': '-110px',
                                       'color': 'RGB(180,238,180)', 'backgroundColor': 'RGB(180,238,180)'}),
                        html.H5('Match Overview',
                                style={'margin-top': '100px'}),
                        html.Div([
                            html.P('Match Date:',
                                   style={'margin-top': '30px', 'font-size': '17px', 'font-weight': 'bold'}),
                            html.P(id = 'time',
                                   style={'margin-top': '-10px', 'color':'forestgreen'}),
                            html.P('Match Result:',
                                   style={'margin-top': '20px', 'font-size': '17px', 'font-weight': 'bold'}),
                            html.P('(Regular and extra time)',
                                   style={'margin-top': '-20px', 'font-size': '16px'}),
                            html.P(id = 'team1_string',
                                   style={'margin-top': '-10px', 'color':'forestgreen'}),
                            html.P(id = 'team2_string',
                                   style={'margin-top': '-10px', 'color':'forestgreen'}),
                            html.P('Managers:',
                                   style={'margin-top': '20px', 'font-size': '17px', 'font-weight': 'bold'}),
                            html.P(id='team1_manager_string',
                                   style={'margin-top': '-10px'}),
                            html.P(id='team1_manager',
                                   style={'margin-top': '-10px', 'color': 'forestgreen'}),
                            html.P(id='team2_manager_string',
                                   style={'margin-top': '-10px'}),
                            html.P(id='team2_manager',
                                   style={'margin-top': '-10px', 'color': 'forestgreen'}),
                            ]
                        )], style = {'margin-left': '20px', 'margin-right': '8%px'}
                ),
                xs=12, sm=12, md=12, lg=2, xl = 2,
                style={"background-color":"RGB(250,247,247)", 'margin-top': '-10px',
                       'margin-right':'-5%','height': '1300px'},
            ),

            # Third column shows the plots
            dbc.Col(
                html.Div(
                    children=[
                        dbc.Spinner(children = [
                                        dcc.Graph(id="team1-plot",
                                          config={'displayModeBar': False},
                                          style= {"margin-top": "20px", "margin-left": "30px"}),
                                        dcc.Graph(id = "team1-formation",
                                                  config = {'displayModeBar': False},
                                        style= {
                                            "width": "180px", "height" : "270px",
                                            "position": "absolute",
                                            "top": "335px",
                                            "left": "945px",
                                            "z-index": "2",
                                        })
                                   ],
                                    size="lg", color="lightgreen"),

                        dbc.Spinner(children = [
                                    dcc.Graph(id="team2-plot",
                                      config={'displayModeBar': False},
                                      style= {"margin-top": "-100px", "margin-left": "30px"}),
                                    dcc.Graph(id="team2-formation",
                                      config={'displayModeBar': False},
                                      style={
                                          "width": "180px", "height": "270px",
                                          "position": "absolute",
                                          "top": "920px",
                                          "left": "945px",
                                          "z-index": "2",
                                      })
                                    ],
                                    size="lg", color="lightgreen"),

                    ], style={ "position": "relative", "width":"100%", "height":"100%", 'overflow-x':"auto"}
                ), xs=12, sm=12, md=12, lg=6, xl=6,
                style={"background-color":"RGB(250,247,247)",
                              "margin-top": "-10px", 'height': '1300px'}
            ),

            # Forth columns shows the notes
            dbc.Col(
                html.Div(
                    children=[
                        html.H6('a',
                                style={'color': 'RGB(180,238,180)', 'backgroundColor': 'RGB(180,238,180)'}),
                        html.P('Notes',
                                style={'margin-top': '10px', 'text-decoration': 'underline'}),
                        html.Div([
                            html.P('Plot direction:',
                                   style={'margin-top': '10px', 'font-size': '14px', 'font-weight': 'bold'}),
                            html.P("Plots unified the play direction of first and second half, which means on those plots "
                                   "the sides doesn't switch between the two halves.",
                                   style={ 'font-size': '14px', 'margin-top': '-15px'}),
                            html.P('Opponent carry:',
                                   style={'margin-top': '10px', 'font-size': '14px', 'font-weight': 'bold'}),
                            html.P("Indicates the start and end when an opponent player successfully carry the "
                                   "ball for more then 3.5s. Line doesn't reflect the real trajectory in between start and end.",
                                   style={'font-size': '14px', 'margin-top': '-15px'}),
                            html.P('Opponent long pass:',
                                   style={'margin-top': '10px', 'font-size': '14px', 'font-weight': 'bold'}),
                            html.P("Indicates opponent players successfully pass and receive the ball over 40 yards."
                                   " Larger circle indicates sender location, smaller circle indicates receiver location.",
                                   style={'font-size': '14px', 'margin-top': '-15px', }),
                            html.P('Shots (w/ and w/o goal):',
                                   style={'margin-top': '10px', 'font-size': '14px', 'font-weight': 'bold'}),
                            html.P("Larger dots indicate location of shots, smaller dots and line indicate recent "
                                   "ball trajectory before the shot.",
                                   style={'font-size': '14px', 'margin-top': '-15px'}),
                            html.P('Defense (success and no success):',
                                   style={'margin-top': '10px', 'font-size': '14px', 'font-weight': 'bold'}),
                            html.P("Indicates active defense actions, which were classified as 'clearance', 'duel'"
                                   " or 'interception' in Statsbomb.",
                                   style={'font-size': '14px', 'margin-top': '-15px'}),
                            html.P('Formation:',
                                   style={'margin-top': '10px', 'font-size': '14px', 'font-weight': 'bold'}),
                            html.P("Only tactical shifts which resulted with formation change were plotted. Click legends to "
                                   "turn layer on or off. Double-click turns on all layers. Double-click again isolates the selected layer.",
                                   style={'font-size': '14px', 'margin-top': '-15px'}),

                        ], style = {'width': '80%'}),
                        html.P("| The usage of this data is for non-profit educational purposes only. |",
                            style={'font-size': '13px', 'width': '80%', 'margin-top': '115%'})
                    ], style = {"background-color": "RGB(250,247,247)", 'height': '100%',
                                'margin-left':'8%','margin-right':'-80%'}
                ),
                xs=12, sm=12, md=12, lg=1, xl=1,
                style={"background-color": "RGB(250,247,247)",
                       'margin-top': '-10px',  'height': '1300px'}
            ),
        ], className="h-100 gx-0 mx-0 px-0")
    ])

# Callback 1: Input - button click from match selection memu. Output - match id.
input_matches = [Input(match, "n_clicks") for match in match_list]
@app.callback(
    Output("output-div", "children"),
    input_matches
)
def get_match(*n_clicks_values):
    clicked_match_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if not clicked_match_id:
        match_id = 3906390
    else:
        match_id = int(clicked_match_id)

    return match_id

# Callback 2: Input - match id from callback 1. Output - a bunch of strings displayed in match overview.
@app.callback(
    Output('time', 'children'),
    Output('team1_string', 'children'),
    Output('team2_string', 'children'),
    Output('team1_manager_string', 'children'),
    Output('team2_manager_string', 'children'),
    Output('team1_manager', 'children'),
    Output('team2_manager', 'children'),
    [Input("output-div", 'children')]
)
def get_info(selected_match):
    '''
    :param selected_match: match id from callback 1
    :return: a bunch of strings
    '''
    match_info = [m for m in json_data_2023 if m['match_id'] == selected_match][0]
    time = match_info['match_date']
    team1_score = match_info['home_score']
    team2_score = match_info['away_score']
    team1_manager = match_info['home_team']['managers'][0]['name']
    team2_manager = match_info['away_team']['managers'][0]['name']

    team1 = team_dict[selected_match][0]
    team2 = team_dict[selected_match][1]

    team1_name = ' '.join(team1.split()[:-1])
    team2_name = ' '.join(team2.split()[:-1])

    team1_string = f"{team1_name} score: {team1_score}"
    team2_string = f"{team2_name} score: {team2_score}"

    team1_manager_string = f"{team1_name} manager:"
    team2_manager_string = f"{team2_name} manager:"

    return (time, team1_string, team2_string, team1_manager_string, team2_manager_string,
            team1_manager, team2_manager)

# Callback 3: Input - match id from callback 1. Output - tactic plot and formation plot for both teams
@app.callback(
    Output('team1-plot', 'figure'),
    Output('team2-plot', 'figure'),
    Output('team1-formation', 'figure'),
    Output('team2-formation', 'figure'),
    [Input("output-div", 'children')]
)
def update_plot(selected_match):
    '''
    :param selected_match: match id from callback 1
    :return: A tuple containing four plot figures.
    '''
    match_id = int(selected_match)
    team1 = team_dict[match_id][0]
    team2 = team_dict[match_id][1]

    team1_name = ' '.join(team1.split()[:-1])
    team2_name = ' '.join(team2.split()[:-1])

    # Load event data from Statsbomb
    url = f'https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{match_id}.json'
    match_events = load_json(url)

    # Get tuples of team actions using imported local module
    team1_events = [event for event in match_events if event['team']['name'] == team1]
    team1_tuples = get_events(team1_events)

    team2_events = [event for event in match_events if event['team']['name'] == team2]
    team2_tuples = get_events(team2_events)

    # Generate plots using imported local module
    fig1 = plot(team1_name, team1_tuples, team2_tuples)
    fig2 = plot2(team2_name, team2_tuples, team1_tuples)

    fig3 = formation(team1_name, team1_tuples)
    fig4 = formation2(team2_name, team2_tuples)

    return fig1, fig2, fig3, fig4
    

if __name__ == '__main__':
    app.run_server(debug=True, port=1020)
