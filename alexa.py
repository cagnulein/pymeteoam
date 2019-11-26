import sys
from meteoam import *

w = MeteoAM(sys.argv[1])
print(w.alexa_today())
