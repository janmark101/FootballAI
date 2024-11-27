from typing import List
import pandas as pd

def load_csv(path : str, columns : List[str]) -> pd.DataFrame:
  """
  Function to laod single csv file with settings :
  Export only the necessary columns defined in arg 'columns'
  Creating additional columns :
  - HP_GAINED : Points gained so far by the home team
  - AP_GAINED : Points gained so far by the away team
  """
  data = pd.read_csv(path)
  data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y')
  data = data[columns]

  #mapping FTR to get points
  data['HomePoints'] = data['FTR'].map({"H" : 3, "D":1 ,"A":0})
  data['AwayPoints'] = data['FTR'].map({"A":3, "D":1, "H":0})
  data[['HP_GAINED','AP_GAINED']] = data.apply(lambda row : get_team_statictics(row=row, df=data,season=data['Season'],div=data['Div'], columns=['HomePoints','AwayPoints']),axis=1)
  return data
    

def get_all_last_games(team : str, date, df : pd.DataFrame, season : str, div : str) -> pd.DataFrame:
  """
  Function to get all previous matches for 'team' in specified season
  """
  return df[(df['Date'] <= date) &
          (df['Season'] == season) &
          (df['Div'] == div) &
          ((df['HomeTeam'] == team) |
          (df['AwayTeam'] == team))].sort_values(by='Date',ascending=False)


def calculate_statiscics(team : str, df : pd.DataFrame, columns : List[str]) -> int:
  """
  Calculate points gained so far by team in single season
  """
  total = 0

  total += df[df['HomeTeam'] == team][columns[0]].sum()
  total += df[df['AwayTeam'] == team][columns[1]].sum()

  return total


def get_team_statictics(row : pd.Series , df : pd.DataFrame, **kwargs) -> pd.Series:
  """
  return Series with two columns :
  Points gained so far by Home team and Away team
  """
  def team_total(team : str) -> int :
    last_games = get_all_last_games(team, row['Date'], df, kwargs['season'], kwargs['div'])
    return calculate_statiscics(team=team, df=last_games, columns=kwargs['columns'] )

  return pd.Series([team_total(row['HomeTeam']), team_total(row['AwayTeam'])])


def prev_games_(team : str, date, df : pd.DataFrame, season : str, div : str, column : str) -> pd.DataFrame:
  """
  Function to get all previous matches in specified season where : 
  If team was 'HomeTeam', get all matches were team was only 'HomeTeam'
  If team was 'AwayTeam', get all matches were team was only 'AwayTeam'
  """
  return df[(df['Date'] < date) &
          (df['Season'] == season) &
          (df['Div'] == div) &
          (df[column] == team)].sort_values(by='Date',ascending=False)


def calculate_rate(team : str, df : pd.DataFrame, condition : str) -> int:
  """
  Calculate rate of wins or draws.
  """
  if len(df) == 0:
      return None

    
  return round(df[df['FTR'] == condition]['FTR'].count() / len(df),3)


def get_team_rate(row : pd.Series , df : pd.DataFrame, **kwargs) -> pd.Series:
  """
  return Series with four columns :
  HWR -> Home win rate for HomeTeam
  HDR -> Home draw rate for HomeTeam
  AWR -> Away win rate for AwayTeam
  ADR -> Away draw rate for AwayTeam
  """
  def team_total(team : str, column : str, condition : str) -> float :
    last_games = prev_games_(team, row['Date'], df, kwargs['season'], kwargs['div'], column)
    return calculate_rate(team=team, df=last_games, condition=condition )

  return pd.Series([team_total(row['HomeTeam'], 'HomeTeam', 1), team_total(row['HomeTeam'], 'HomeTeam', 0), team_total(row['AwayTeam'], 'AwayTeam', -1), team_total(row['AwayTeam'], 'AwayTeam', 0)])


def get_last_5_games(team : str, date, df : pd.DataFrame) -> pd.DataFrame:
  """
  Function to get at leats last 4 matches for 'team'
  """
  df = df[(df['Date'] < date) &
          ((df['HomeTeam'] == team) |
          (df['AwayTeam'] == team))].sort_values(by='Date',ascending=False)


  if len(df) <= 4:
    return None

  return df.head(5)


def get_team_statictics_(row : pd.Series , df : pd.DataFrame, **kwargs) -> pd.Series:
  """
  Calculate statistics from at least 4 previos matches for Home team and Away team
  Statistics to calculate are in arg kwargs['columns']
  return Series with 2 columns
  """
  home_team = row['HomeTeam']
  away_team = row['AwayTeam']
  date = row['Date']

  home_last_games = get_last_5_games(home_team, date, df)
  away_last_games = get_last_5_games(away_team, date, df)

  if home_last_games is None or away_last_games is None:
    return pd.Series([None, None])

  total_home = calculate_statiscics(home_team, home_last_games, kwargs['columns'])
  total_away = calculate_statiscics(away_team, away_last_games, kwargs['columns'])

  return pd.Series([total_home /5,total_away /5])


def start_season(data):
  """
  Function to calculate how many days have passed since the start of the season
  """
  if data >= pd.Timestamp('2021-07-01') and data <= pd.Timestamp('2022-06-15'):
      return (data - pd.Timestamp('2021-07-01')).days
  elif data >= pd.Timestamp('2022-07-01') and data <= pd.Timestamp('2023-06-15'):
      return (data - pd.Timestamp('2022-07-01')).days
  elif data >= pd.Timestamp('2023-07-01') and data <= pd.Timestamp('2024-06-15'):
      return (data - pd.Timestamp('2023-07-01')).days
  elif data >= pd.Timestamp('2024-07-01') and data <= pd.Timestamp('2025-06-15'):
      return (data - pd.Timestamp('2024-07-01')).days
  return None
