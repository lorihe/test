import requests
import plotly.graph_objects as go

import soccerfield, soccerfield2

def load_json(url):
    response = requests.get(url)
    return response.json()

# Generate position dictionary to plot formation. Refer to Statsbomb data specification.
position_dict = {1:(10, 40),
                 2:(25, 72), 3:(25, 56), 4:(25, 40), 5:(25, 24), 6:(25, 8),
                 7:(42.5, 72), 9:(42.5, 56), 10:(42.5, 40), 11:(42.5, 24), 8:(42.5, 8),
                 12:(60, 72), 13:(60, 56), 14:(60, 40), 15:(60, 24), 16:(60, 8),
                 17:(77.5, 72), 18:(77.5, 56), 19:(77.5, 40), 20:(77.5, 24), 21:(77.5, 8),
                 25:(88.75, 40), 22:(100, 56), 23:(100, 40), 24:(100, 24)}

# Set up plot colors.
goal = 'sienna'
no_goal = 'goldenrod'
carry = 'gainsboro'
defense = 'darkgreen'
defense_no = 'yellowgreen'
passes = 'RGB(26,26,26)'

def get_events(events):
    '''
    :param events: json data which contains events related to a specified team in a specified match
    :return: multiple tuples, each contains a json data for a certain action
    '''
    
    goal_events = [e for e in events if e['type']['id'] == 16 and 
            e['shot']['outcome']['name'] == 'Goal' and e['period'] != 5]
    no_goal_events = [e for e in events if e['type']['id'] == 16 and 
            e['shot']['outcome']['name'] != 'Goal' and e['period'] != 5]

    goal_seq = {}
    for e in goal_events:        
        before_goal_events = events[events.index(e)-5 : events.index(e)+1]
        before_goal_events = [e for e in before_goal_events if 'location' in e]
        goal_seq[e['index']] = before_goal_events
        
    no_goal_seq = {}
    for e in no_goal_events:
        before_no_goal_events = events[events.index(e)-4 : events.index(e)+1]
        before_no_goal_events= [e for e in before_no_goal_events if 'location' in e]
        no_goal_seq[e['index']] = before_no_goal_events    
    
    carry = [e for e in events if e['type']['id'] == 43 and e['duration'] > 3.5] 

    defense = [e for e in events if e['type']['id'] == 9 or 
                                    (e['type']['id'] == 4 and e['duel']['type']['id'] in [11, 4, 15, 16, 17]) or 
                                    (e['type']['id'] == 10 and e['interception']['outcome']['id'] in [4, 15, 16, 17])]

    defense_no = [e for e in events if (e['type']['id'] == 4 and e['duel']['type']['id'] not in [11, 4, 15, 16, 17]) or
                                       (e['type']['id'] == 10 and e['interception']['outcome']['id'] not in [4, 15, 16, 17])]

    passes_l = [e for e in events if e['type']['id'] == 30 and e['pass']['length'] > 40 and 'outcome' not in e['pass']]

    starting_XI = [e for e in events if e['type']['id'] == 35]
    tactic_shift = [e for e in events if e['type']['id'] == 36]

    return (goal_events, no_goal_events, goal_seq, no_goal_seq, carry, defense,
            defense_no, passes_l, starting_XI, tactic_shift)

