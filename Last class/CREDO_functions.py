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
  df.columns = [ 'wysokość', 'szerokość', 'szerokość_geo', 'długość_geo', 'czas', 'id_urządzenia', 'id_użytkownika', 'id_zespołu']
  df = map_id(df)
  return df

def map_id(df):
  with open('/content/CREDO/user_mapping.json') as json_file:
    users_data = json.load(json_file)

  users = users_data['users'] 
  users_map = {user['id']: user['username'] for user in users}
  df['id_użytkownika'] = df['id_użytkownika'].map(users_map)
  
  with open('/content/CREDO/team_mapping.json') as json_file:
    teams_data = json.load(json_file)
  
  teams = teams_data['teams'] 
  teams_map = {team['id']: team['name'] for team in teams}
  df['id_zespołu'] = df['id_zespołu'].map(users_map)
  return df



def particle_flux(data):
    time = 0
    surface = 0
    n = 0
    for device in data['device_id'].unique():
        size = data[data['device_id'] == device][['height', 'width']].head(1)
        surface += float(size['height'].values[0]) * float(size['width'].values[0])*10**(-10)
        time_stamps = data[data['device_id'] == device]['timestamp']
        time_stamps = time_stamps.sort_values().reset_index(drop=True)
        time_diffs = time_stamps.diff().dropna()
        time_diffs = pd.to_timedelta(time_diffs).dt.total_seconds()
        time_diffs = time_diffs[time_diffs<=300]
        n += len(time_diffs)+1
        time += time_diffs.sum()
    return n/(surface*time)

def filter_by_date(df, start_date, end_date=None):
    if end_date:
        filtered_df = df[(df['czas'].dt.date >= pd.Timestamp(start_date).date()) &
                         (df['czas'].dt.date <= pd.Timestamp(end_date).date())]
    else:
        filtered_df = df[df['czas'].dt.date == pd.Timestamp(start_date).date()]
    
    return filtered_df

def weekdays(df, weekday):
    polish_days = {
      0: 'Poniedziałek',
      1: 'Wtorek',
      2: 'Środa',
      3: 'Czwartek',
      4: 'Piątek',
      5: 'Sobota',
      6: 'Niedziela'}
    df = df[df['czas'].dt.day.isin(weekday)].copy()
    df['dzień'] = df['czas'].dt.weekday.map(polish_days)  
    return df

def months(df, month):
    polish_months = {
      1: 'Styczeń',
      2: 'Luty',
      3: 'Marzec',
      4: 'Kwiecień',
      5: 'Maj',
      6: 'Czerwiec',
      7: 'Lipiec',
      8: 'Sierpień',
      9: 'Wrzesień',
      10: 'Październik',
      11: 'Listopad',
      12: 'Grudzień'
   }
    df = df[df['czas'].dt.month.isin(month)].copy()
    df['miesiąc'] = df['czas'].dt.month.map(polish_months)  
    return df

def years(df, year):
    df = df[df['czas'].dt.year.isin(year)].copy()
    df['rok'] = df['czas'].dt.year  
    return df

def users(df, user_names):
    df = df[df['id_użytkownika'].isin(user_names)]  
    return df

def teams(df, team_names):
    df = df[df['id_zespołu'].isin(team_names)]  
    return df

def show_on_map(df):
    points = df.groupby(['szerokość_geo', 'długość_geo']).size().reset_index(name='counts')
    points['sizes'] = points['counts']/points['counts'].max() + 0.05
    points= points.drop(index=1)
    fig = px.scatter_mapbox(points, lon=points['długość'], lat=points["szerokość_geo"], color=points["counts"], size=points["sizes"], zoom=3, )
    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()

