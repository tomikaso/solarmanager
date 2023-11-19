# Kunterbunt_Solar_Manager (c) Thomas, March 2023
import time
from datetime import datetime, timezone
import os, shutil

today = datetime.now()

print (today)
print (today.weekday())
if today.weekday() > 4:
    print('Niedertarif')