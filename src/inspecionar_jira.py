import pandas as pd

issues = pd.read_csv("data/raw/jira_issues.csv")
print(issues["current_status"].value_counts())
print()
print(pd.read_csv("data/raw/incidents.csv"))