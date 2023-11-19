#API-Key: XWX5XJW7E2Q9AGY1HOAMF2H15KZF5PLJ
# Standort 3452377


import requests

response = requests.get("https://monitoringapi.solaredge.com/site/3452377/currentPowerFlow.json?api_key=XWX5XJW7E2Q9AGY1HOAMF2H15KZF5PLJ")
print(response.status_code)
print(response.json())