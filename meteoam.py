# -*- coding: utf-8 -*-

import collections
from datetime import datetime
from datetime import timedelta  
import json
import requests
import re

from bs4 import BeautifulSoup

class Weather:
    _from_url = {
        "coperto.png": 0,
        "coperto_foschia.png": 1,
        "coperto_nebbia.png": 2,
        "coperto_neve.png": 3,
        "coperto_pioggia.png": 4,
        "coperto_temporale.png": 5,
        "foschia.png": 6,
        "fumo.png": 7,
        "molto_nuvoloso.png": 8,
        "molto_nuvoloso_foschia.png": 9,
        "molto_nuvoloso_nebbia.png": 10,
        "molto_nuvoloso_neve.png": 11,
        "molto_nuvoloso_pioggia.png": 12,
        "molto_nuvoloso_temporale.png": 13,
        "nebbia.png": 14,
        "neve.png": 15,
        "nuvoloso.png": 16,
        "nuvoloso_foschia.png": 17,
        "nuvoloso_nebbia.png": 18,
        "nuvoloso_neve.png": 19,
        "nuvoloso_pioggia.png": 20,
        "nuvoloso_temporale.png": 21,
        "pioggia.png": 22,
        "poco_nuvoloso.png": 23,
        "poco_nuvoloso_foschia.png": 24,
        "poco_nuvoloso_nebbia.png": 25,
        "poco_nuvoloso_neve.png": 26,
        "poco_nuvoloso_pioggia.png": 27,
        "poco_nuvoloso_temporale.png": 28,
        "sabbia.png": 29,
        "sabbia_polvere.png": 30,
        "sereno.png": 31,
        "sereno_foschia.png": 32,
        "sereno_nebbia.png": 33,
        "sereno_neve.png": 34,
        "sereno_pioggia.png": 35,
        "sereno_temporale.png": 36,
        "sollevamento_neve.png": 37,
        "temporale.png": 38
    }
    w_id = -1
    def __init__(self, url):
        self.w_id = self._from_url[url.split("/")[-1]]
    
    def to_text(self):
        return ["Coperto","Coperto con foschia","Coperto con nebbia","Coperto con neve","Coperto con pioggia","Coperto con temporali","Foschia","Fumo","Molto nuvoloso","Molto nuvoloso con foschia","Molto nuvoloso con nebbia","Molto nuvoloso con neve","Molto nuvoloso con pioggia","Molto nuvoloso con temporali","Nebbia","Neve","Nuvoloso","Nuvoloso con foschia","Nuvoloso con nebbia","Nuvoloso con neve","Nuvoloso con pioggia","Nuvoloso con temporali","Pioggia","Poco nuvoloso","Poco nuvoloso con foschia","Poco nuvoloso con nebbia","Poco nuvoloso con neve","Poco nuvoloso con pioggia","Poco nuvoloso con temporali","Sabbia","Sabbia e polvere","Sereno","Sereno con foschia","Sereno con nebbia","Sereno con neve","Sereno con pioggia","Sereno con temporali","Sollevamento neve","Temporali"][self.w_id]

class Period:
    weather = None
    hour_start = 0
    hour_end = 0
    day = None

    def __init__(self, weather, day, hour_start, hour_end = None):
        self.weather = weather
        self.hour_start = hour_start
        self.hour_end = hour_end
        self.day = day

    def string(self):
        return("Dalle ore " + str(self.hour_start) + " è previsto tempo " + self.weather + "; ")

