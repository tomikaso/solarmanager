from datetime import datetime, timezone
import math

class astro:
  def __init__(self, time):
    self.latitude = 47
    self.post_winter_solistude = time.month*30+time.day-20
    self.maxdeclination = self.latitude - 22.5 * math.cos(self.post_winter_solistude/360*6.28)
    self.daylength = 12 - 4 * math.cos(self.post_winter_solistude/360*6.28)
    self.sunrise= 11.5-self.daylength/2
    self.sunset = self.sunrise + self.daylength
    self.utctime = time.hour + time.minute/60
    if self.utctime > self.sunrise and self.utctime < self.sunset:
            self.daylight = 1
    else:
        self.daylight = 0
    self.theo_power = 10600 * math.sin(self.daylight * math.sin((self.utctime-self.sunrise)*math.pi/self.daylength)*self.maxdeclination/180*math.pi)
    if time.month >=8 and time.month <11:
      self.autum_haze = 0.9 # less radiation in August - October
    else:
      self.autum_haze = 1

