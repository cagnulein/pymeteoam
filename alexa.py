import sys
from meteoam import *

found = False

today = True
tomorrow = True
rain = True
temperature = True
condition = True

try:
   if(sys.argv[1].find('oggi ') >= 0):
      today = True
      tomorrow = False
   elif(sys.argv[1].find('domani ') >= 0):
      today = False
      tomorrow = True
   if(sys.argv[1].find('temperatura ') >= 0):
      temperature = True
      rain = False
      condition = False
   if(sys.argv[1].find('piove ') >= 0):
      temperature = False
      rain = True
      condition = False

   w = MeteoAM(sys.argv[1], today, tomorrow, rain, temperature, condition)
   print(w.alexa_today())
   found = True
except:
   if(len(sys.argv[1].split())==1):
     found = False
   else:
     for a in sys.argv[1].split():
       try:
         w = MeteoAM(a, today, tomorrow, rain, temperature, condition)
         print(w.alexa_today())
         found = True
         break
       except:
         found = False

if(found == False):
   print("Non ho trovato la citta' " + sys.argv[1] + ". Mi spiace.")

