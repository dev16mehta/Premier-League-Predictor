import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load the dataset
data_url = r'C:\Users\dev16\OneDrive\Documents\pl predictor\premier-league-matches.csv'
df = pd.read_csv(data_url)

# Print the column names to check
print("Column names in the dataset:", df.columns)

# Display the first few rows of the dataset to inspect
print(df.head())

# Feature engineering: create new features such as team form, player statistics, etc.
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
df['Season'] = df['Date'].dt.year

# Create a simple feature for team form: average points in last 5 games
def calculate_team_form(df, team, date):
    past_games = df[(df['Date'] < date) & ((df['HomeTeam'] == team) | (df['AwayTeam'] == team))].tail(5)
    points = 0
    for index, game in past_games.iterrows():
        if game['HomeTeam'] == team:
            if game['FTR'] == 'H':
                points += 3
            elif game['FTR'] == 'D':
                points += 1
        else:
            if game['FTR'] == 'A':
                points += 3
            elif game['FTR'] == 'D':
                points += 1
    return points / 5

# Verify column existence before applying function
required_columns = ['HomeTeam', 'AwayTeam', 'Date', 'FTR']
for col in required_columns:
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found in the dataset")

df['HomeTeamForm'] = df.apply(lambda row: calculate_team_form(df, row['HomeTeam'], row['Date']), axis=1)
df['AwayTeamForm'] = df.apply(lambda row: calculate_team_form(df, row['AwayTeam'], row['Date']), axis=1)

# Drop rows with NaN values
df = df.dropna(subset=['HomeTeamForm', 'AwayTeamForm'])

# Encode categorical variables
le = LabelEncoder()
df['HomeTeam'] = le.fit_transform(df['HomeTeam'])
df['AwayTeam'] = le.fit_transform(df['AwayTeam'])
df['FTR'] = le.fit_transform(df['FTR'])

# Define features and target variable
features = ['HomeTeam', 'AwayTeam', 'HomeTeamForm', 'AwayTeamForm']
target = 'FTR'

X = df[features]
y = df[target]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a RandomForestClassifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate the model
y_pred = clf.predict(X_test)
print(f'Accuracy: {accuracy_score(y_test, y_pred):.2f}')

# Simulate the season
teams = df['HomeTeam'].unique()

# Initialize standings
standings = {team: 0 for team in teams}

# Simulate each match
for index, row in df.iterrows():
    home_team = row['HomeTeam']
    away_team = row['AwayTeam']
    match_features = row[features].values.reshape(1, -1)
    result = clf.predict(match_features)[0]

    if result == 0:  # Home win
        standings[home_team] += 3
    elif result == 1:  # Draw
        standings[home_team] += 1
        standings[away_team] += 1
    elif result == 2:  # Away win
        standings[away_team] += 3

# Convert standings to DataFrame for display
standings_df = pd.DataFrame(list(standings.items()), columns=['Team', 'Points'])
standings_df = standings_df.sort_values(by='Points', ascending=False)
print(standings_df)
