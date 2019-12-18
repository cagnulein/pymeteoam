import sys
from meteoam import *

found = False

try:
   w = MeteoAM(sys.argv[1])
   print(w.alexa_today())
   found = True
except:
   if(len(sys.argv[1].split())==1):
     found = False
   else:
     for a in sys.argv[1].split():
       try:
         w = MeteoAM(a)
         print(w.alexa_today())
         found = True
         break
       except:
         found = False

if(found == False):
   print("Non ho trovato la citta' " + sys.argv[1] + ". Mi spiace.")