def plot(team1_name, team1_tuples, team2_tuples):
    '''
    :param team1_name:
    :param team1_tuples: a tuple generated by function get_events(event) for team 1
    :param team2_tuples: a tuple generated by function get_events(event) for team 2
    :return: plot figure
    '''
    # Import soccer field layout and set up plot layout
    field_layout = soccerfield.get_layout()

    fig = go.Figure(layout=field_layout)
    fig.update_layout(title=dict(text=f'{team1_name} Tactic Plot',
                                 xanchor="left", x=0.8, y=0.89),
                      title_font=dict(family = "Roboto, sans-serif", size=18, color='forestgreen'),
                      width=1120, height=680, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=0, r=100, t=0, b=0),
                      xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=False, zeroline=False),
                      legend=dict(xanchor="left", x=1, y=0.85,
                                  font = dict(family = "Roboto, sans-serif", size = 14))
                      )

    fig.update_layout(dragmode= False)

    # Plot opponent carry events
    fig.add_trace(go.Scatter(x = [None], y = [None], legendgroup = 'carry', name = 'opponent carry (>3.5s)',
                            mode='lines', line=dict(color=carry, width = 1.8, dash = 'dashdot')))
    for e in team2_tuples[4]:
        fig.add_trace(go.Scatter(
            x = [120-e['location'][0], 120-e['carry']['end_location'][0]],
            y = [80-e['location'][1], 80-e['carry']['end_location'][1]],
            legendgroup = 'carry',
            showlegend = False,
            mode='lines',
            line=dict(color=carry, width = 1.6, dash = 'dashdot')
        ))

    # Plot opponent pass events
    fig.add_trace(go.Scatter(x = [None], y = [None], legendgroup = 'passes', name = 'opponent long pass (>40 yards)',
                        mode='lines+markers',
                        marker = dict(symbol = 'circle-open', color = passes, size = 8),
                        line=dict(color=passes, width = 0.8, dash = 'dot')))
    for e in team2_tuples[7]:
        fig.add_trace(go.Scatter(
            x = [120-e['pass']['end_location'][0]],
            y = [80-e['pass']['end_location'][1]],
            legendgroup = 'passes',
            showlegend=False,
            mode='markers', marker=dict(size=6, symbol = 'circle-open', color= passes, opacity=0.9)))
        fig.add_trace(go.Scatter(
            x = [120-e['location'][0]],
            y = [80-e['location'][1]],
            legendgroup = 'passes',
            showlegend = False,
            mode='markers', marker=dict(size=3, symbol = 'circle-open', color= passes, opacity=0.6)))
        fig.add_trace(go.Scatter(
            x = [120-e['location'][0], 120-e['pass']['end_location'][0]],
            y = [80-e['location'][1], 80-e['pass']['end_location'][1]],
            legendgroup = 'passes',
            showlegend = False,
            mode='lines',
            line=dict(color=passes, width = 0.3, dash = 'dot')
        ))

    # Plot no goal events
    fig.add_trace(go.Scatter(
        x = [e['location'][0] for e in team1_tuples[1]],
        y = [e['location'][1] for e in team1_tuples[1]],
        legendgroup = 'no goal shots',
        name = 'shots w/ no goal',
        mode='markers',
        marker=dict(size=7 , symbol = 'circle', color=no_goal)))

    # Plot goal events
    fig.add_trace(go.Scatter(
        x = [e['location'][0] for e in team1_tuples[0]],
        y = [e['location'][1] for e in team1_tuples[0]],
        legendgroup = 'goal shots',
        name = 'shots w/ goal',
        mode='markers',
        marker=dict(size=9, symbol = 'circle', color=goal)
    ))

    # Plot no goal recent trajectory events
    for key, seq in team1_tuples[3].items():
        fig.add_trace(go.Scatter(
            x = [e['location'][0] for e in seq[:-1]],
            y = [e['location'][1] for e in seq[:-1]],
            legendgroup = 'no goal shots',
            showlegend = False,
            mode='markers',
            marker=dict( size=6, symbol = 'circle', color=no_goal, opacity=0.3)
        ))        
    for key, seq in team1_tuples[3].items():
        fig.add_trace(go.Scatter(
            x=[event['location'][0] for event in seq],  
            y=[event['location'][1] for event in seq], 
            legendgroup = 'no goal shots',
            showlegend = False,
            mode='lines',
            line=dict(color=no_goal, width = 0.7)
        ))

    # Plot goal recent trajectory events
    for key, seq in team1_tuples[2].items():
        fig.add_trace(go.Scatter(
            x = [e['location'][0] for e in seq[:-1]],
            y = [e['location'][1] for e in seq[:-1]],
            legendgroup = 'goal shots',
            showlegend = False,
            mode='markers',
            marker=dict(size=6, symbol = 'circle', color=goal, opacity=0.3)
        ))        
    for key, seq in team1_tuples[2].items():
        fig.add_trace(go.Scatter(
            x=[event['location'][0] for event in seq],  
            y=[event['location'][1] for event in seq], 
            legendgroup = 'goal shots',
            showlegend = False,
            mode='lines',
            line=dict(color=goal, width = 1.2)
        ))

    # Plot defense success events
    fig.add_trace(go.Scatter(
        x = [e['location'][0] for e in team1_tuples[5]],
        y = [e['location'][1] for e in team1_tuples[5]],
        name = 'defense-success',
        mode='markers',
        marker=dict(size=6, symbol = 'diamond', color=defense, opacity=0.8)
    ))

    # Plot defense no success events
    fig.add_trace(go.Scatter(
        x = [e['location'][0] for e in team1_tuples[6]],
        y = [e['location'][1] for e in team1_tuples[6]],
        name = 'defense-no success',
        mode='markers',
        marker=dict(size=6, symbol = 'diamond', color=defense_no, opacity=0.8)
    ))
    
    return fig