class MeteoAM:
    place_id = None
    nome = ""
    def __init__(self, place):
        if type(place) is str:
            response = requests.request("GET", "http://www.meteoam.it/ricerca_localita/autocomplete/" + place, headers={'User-Agent': 'pymeteoam'})
            localita = json.loads(response.text, object_pairs_hook=collections.OrderedDict)
            for l in list(localita.keys()):
                if(place.capitalize() == l.capitalize()):
                   self.nome = l
            response = requests.request("POST", "http://www.meteoam.it/ta/previsione/", data="ricerca_localita="+self.nome+"&form_id=ricerca_localita_form", headers={'content-type': 'application/x-www-form-urlencoded', 'User-Agent': 'pymeteoam'}, allow_redirects=False)
            self.place_id = response.headers["Location"].split('/')[-2]
        else:
            self.place_id = place

    def forecast_24h(self):
        response = requests.request("GET", "http://www.meteoam.it/sites/all/modules/custom/tempo_in_atto/highcharts/dati_temperature_giornaliero.php", data=0, params={"icao":str(self.place_id)}, headers={'User-Agent': 'pymeteoam'})
        press_cond = response.text
        response = requests.request("GET", "http://www.meteoam.it/sites/all/modules/custom/tempo_in_atto/highcharts/dati_temperature.php", data=0, params={"id":str(self.place_id)}, headers={'User-Agent': 'pymeteoam'})
        temp = response.text
        dati_meteo_grezzi = ([f+g for f,g in zip(temp.replace("\r", '').split("\n"), ["\t"+"\t".join(h.split("\t")[1:]) for h in press_cond.replace("\r", '').split("\n")])])[:-1]
        return [(lambda x: {"date": datetime.strptime(x[0], "%m/%d/%Y %H:%M"), "temperature": float(x[1]), "pressure": float(x[2]), "weather": Weather(x[3]).to_text()})(dta.split("\t")) for dta in dati_meteo_grezzi]

    def forecast_daily(self):
        dow = {"Lun": 1, "Mar": 2, "Mer": 3, "Gio": 4, "Ven": 5, "Sab": 6, "Dom": 0}
        response = requests.request("GET", "http://www.meteoam.it/widget/localita/"+str(self.place_id), headers={'User-Agent': 'pymeteoam'})
        print(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        return {
            "place": soup.find("h3").find("a").text.capitalize(), "forecast": [(lambda x: {"weekday": dow[x[0].text], "extreme_weather": x[1].find("img")["alt"] if x[1].find("img") is not None else None, "weather": x[2].find("img")["alt"], "min_t": float(x[3].text.encode("utf-8").replace("°",'')), "max_t": float(x[4].text.encode("utf-8").replace("°",'')), "wind": x[5].find(attrs={"class":"badge"})["title"]})(r.find_all("td")) for r in soup.find_all("tr")[1:]]}

    def prob_rain_today(self):
        response = requests.request("GET", "http://www.meteoam.it/ta/previsione/" + str(self.place_id), headers={'User-Agent': 'pymeteoam'})
        soup = BeautifulSoup(response.text, 'html.parser')
        temp = soup.find_all("tr")
        max_pct = 0
        last_hour = 0
        for t in temp:
            hour = re.search("[0-9][0-9]:[0-9][0-9]", str(t))
            if(hour):
               current_hour = int((hour.string[9:11]))
               #controllo che questo dato di pioggia non sia del giorno successivo
               if(last_hour > current_hour):
                  return(max_pct)
               last_hour = current_hour
            td = t.find_all("td")
            if(len(td)):
                rain = re.search("[0-9]*%", str(td[1]))
                if(rain):
                   r = int(rain.string[4:-6])
                   if(max_pct < r):
                       max_pct = r
        return(max_pct)

    def similar_condition(self, a, b):
        if(a.find("pioggia") > 0):
           return (b.find("pioggia") > 0)
        elif(a.find("temporale") > 0):
           return (b.find("temporale") > 0)
        elif(a.find("neve") > 0):
           return (b.find("neve") > 0)
        else:
           return (b.find("pioggia") < 0 and b.find("temporale") < 0 and b.find("neve") < 0)

    def alexa_today(self):
        dati = self.forecast_24h()
        temp_min = 99999
        temp_max = -99999
        periods = []
        for t in dati:
           if(datetime.now().day == t['date'].day):
              if(temp_min > t['temperature']):
                 temp_min = int(t['temperature'])
              if(temp_max < t['temperature']):
                 temp_max = int(t['temperature'])
           if(datetime.now().day == t['date'].day or (datetime.now() + timedelta(days=1)).day  == t['date'].day):
              p = Period(t['weather'], t['date'].day, t['date'].hour)
              if(len(periods) == 0):
                 periods.append(p)
              elif((periods[len(periods)-1].weather == p.weather or self.similar_condition(periods[len(periods)-1].weather, p.weather) ) and periods[len(periods)-1].day == p.day):
                 periods[len(periods)-1].hour_end = p.hour_start
              else:
                 periods[len(periods)-1].hour_end = p.hour_start
                 periods.append(p)
              #print(t)

        full_string = "A " + self.nome  + " per oggi "
        last_hour = None
        for p in periods:
           if(p != None):
              if(last_hour != None and last_hour > p.hour_start):
                 temp_string = ""
                 if(temp_min != temp_max):
                    temp_string = "La temperatura minima oggi sarà di " + str(temp_min) + " gradi, mentre quella massima sarà di " + str(temp_max) + " gradi centigradi."
                 else:
                    temp_string = "La temperatura sarà stabile intorno ai " + str(temp_min) + " gradi."
                 rain = self.prob_rain_today()
                 if(rain > 0):
                    temp_string = temp_string + " C'è il " + str(rain) + "% di possibilità di pioggia per oggi. Prendi l'ombrello!"
                 else:
                    temp_string = temp_string + " Oggi non sono previste precipitazioni, puoi lasciare l'ombrello a casa!" 
                 full_string = full_string + temp_string
                 full_string = full_string + " Per domani "
              last_hour = p.hour_start
              full_string = full_string + p.string()
        return full_string
