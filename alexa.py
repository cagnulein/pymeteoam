import sys
from meteoam import *

try:
   w = MeteoAM(sys.argv[1])
   print(w.alexa_today())
except:
   print("Non ho trovato la citta' " + sys.argv[1] + ". Mi spiace.")