def plot2(team2_name, team2_tuples, team1_tuples):
    # Made a plot2 function because I want the lower plot to rotate for 180 degree. Didn't figure out a better way to do this.
    '''
    :param team2_name:
    :param team2_tuples: a tuple generated by function get_events(event) for team 2
    :param team1_tuples: a tuple generated by function get_events(event) for team 1
    :return: plot figure
    '''
    # Import soccer field layout and set up plot layout
    field_layout = soccerfield.get_layout()

    fig = go.Figure(layout=field_layout)
    fig.update_layout(title=dict(text=f'{team2_name} Tactic Plot',
                                 xanchor="left", x=0.80, y=0.89),
                      title_font=dict(family = "Roboto, sans-serif", size=18, color='forestgreen'),
                      width=1120, height=680, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=0, r=100, t=0, b=0),
                      xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=False, zeroline=False),
                      legend=dict(x=1, y=0.85,
                                  font = dict(family = "Roboto, sans-serif", size = 14))
                      )

    fig.update_layout(dragmode=False)

    # Plot opponent carry events
    fig.add_trace(go.Scatter(x=[None], y=[None], legendgroup='carry', name='opponent carry (>3.5s)',
                             mode='lines', line=dict(color=carry, width=1.8, dash='dashdot')))
    for e in team1_tuples[4]:
        fig.add_trace(go.Scatter(
            x=[e['location'][0], e['carry']['end_location'][0]],
            y=[e['location'][1], e['carry']['end_location'][1]],
            legendgroup='carry',
            showlegend=False,
            mode='lines',
            line=dict(color=carry, width=1.6, dash='dashdot')
        ))

    # Plot opponent pass events
    fig.add_trace(go.Scatter(x=[None], y=[None], legendgroup='passes', name='opponent long pass (>40 yards)',
                             mode='lines+markers',
                             marker=dict(symbol='circle-open', color=passes, size=8),
                             line=dict(color=passes, width=0.8, dash='dot')))
    for e in team1_tuples[7]:
        fig.add_trace(go.Scatter(
            x=[e['pass']['end_location'][0]],
            y=[e['pass']['end_location'][1]],
            legendgroup='passes',
            showlegend=False,
            mode='markers', marker=dict(size=6, symbol='circle-open', color=passes, opacity=0.9)))
        fig.add_trace(go.Scatter(
            x=[e['location'][0]],
            y=[e['location'][1]],
            legendgroup='passes',
            showlegend=False,
            mode='markers', marker=dict(size=3, symbol='circle-open', color=passes, opacity=0.6)))
        fig.add_trace(go.Scatter(
            x=[e['location'][0], e['pass']['end_location'][0]],
            y=[e['location'][1], e['pass']['end_location'][1]],
            legendgroup='passes',
            showlegend=False,
            mode='lines',
            line=dict(color=passes, width=0.3, dash='dot')
        ))

    # Plot no goal events
    fig.add_trace(go.Scatter(
        x=[120-e['location'][0] for e in team2_tuples[1]],
        y=[80-e['location'][1] for e in team2_tuples[1]],
        legendgroup='no goal shots',
        name='shots w/ no goal',
        mode='markers',
        marker=dict(size=7, symbol='circle', color=no_goal)))

    # Plot goal events
    fig.add_trace(go.Scatter(
        x=[120-e['location'][0] for e in team2_tuples[0]],
        y=[80-e['location'][1] for e in team2_tuples[0]],
        legendgroup='goal shots',
        name='shots w/ goal',
        mode='markers',
        marker=dict(size=9, symbol='circle', color=goal)
    ))

    # Plot no goal recent trajectory events
    for key, seq in team2_tuples[3].items():
        fig.add_trace(go.Scatter(
            x=[120-e['location'][0] for e in seq[:-1]],
            y=[80-e['location'][1] for e in seq[:-1]],
            legendgroup='no goal shots',
            showlegend=False,
            mode='markers',
            marker=dict(size=6, symbol='circle', color=no_goal, opacity=0.3)
        ))
    for key, seq in team2_tuples[3].items():
        fig.add_trace(go.Scatter(
            x=[120-event['location'][0] for event in seq],
            y=[80-event['location'][1] for event in seq],
            legendgroup='no goal shots',
            showlegend=False,
            mode='lines',
            line=dict(color=no_goal, width=0.7)
        ))

    # Plot goal recent trajectory events
    for key, seq in team2_tuples[2].items():
        fig.add_trace(go.Scatter(
            x=[120-e['location'][0] for e in seq[:-1]],
            y=[80-e['location'][1] for e in seq[:-1]],
            legendgroup='goal shots',
            showlegend=False,
            mode='markers',
            marker=dict(size=6, symbol='circle', color=goal, opacity=0.3)
        ))
    for key, seq in team2_tuples[2].items():
        fig.add_trace(go.Scatter(
            x=[120-event['location'][0] for event in seq],
            y=[80-event['location'][1] for event in seq],
            legendgroup='goal shots',
            showlegend=False,
            mode='lines',
            line=dict(color=goal, width=1.2)
        ))

    # Plot defense success events
    fig.add_trace(go.Scatter(
        x=[120-e['location'][0] for e in team2_tuples[5]],
        y=[80-e['location'][1] for e in team2_tuples[5]],
        name='defense-success',
        mode='markers',
        marker=dict(size=6, symbol='diamond', color=defense, opacity=0.8)
    ))

    # Plot defense no success events
    fig.add_trace(go.Scatter(
        x=[120-e['location'][0] for e in team2_tuples[6]],
        y=[80-e['location'][1] for e in team2_tuples[6]],
        name='defense-no success',
        mode='markers',
        marker=dict(size=6, symbol='diamond', color=defense_no, opacity=0.8)
    ))

    return fig

