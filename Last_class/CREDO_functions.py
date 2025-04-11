import pandas as pd
import json
import plotly.express as px
import matplotlib.pyplot as plt

def read_data(file_path):
  with open(file_path) as f:
    json_data = json.load(f)
    
  detections = json_data["detections"]
  df = pd.json_normalize(detections)
  df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Europe/Warsaw')
  df = df.drop(['id','provider', 'metadata', 'source', 'visible', 'time_received', 'altitude', 'frame_content', 'x', 'y', 'accuracy'], axis=1)
  return df

def map_id(df):
  with open('/content/CREDO/user_mapping.json') as json_file:
    users_data = json.load(json_file)

  users = users_data['users'] 
  users_map = {user['id']: user['username'] for user in users}
  df['user_id'] = df['user_id'].map(users_map)
  
  with open('/content/CREDO/team_mapping.json') as json_file:
    teams_data = json.load(json_file)
  
  teams = teams_data['teams'] 
  teams_map = {team['id']: team['name'] for team in teams}
  df['team_id'] = df['team_id'].map(users_map)
  return df


def filter_by_date(df, start_date, end_date=None):
    if end_date:
        filtered_df = df[(df['timestamp'].dt.date >= pd.Timestamp(start_date).date()) &
                         (df['timestamp'].dt.date <= pd.Timestamp(end_date).date())]
    else:
        filtered_df = df[df['timestamp'].dt.date == pd.Timestamp(start_date).date()]
    
    return filtered_df

def weekdays(df, weekday):
    df = df[df['timestamp'].dt.day.isin(weekday)].copy()
    df['day'] = df['timestamp'].dt.weekday 
    return df

def months(df, month):
    df = df[df['timestamp'].dt.month.isin(month)].copy()
    df['month'] = df['timestamp'].dt.month
    return df

def years(df, year):
    df = df[df['timestamp'].dt.year.isin(year)].copy()
    df['year'] = df['timestamp'].dt.year  
    return df

def users(df, user_names):
    df = df[df['user_id'].isin(user_names)]  
    return df

def teams(df, team_names):
    df = df[df['team_id'].isin(team_names)]  
    return df

def show_on_map(df):
    points = df.groupby(['latitude', 'longitude']).size().reset_index(name='counts')
    points['sizes'] = points['counts']/points['counts'].max() + 0.05
    points= points.drop(index=1)
    fig = px.scatter_mapbox(points, lon=points['longitude'], lat=points["latitude"], color=points["counts"], size=points["sizes"], zoom=3, )
    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()

