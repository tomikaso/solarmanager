import plotenergy
from datetime import datetime, timezone

today = datetime.now(timezone.utc)

print (today.hour, ':', today.minute)


x = [ '00.10', '00.22', '00.38', '00.55' , '01.22', '01.38', '01.45']
y = [38, 39, 42, 41, 41, 42, 46]
#plotenergy.plot_boiler(x, y, 36,50)

#x.append(str(today.hour)+':'+str(today.minute))
#x.pop(0)
y.append(39)
y.pop(0)
#plotenergy.plot_boiler(x, y, 36, 50)

y1 = [500, 600, 550, 700, 200, 100, 460]
y2 = [1500, 1600, 2550, 3700, 2200, 1100, 2460]
y3 = [2500, 2600, 2550, 3700, 3200, 2100, 2460]
y4 = [0, 0, 100, 100, 0, 0, 0]
y5 = [100, 100, 0, 0, 100, 100, 100]

i = 0
while i < 24:
    x.append(str(round(i,0))+'.'+str(int((i-round(i,0))*60)))
    i=i+0.06
    y1.append(3000)
    y2.append(1000)
    y3.append(1000)
    y4.append(100)
    y5.append(10)
plotenergy.plot_energy(x, y1, y2, y3, y4, y5, 0,5000)