def formation(team1_name, team1_tuples):
    '''
    :param team1_name:
    :param team1_tuples: a tuple generated by function get_events(event) for team 1
    :return: plot figure
    '''
    # Import soccer field layout and set up plot layout
    field_layout = soccerfield2.get_layout()

    fig = go.Figure(layout=field_layout)
    fig.update_layout(title=dict(text=f'{team1_name} Formation',
                                 yanchor="bottom", x=0.5, y=0.96),
                      title_font=dict(family="Roboto, sans-serif", size=14),
                      margin=dict(l=0, r=0, t=20, b=140),
                      xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=False, zeroline=False),
                      legend=dict(xanchor="left", yanchor="top",
                                  x=0, y=0, font=dict(family="Roboto, sans-serif", size=14)),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor='rgba(0,0,0,0)',
                      )
    fig.update_layout(dragmode=False)

    # Get starting XI position id from event tuple
    start_ids = [player['position']['id'] for player in team1_tuples[8][0]['tactics']['lineup']]
    fig.add_trace(go.Scatter(
        x = [position_dict[i][0] for i in start_ids],
        y = [position_dict[i][1] for i in start_ids],
        mode='markers',
        name = 'starting XI',
        marker=dict(size=8, symbol = 'circle', color='grey'),
    ))

    # Get tactical shift position id from event tuple
    tac_temp = start_ids
    for tac in team1_tuples[9]:
        m = tac['minute']
        s =tac['second']
        position_ids = [player['position']['id'] for player in tac['tactics']['lineup']]
        if position_ids != tac_temp :
            fig.add_trace(go.Scatter(
                x=[position_dict[i][0] for i in position_ids],
                y=[position_dict[i][1] for i in position_ids],
                mode='markers',
                name=f'tactical shift {m}:{s}',
                marker=dict(size=8, symbol='circle', color='tan'),
                visible='legendonly'
            ))
            tac_temp = position_ids
    return fig

def formation2(team2_name, team2_tuples):
    # Made a formation2 function because I want the lower plot to rotate for 180 degree. Didn't figure out a better way to do this.
    '''
    :param team2_name:
    :param team2_tuples: a tuple generated by function get_events(event) for team 2
    :return: plot figure
    '''
    # Import soccer field layout and set up plot layout
    field_layout = soccerfield2.get_layout()

    fig = go.Figure(layout=field_layout)
    fig.update_layout(title=dict(text=f'{team2_name} Formation',
                                 yanchor="bottom", x=0.5, y=0.96),
                      title_font=dict(family="Roboto, sans-serif", size=14),
                      margin=dict(l=0, r=0, t=20, b=140),
                      xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=False, zeroline=False),
                      legend=dict(xanchor="left", yanchor="top",
                                  x=0, y=0, font=dict(family="Roboto, sans-serif", size=14)),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor='rgba(0,0,0,0)',
                      )
    fig.update_layout(dragmode=False)

    start_ids = [player['position']['id'] for player in team2_tuples[8][0]['tactics']['lineup']]
    fig.add_trace(go.Scatter(
        x=[120-position_dict[i][0] for i in start_ids],
        y=[80-position_dict[i][1] for i in start_ids],
        mode='markers',
        name='starting XI',
        marker=dict(size=8, symbol='circle', color='grey'),
    ))

    tac_temp = start_ids
    for tac in team2_tuples[9]:
        m = tac['minute']
        s = tac['second']
        position_ids = [player['position']['id'] for player in tac['tactics']['lineup']]
        if position_ids != tac_temp:
            fig.add_trace(go.Scatter(
                x=[120-position_dict[i][0] for i in position_ids],
                y=[80-position_dict[i][1] for i in position_ids],
                mode='markers',
                name=f'tactical shift {m}:{s}',
                marker=dict(size=8, symbol='circle', color='tan'),
                visible='legendonly'
            ))
            tac_temp = position_ids
    return fig