#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o simulador da Copa 2026 buscando os resultados reais na API-Football.
- Fonte primaria: API-Football (variavel de ambiente API_KEY).
- Rede de seguranca: resultados_reais.json (usado se a API falhar).
Saida: site/index.html  (publicado pelo GitHub Pages).
"""
import os, json, itertools, unicodedata, datetime
try:
    import requests
except Exception:
    requests = None
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Sao_Paulo")
except Exception:
    TZ = None

HERE = os.path.dirname(os.path.abspath(__file__))
# fonte de resultados: openfootball (dominio publico, sem chave) — atualizada algumas vezes ao dia
OF_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
OF_NAMES = {"Mexico":"MEX","South Africa":"RSA","South Korea":"KOR","Czech Republic":"CZE",
  "Canada":"CAN","Bosnia & Herzegovina":"BIH","Qatar":"QAT","Switzerland":"SUI",
  "Brazil":"BRA","Morocco":"MAR","Haiti":"HAI","Scotland":"SCO","USA":"USA","Paraguay":"PAR",
  "Australia":"AUS","Turkey":"TUR","Germany":"GER","Curaçao":"CUW","Ivory Coast":"CIV","Ecuador":"ECU",
  "Netherlands":"NED","Japan":"JPN","Sweden":"SWE","Tunisia":"TUN","Belgium":"BEL","Egypt":"EGY",
  "Spain":"ESP","Cape Verde":"CPV","Saudi Arabia":"KSA","Uruguay":"URU","Algeria":"ALG","Argentina":"ARG",
  "Austria":"AUT","Colombia":"COL","Croatia":"CRO","DR Congo":"COD","England":"ENG","France":"FRA",
  "Ghana":"GHA","Iran":"IRN","Iraq":"IRQ","Jordan":"JOR","New Zealand":"NZL","Norway":"NOR",
  "Panama":"PAN","Portugal":"POR","Senegal":"SEN","Uzbekistan":"UZB"}
OF_KO = {"Round of 32":"R32","Round of 16":"R16","Quarter-final":"QF","Semi-final":"SF","Final":"F"}
# arquivos extras do mesmo repo openfootball (dominio publico, sem chave)
OF_SQUADS   = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.squads.json"
OF_STADIUMS = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.stadiums.json"
OF_TEAMS    = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.teams.json"
COUNTRY = {"us":"EUA","mx":"México","ca":"Canadá"}
CFLAG   = {"us":"🇺🇸","mx":"🇲🇽","ca":"🇨🇦"}
# historico das Copas 1930-2022 (calculado uma vez, fixo) — por codigo de selecao
HIST = {"ALG":{"p":4,"t":[],"v":[],"sf":0,"j":13,"w":3,"dr":4,"l":6,"gf":12,"ga":17,"fr":1982,"bl":2},"ARG":{"p":18,"t":[1978,1986,2022],"v":[1930,1990,2014],"sf":5,"j":88,"w":44,"dr":21,"l":23,"gf":147,"ga":99,"fr":1930,"bl":5},"AUS":{"p":6,"t":[],"v":[],"sf":0,"j":20,"w":4,"dr":4,"l":12,"gf":17,"ga":37,"fr":1974,"bl":2},"AUT":{"p":7,"t":[],"v":[],"sf":2,"j":29,"w":11,"dr":5,"l":13,"gf":41,"ga":46,"fr":1934,"bl":4},"BEL":{"p":14,"t":[],"v":[],"sf":2,"j":51,"w":19,"dr":14,"l":18,"gf":64,"ga":68,"fr":1930,"bl":4},"BIH":{"p":1,"t":[],"v":[],"sf":0,"j":3,"w":1,"dr":0,"l":2,"gf":4,"ga":4,"fr":2014,"bl":0},"BRA":{"p":22,"t":[1958,1962,1970,1994,2002],"v":[1950,1998],"sf":8,"j":114,"w":75,"dr":20,"l":19,"gf":234,"ga":106,"fr":1930,"bl":5},"CAN":{"p":2,"t":[],"v":[],"sf":0,"j":6,"w":0,"dr":0,"l":6,"gf":2,"ga":12,"fr":1986,"bl":0},"CPV":{"p":0,"t":[],"v":[],"sf":0,"j":0,"w":0,"dr":0,"l":0,"gf":0,"ga":0,"fr":None,"bl":0},"COL":{"p":6,"t":[],"v":[],"sf":0,"j":22,"w":9,"dr":4,"l":9,"gf":31,"ga":28,"fr":1962,"bl":3},"CRO":{"p":6,"t":[],"v":[2018],"sf":3,"j":30,"w":12,"dr":9,"l":9,"gf":40,"ga":31,"fr":1998,"bl":5},"CUW":{"p":0,"t":[],"v":[],"sf":0,"j":0,"w":0,"dr":0,"l":0,"gf":0,"ga":0,"fr":None,"bl":0},"CZE":{"p":1,"t":[],"v":[],"sf":0,"j":3,"w":1,"dr":0,"l":2,"gf":3,"ga":4,"fr":2006,"bl":0},"COD":{"p":1,"t":[],"v":[],"sf":0,"j":3,"w":0,"dr":0,"l":3,"gf":0,"ga":14,"fr":1974,"bl":0},"ECU":{"p":4,"t":[],"v":[],"sf":0,"j":13,"w":5,"dr":2,"l":6,"gf":14,"ga":14,"fr":2002,"bl":2},"EGY":{"p":3,"t":[],"v":[],"sf":0,"j":7,"w":0,"dr":2,"l":5,"gf":5,"ga":12,"fr":1934,"bl":0},"ENG":{"p":16,"t":[1966],"v":[],"sf":3,"j":74,"w":29,"dr":27,"l":18,"gf":99,"ga":65,"fr":1950,"bl":5},"FRA":{"p":16,"t":[1998,2018],"v":[2006,2022],"sf":7,"j":73,"w":37,"dr":17,"l":19,"gf":129,"ga":80,"fr":1930,"bl":5},"GER":{"p":20,"t":[1954,1974,1990,2014],"v":[1966,1982,1986,2002],"sf":12,"j":112,"w":65,"dr":27,"l":20,"gf":224,"ga":120,"fr":1934,"bl":5},"GHA":{"p":4,"t":[],"v":[],"sf":0,"j":15,"w":4,"dr":4,"l":7,"gf":17,"ga":23,"fr":2006,"bl":3},"HAI":{"p":1,"t":[],"v":[],"sf":0,"j":3,"w":0,"dr":0,"l":3,"gf":2,"ga":14,"fr":1974,"bl":0},"IRN":{"p":6,"t":[],"v":[],"sf":0,"j":18,"w":3,"dr":4,"l":11,"gf":13,"ga":31,"fr":1978,"bl":0},"IRQ":{"p":1,"t":[],"v":[],"sf":0,"j":3,"w":0,"dr":0,"l":3,"gf":1,"ga":4,"fr":1986,"bl":0},"CIV":{"p":3,"t":[],"v":[],"sf":0,"j":9,"w":3,"dr":1,"l":5,"gf":13,"ga":14,"fr":2006,"bl":0},"JPN":{"p":7,"t":[],"v":[],"sf":0,"j":25,"w":7,"dr":6,"l":12,"gf":25,"ga":33,"fr":1998,"bl":2},"JOR":{"p":0,"t":[],"v":[],"sf":0,"j":0,"w":0,"dr":0,"l":0,"gf":0,"ga":0,"fr":None,"bl":0},"MEX":{"p":17,"t":[],"v":[],"sf":0,"j":60,"w":17,"dr":16,"l":27,"gf":62,"ga":100,"fr":1930,"bl":3},"MAR":{"p":6,"t":[],"v":[],"sf":1,"j":23,"w":5,"dr":7,"l":11,"gf":20,"ga":27,"fr":1970,"bl":4},"NED":{"p":11,"t":[],"v":[1974,1978,2010],"sf":3,"j":55,"w":30,"dr":17,"l":8,"gf":96,"ga":46,"fr":1934,"bl":5},"NZL":{"p":2,"t":[],"v":[],"sf":0,"j":6,"w":0,"dr":3,"l":3,"gf":4,"ga":14,"fr":1982,"bl":0},"NOR":{"p":3,"t":[],"v":[],"sf":0,"j":8,"w":2,"dr":4,"l":2,"gf":7,"ga":7,"fr":1938,"bl":2},"PAN":{"p":1,"t":[],"v":[],"sf":0,"j":3,"w":0,"dr":0,"l":3,"gf":2,"ga":11,"fr":2018,"bl":0},"PAR":{"p":8,"t":[],"v":[],"sf":0,"j":27,"w":7,"dr":11,"l":9,"gf":30,"ga":37,"fr":1930,"bl":3},"POR":{"p":8,"t":[],"v":[],"sf":2,"j":35,"w":17,"dr":6,"l":12,"gf":61,"ga":41,"fr":1966,"bl":4},"QAT":{"p":1,"t":[],"v":[],"sf":0,"j":3,"w":0,"dr":0,"l":3,"gf":1,"ga":7,"fr":2022,"bl":0},"KSA":{"p":6,"t":[],"v":[],"sf":0,"j":19,"w":4,"dr":2,"l":13,"gf":14,"ga":44,"fr":1994,"bl":2},"SCO":{"p":8,"t":[],"v":[],"sf":0,"j":23,"w":4,"dr":7,"l":12,"gf":25,"ga":41,"fr":1954,"bl":0},"SEN":{"p":3,"t":[],"v":[],"sf":0,"j":12,"w":4,"dr":5,"l":3,"gf":15,"ga":16,"fr":2002,"bl":3},"RSA":{"p":3,"t":[],"v":[],"sf":0,"j":9,"w":2,"dr":4,"l":3,"gf":11,"ga":16,"fr":1998,"bl":0},"KOR":{"p":11,"t":[],"v":[],"sf":1,"j":38,"w":6,"dr":11,"l":21,"gf":38,"ga":78,"fr":1954,"bl":4},"ESP":{"p":16,"t":[2010],"v":[],"sf":1,"j":67,"w":30,"dr":19,"l":18,"gf":107,"ga":74,"fr":1934,"bl":5},"SWE":{"p":12,"t":[],"v":[1958],"sf":3,"j":51,"w":19,"dr":14,"l":18,"gf":79,"ga":71,"fr":1934,"bl":5},"SUI":{"p":12,"t":[],"v":[],"sf":0,"j":41,"w":14,"dr":9,"l":18,"gf":55,"ga":72,"fr":1934,"bl":3},"TUN":{"p":6,"t":[],"v":[],"sf":0,"j":18,"w":3,"dr":5,"l":10,"gf":14,"ga":26,"fr":1978,"bl":0},"TUR":{"p":2,"t":[],"v":[],"sf":1,"j":10,"w":4,"dr":2,"l":4,"gf":19,"ga":17,"fr":1954,"bl":4},"USA":{"p":11,"t":[],"v":[],"sf":1,"j":37,"w":9,"dr":10,"l":18,"gf":39,"ga":63,"fr":1930,"bl":4},"URU":{"p":14,"t":[1930,1950],"v":[],"sf":4,"j":59,"w":24,"dr":15,"l":20,"gf":88,"ga":74,"fr":1930,"bl":5},"UZB":{"p":0,"t":[],"v":[],"sf":0,"j":0,"w":0,"dr":0,"l":0,"gf":0,"ga":0,"fr":None,"bl":0}}
# confrontos diretos em Copas 1930-2022 (fixo) — chave "CODE1-CODE2" ordenada alfabeticamente
H2H = {"FRA-MEX":[[1930,"G",4,1,""],[1954,"G",3,2,""],[1966,"G",1,1,""],[2010,"G",0,2,""]],"ARG-FRA":[[1930,"G",1,0,""],[1978,"G",2,1,""],[2018,"R16",3,4,""],[2022,"F",2,2,"4-2"]],"ARG-MEX":[[1930,"G",6,3,""],[2006,"R16",1,1,""],[2010,"R16",3,1,""],[2022,"G",2,0,""]],"BEL-USA":[[1930,"G",0,3,""],[2014,"R16",0,0,""]],"PAR-USA":[[1930,"G",0,3,""]],"BEL-PAR":[[1930,"G",0,1,""],[1986,"G",2,2,""]],"ARG-USA":[[1930,"SF",6,1,""]],"ARG-URU":[[1930,"F",2,4,""],[1986,"R16",1,0,""]],"ARG-SWE":[[1934,"G",2,3,""],[2002,"G",1,1,""]],"AUT-FRA":[[1934,"G",1,1,""],[1982,"G",0,1,""]],"BEL-GER":[[1934,"G",2,5,""],[1994,"R16",2,3,""]],"BRA-ESP":[[1934,"G",1,3,""],[1950,"G",6,1,""],[1962,"G",2,1,""],[1978,"G",0,0,""],[1986,"G",1,0,""]],"NED-SUI":[[1934,"G",2,3,""]],"GER-SWE":[[1934,"QF",2,1,""],[1958,"SF",1,3,""],[1974,"G",4,2,""],[2006,"R16",2,0,""],[2018,"G",2,1,""]],"AUT-GER":[[1934,"3P",2,3,""],[1954,"SF",1,6,""],[1978,"G",3,2,""],[1982,"G",0,1,""]],"GER-SUI":[[1938,"G",1,1,""],[1938,"G",2,4,""],[1962,"G",2,1,""],[1966,"G",5,0,""]],"BEL-FRA":[[1938,"G",1,3,""],[1986,"3P",2,2,""],[2018,"SF",0,1,""]],"BRA-SWE":[[1938,"3P",4,2,""],[1950,"G",7,1,""],[1958,"F",5,2,""],[1978,"G",1,1,""],[1990,"G",2,1,""],[1994,"G",1,1,""],[1994,"SF",1,0,""]],"BRA-MEX":[[1950,"G",4,0,""],[1954,"G",5,0,""],[1962,"G",2,0,""],[2014,"G",0,0,""],[2018,"R16",2,0,""]],"BRA-SUI":[[1950,"G",2,2,""],[2018,"G",1,1,""],[2022,"G",1,0,""]],"MEX-SUI":[[1950,"G",1,2,""]],"ESP-USA":[[1950,"G",3,1,""]],"ENG-USA":[[1950,"G",0,1,""],[2010,"G",1,1,""],[2022,"G",0,0,""]],"ENG-ESP":[[1950,"G",0,1,""],[1982,"G",0,0,""]],"PAR-SWE":[[1950,"G",2,2,""],[2006,"G",0,1,""]],"ESP-URU":[[1950,"G",2,2,""],[1990,"G",0,0,""]],"SWE-URU":[[1950,"G",2,3,""],[1970,"G",1,0,""],[1974,"G",3,0,""]],"ESP-SWE":[[1950,"G",1,3,""],[1978,"G",1,0,""]],"BRA-URU":[[1950,"G",1,2,""],[1970,"SF",3,1,""]],"GER-TUR":[[1954,"G",4,1,""],[1954,"G",7,2,""]],"KOR-TUR":[[1954,"G",0,7,""],[2002,"3P",2,3,""]],"AUT-SCO":[[1954,"G",1,0,""]],"SCO-URU":[[1954,"G",0,7,""],[1986,"G",0,0,""]],"BEL-ENG":[[1954,"G",3,3,""],[1990,"R16",0,0,""],[2018,"G",1,0,""],[2018,"3P",2,0,""]],"ENG-SUI":[[1954,"G",2,0,""]],"AUT-SUI":[[1954,"QF",7,5,""]],"ENG-URU":[[1954,"QF",2,4,""],[1966,"G",0,0,""],[2014,"G",1,2,""]],"AUT-URU":[[1954,"3P",3,1,""]],"ARG-GER":[[1958,"G",1,3,""],[1966,"G",0,0,""],[1986,"F",3,2,""],[1990,"F",0,1,""],[2006,"QF",1,1,"2-4"],[2010,"QF",0,4,""],[2014,"F",0,0,""]],"FRA-PAR":[[1958,"G",7,3,""],[1998,"R16",0,0,""]],"PAR-SCO":[[1958,"G",3,2,""]],"FRA-SCO":[[1958,"G",2,1,""]],"MEX-SWE":[[1958,"G",0,3,""],[2018,"G",0,3,""]],"AUT-BRA":[[1958,"G",0,3,""],[1978,"G",0,1,""]],"BRA-ENG":[[1958,"G",0,0,""],[1962,"QF",3,1,""],[1970,"G",1,0,""],[2002,"QF",2,1,""]],"AUT-ENG":[[1958,"G",2,2,""]],"BRA-FRA":[[1958,"SF",5,2,""],[1986,"QF",1,1,"3-4"],[1998,"F",0,3,""],[2006,"QF",0,1,""]],"FRA-GER":[[1958,"3P",6,3,""],[1982,"SF",1,1,"4-5"],[1986,"SF",0,2,""],[2014,"QF",0,1,""]],"COL-URU":[[1962,"G",1,2,""],[2014,"R16",2,0,""]],"ESP-MEX":[[1962,"G",1,0,""]],"ARG-ENG":[[1962,"G",1,3,""],[1966,"QF",0,1,""],[1986,"QF",2,1,""],[1998,"R16",2,2,"4-3"],[2002,"G",0,1,""]],"FRA-URU":[[1966,"G",1,2,""],[2002,"G",0,0,""],[2010,"G",0,0,""],[2018,"QF",2,0,""]],"ENG-MEX":[[1966,"G",2,0,""]],"MEX-URU":[[1966,"G",0,0,""],[2010,"G",0,1,""]],"ENG-FRA":[[1966,"G",2,0,""],[1982,"G",3,1,""],[2022,"QF",1,2,""]],"ARG-ESP":[[1966,"G",2,1,""]],"ESP-SUI":[[1966,"G",2,1,""],[1994,"R16",3,0,""],[2010,"G",0,1,""]],"ARG-SUI":[[1966,"G",2,0,""],[2014,"R16",0,0,""]],"ESP-GER":[[1966,"G",1,2,""],[1982,"G",1,2,""],[1994,"G",1,1,""],[2010,"SF",1,0,""],[2022,"G",1,1,""]],"BRA-POR":[[1966,"G",1,3,""],[2010,"G",0,0,""]],"GER-URU":[[1966,"QF",4,0,""],[1970,"3P",1,0,""],[1986,"G",1,1,""],[2010,"3P",3,2,""]],"ENG-POR":[[1966,"SF",2,1,""],[1986,"G",0,1,""],[2006,"QF",0,0,"1-3"]],"ENG-GER":[[1966,"F",2,2,""],[1970,"QF",2,2,""],[1982,"G",0,0,""],[1990,"SF",1,1,"3-4"],[2010,"R16",1,4,""]],"BEL-MEX":[[1970,"G",0,1,""],[1986,"G",1,2,""],[1998,"G",2,2,""]],"GER-MAR":[[1970,"G",2,1,""],[1986,"R16",1,0,""]],"AUS-GER":[[1974,"G",0,3,""],[2010,"G",0,4,""]],"COD-SCO":[[1974,"G",0,2,""]],"BRA-SCO":[[1974,"G",0,0,""],[1982,"G",4,1,""],[1990,"G",1,0,""],[1998,"G",2,1,""]],"BRA-COD":[[1974,"G",3,0,""]],"NED-URU":[[1974,"G",2,0,""],[2010,"SF",3,2,""]],"NED-SWE":[[1974,"G",0,0,""]],"ARG-HAI":[[1974,"G",4,1,""]],"ARG-NED":[[1974,"G",0,4,""],[1978,"F",1,1,""],[1998,"QF",1,2,""],[2006,"G",0,0,""],[2014,"SF",0,0,"4-2"],[2022,"QF",2,2,"4-3"]],"ARG-BRA":[[1974,"G",1,2,""],[1978,"G",0,0,""],[1982,"G",1,3,""],[1990,"R16",1,0,""]],"BRA-NED":[[1974,"G",0,2,""],[1994,"QF",3,2,""],[1998,"SF",1,1,"4-2"],[2010,"QF",1,2,""],[2014,"3P",0,3,""]],"GER-NED":[[1974,"F",2,1,""],[1978,"G",2,2,""],[1990,"R16",2,1,""]],"MEX-TUN":[[1978,"G",1,3,""]],"GER-MEX":[[1978,"G",6,0,""],[1986,"QF",0,0,"4-1"],[1998,"R16",2,1,""],[2018,"G",0,1,""]],"GER-TUN":[[1978,"G",0,0,""]],"AUT-ESP":[[1978,"G",2,1,""]],"AUT-SWE":[[1978,"G",1,0,""]],"IRN-NED":[[1978,"G",0,3,""]],"IRN-SCO":[[1978,"G",1,1,""]],"NED-SCO":[[1978,"G",2,3,""]],"AUT-NED":[[1978,"G",1,5,""]],"ALG-GER":[[1982,"G",2,1,""],[2014,"R16",0,0,""]],"ALG-AUT":[[1982,"G",0,2,""]],"ARG-BEL":[[1982,"G",0,1,""],[1986,"SF",2,0,""],[2014,"QF",1,0,""]],"NZL-SCO":[[1982,"G",2,5,""]],"BRA-NZL":[[1982,"G",4,0,""]],"ARG-KOR":[[1986,"G",3,1,""],[2010,"G",4,1,""]],"IRQ-PAR":[[1986,"G",0,1,""]],"MEX-PAR":[[1986,"G",1,1,""]],"BEL-IRQ":[[1986,"G",2,1,""]],"IRQ-MEX":[[1986,"G",0,1,""]],"CAN-FRA":[[1986,"G",0,1,""]],"ALG-BRA":[[1986,"G",0,1,""]],"ALG-ESP":[[1986,"G",0,3,""]],"GER-SCO":[[1986,"G",2,1,""]],"ENG-MAR":[[1986,"G",0,0,""]],"MAR-POR":[[1986,"G",3,1,""],[2018,"G",0,1,""],[2022,"QF",1,0,""]],"ENG-PAR":[[1986,"R16",3,0,""],[2006,"G",1,0,""]],"BEL-ESP":[[1986,"QF",1,1,"5-4"],[1990,"G",1,2,""]],"AUT-USA":[[1990,"G",2,1,""]],"SCO-SWE":[[1990,"G",2,1,""]],"COL-GER":[[1990,"G",1,1,""]],"BEL-KOR":[[1990,"G",2,0,""],[1998,"G",1,1,""],[2014,"G",1,0,""]],"BEL-URU":[[1990,"G",3,1,""]],"ESP-KOR":[[1990,"G",3,1,""],[1994,"G",2,2,""],[2002,"QF",0,0,"3-5"]],"KOR-URU":[[1990,"G",0,1,""],[2010,"R16",1,2,""],[2022,"G",0,0,""]],"EGY-NED":[[1990,"G",1,1,""]],"ENG-NED":[[1990,"G",0,0,""]],"EGY-ENG":[[1990,"G",0,1,""]],"SUI-USA":[[1994,"G",1,1,""]],"COL-USA":[[1994,"G",1,2,""]],"COL-SUI":[[1994,"G",2,0,""]],"GER-KOR":[[1994,"G",3,2,""],[2002,"SF",1,0,""],[2018,"G",0,2,""]],"MEX-NOR":[[1994,"G",0,1,""]],"BEL-MAR":[[1994,"G",1,0,""],[2022,"G",0,2,""]],"KSA-NED":[[1994,"G",1,2,""]],"BEL-NED":[[1994,"G",1,0,""],[1998,"G",0,0,""]],"KSA-MAR":[[1994,"G",2,1,""]],"MAR-NED":[[1994,"G",1,2,""]],"BEL-KSA":[[1994,"G",0,1,""]],"KSA-SWE":[[1994,"R16",1,3,""]],"BRA-USA":[[1994,"R16",1,0,""]],"MAR-NOR":[[1998,"G",2,2,""]],"NOR-SCO":[[1998,"G",1,1,""]],"BRA-MAR":[[1998,"G",3,0,""]],"MAR-SCO":[[1998,"G",3,0,""]],"BRA-NOR":[[1998,"G",1,2,""]],"FRA-RSA":[[1998,"G",3,0,""],[2010,"G",1,2,""]],"FRA-KSA":[[1998,"G",4,0,""]],"KSA-RSA":[[1998,"G",2,2,""]],"ESP-PAR":[[1998,"G",0,0,""],[2002,"G",3,1,""],[2010,"QF",1,0,""]],"KOR-MEX":[[1998,"G",1,3,""],[2018,"G",1,2,""]],"KOR-NED":[[1998,"G",0,5,""]],"MEX-NED":[[1998,"G",2,2,""],[2014,"R16",1,2,""]],"GER-USA":[[1998,"G",2,0,""],[2002,"QF",1,0,""],[2014,"G",1,0,""]],"IRN-USA":[[1998,"G",2,1,""],[2022,"G",0,1,""]],"GER-IRN":[[1998,"G",2,0,""]],"ENG-TUN":[[1998,"G",2,0,""],[2018,"G",2,1,""]],"COL-TUN":[[1998,"G",1,0,""]],"COL-ENG":[[1998,"G",0,2,""],[2018,"R16",1,1,"3-4"]],"ARG-JPN":[[1998,"G",1,0,""]],"CRO-JPN":[[1998,"G",1,0,""],[2006,"G",0,0,""],[2022,"R16",1,1,"3-1"]],"ARG-CRO":[[1998,"G",1,0,""],[2018,"G",0,3,""],[2022,"SF",3,0,""]],"CRO-GER":[[1998,"QF",3,0,""]],"CRO-FRA":[[1998,"SF",1,2,""],[2018,"F",2,4,""]],"CRO-NED":[[1998,"3P",2,1,""]],"FRA-SEN":[[2002,"G",0,1,""]],"SEN-URU":[[2002,"G",3,3,""]],"PAR-RSA":[[2002,"G",2,2,""]],"ESP-RSA":[[2002,"G",3,2,""]],"BRA-TUR":[[2002,"G",2,1,""],[2002,"SF",1,0,""]],"POR-USA":[[2002,"G",2,3,""],[2014,"G",2,2,""]],"KOR-USA":[[2002,"G",1,1,""]],"KOR-POR":[[2002,"G",1,0,""],[2022,"G",2,1,""]],"GER-KSA":[[2002,"G",8,0,""]],"ENG-SWE":[[2002,"G",1,1,""],[2006,"G",2,2,""],[2018,"QF",2,0,""]],"CRO-MEX":[[2002,"G",0,1,""],[2014,"G",1,3,""]],"ECU-MEX":[[2002,"G",1,2,""]],"CRO-ECU":[[2002,"G",0,1,""]],"BEL-JPN":[[2002,"G",2,2,""],[2018,"R16",3,2,""]],"BEL-TUN":[[2002,"G",1,1,""],[2018,"G",5,2,""]],"JPN-TUN":[[2002,"G",2,0,""]],"GER-PAR":[[2002,"R16",1,0,""]],"SEN-SWE":[[2002,"R16",1,1,""]],"MEX-USA":[[2002,"R16",0,2,""]],"BEL-BRA":[[2002,"R16",0,2,""],[2018,"QF",2,1,""]],"JPN-TUR":[[2002,"R16",0,1,""]],"SEN-TUR":[[2002,"QF",0,0,""]],"BRA-GER":[[2002,"F",2,0,""],[2014,"SF",1,7,""]],"ECU-GER":[[2006,"G",0,3,""]],"ARG-CIV":[[2006,"G",2,1,""]],"CIV-NED":[[2006,"G",1,2,""]],"IRN-MEX":[[2006,"G",1,3,""]],"IRN-POR":[[2006,"G",0,2,""],[2018,"G",1,1,""]],"MEX-POR":[[2006,"G",1,2,""]],"CZE-USA":[[2006,"G",3,0,""]],"CZE-GHA":[[2006,"G",0,2,""]],"GHA-USA":[[2006,"G",2,1,""],[2010,"R16",1,1,""],[2014,"G",1,2,""]],"BRA-CRO":[[2006,"G",1,0,""],[2014,"G",3,1,""],[2022,"QF",0,0,"2-4"]],"AUS-JPN":[[2006,"G",3,1,""]],"AUS-BRA":[[2006,"G",0,2,""]],"BRA-JPN":[[2006,"G",4,1,""]],"AUS-CRO":[[2006,"G",2,2,""]],"FRA-SUI":[[2006,"G",0,0,""],[2014,"G",5,2,""]],"FRA-KOR":[[2006,"G",1,1,""]],"KOR-SUI":[[2006,"G",0,2,""]],"KSA-TUN":[[2006,"G",2,2,""]],"ESP-TUN":[[2006,"G",3,1,""]],"ESP-KSA":[[2006,"G",1,0,""]],"ECU-ENG":[[2006,"R16",0,1,""]],"NED-POR":[[2006,"R16",0,1,""]],"BRA-GHA":[[2006,"R16",3,0,""]],"ESP-FRA":[[2006,"R16",1,3,""]],"FRA-POR":[[2006,"SF",1,0,""]],"GER-POR":[[2006,"3P",3,1,""],[2014,"G",4,0,""]],"MEX-RSA":[[2010,"G",1,1,""]],"RSA-URU":[[2010,"G",0,3,""]],"ALG-ENG":[[2010,"G",0,0,""]],"ALG-USA":[[2010,"G",0,1,""]],"AUS-GHA":[[2010,"G",1,1,""]],"GER-GHA":[[2010,"G",1,0,""],[2014,"G",2,2,""]],"JPN-NED":[[2010,"G",0,1,""]],"NZL-PAR":[[2010,"G",0,0,""]],"CIV-POR":[[2010,"G",0,0,""]],"BRA-CIV":[[2010,"G",3,1,""]],"JPN-PAR":[[2010,"R16",0,0,"3-5"]],"ESP-POR":[[2010,"R16",1,0,""],[2018,"G",3,3,""]],"GHA-URU":[[2010,"QF",1,1,"2-4"],[2022,"G",0,2,""]],"ESP-NED":[[2010,"F",0,0,""],[2014,"G",1,5,""]],"AUS-NED":[[2014,"G",2,3,""]],"AUS-ESP":[[2014,"G",0,3,""]],"CIV-JPN":[[2014,"G",2,1,""]],"CIV-COL":[[2014,"G",1,2,""]],"COL-JPN":[[2014,"G",4,1,""],[2018,"G",1,2,""]],"ECU-SUI":[[2014,"G",1,2,""]],"ECU-FRA":[[2014,"G",0,0,""]],"ARG-BIH":[[2014,"G",2,1,""]],"ARG-IRN":[[2014,"G",1,0,""]],"BIH-IRN":[[2014,"G",3,1,""]],"GHA-POR":[[2014,"G",1,2,""],[2022,"G",2,3,""]],"ALG-BEL":[[2014,"G",1,2,""]],"ALG-KOR":[[2014,"G",4,2,""]],"BRA-COL":[[2014,"QF",2,1,""]],"EGY-URU":[[2018,"G",0,1,""]],"KSA-URU":[[2018,"G",0,1,""]],"EGY-KSA":[[2018,"G",1,2,""]],"IRN-MAR":[[2018,"G",1,0,""]],"ESP-IRN":[[2018,"G",1,0,""]],"ESP-MAR":[[2018,"G",2,2,""],[2022,"R16",0,0,"0-3"]],"AUS-FRA":[[2018,"G",1,2,""],[2022,"G",1,4,""]],"KOR-SWE":[[2018,"G",0,1,""]],"BEL-PAN":[[2018,"G",3,0,""]],"ENG-PAN":[[2018,"G",6,1,""]],"PAN-TUN":[[2018,"G",1,2,""]],"JPN-SEN":[[2018,"G",2,2,""]],"COL-SEN":[[2018,"G",1,0,""]],"POR-URU":[[2018,"R16",1,2,""],[2022,"G",2,0,""]],"SUI-SWE":[[2018,"R16",0,1,""]],"CRO-ENG":[[2018,"SF",1,1,""]],"ECU-QAT":[[2022,"G",2,0,""]],"NED-SEN":[[2022,"G",2,0,""]],"QAT-SEN":[[2022,"G",1,3,""]],"ECU-NED":[[2022,"G",1,1,""]],"ECU-SEN":[[2022,"G",1,2,""]],"NED-QAT":[[2022,"G",2,0,""]],"ENG-IRN":[[2022,"G",6,2,""]],"ARG-KSA":[[2022,"G",1,2,""]],"KSA-MEX":[[2022,"G",1,2,""]],"AUS-TUN":[[2022,"G",1,0,""]],"FRA-TUN":[[2022,"G",0,1,""]],"GER-JPN":[[2022,"G",1,2,""]],"ESP-JPN":[[2022,"G",1,2,""]],"CRO-MAR":[[2022,"G",0,0,""],[2022,"3P",2,1,""]],"BEL-CAN":[[2022,"G",1,0,""]],"CAN-CRO":[[2022,"G",1,4,""]],"BEL-CRO":[[2022,"G",0,0,""]],"CAN-MAR":[[2022,"G",1,2,""]],"GHA-KOR":[[2022,"G",3,2,""]],"NED-USA":[[2022,"R16",3,1,""]],"ARG-AUS":[[2022,"R16",2,1,""]],"ENG-SEN":[[2022,"R16",3,0,""]],"BRA-KOR":[[2022,"R16",4,1,""]],"POR-SUI":[[2022,"R16",6,1,""]],"FRA-MAR":[[2022,"SF",2,0,""]]}
_DOW = ["seg","ter","qua","qui","sex","sáb","dom"]          # datetime.weekday(): 0=segunda
_MON = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
def fmt_date_pt(iso):
    try:
        y,m,d=map(int,iso.split("-")); wd=datetime.date(y,m,d).weekday()
        return f"{_DOW[wd]}, {d:02d}/{_MON[m-1]}"
    except Exception:
        return ""
def fmt_when_brt(date_iso, time_str):
    """Converte data+hora local da sede ('16:00 UTC-7') para o fuso de Brasília (UTC-3).
       Retorna (data_pt, hora_pt). Jogos noturnos nos EUA viram madrugada/dia seguinte aqui."""
    import re
    if not date_iso: return "", ""
    m=re.match(r'\s*(\d{1,2}):(\d{2})\s*UTC([+-]?\d+)', time_str or '')
    if not m:
        return fmt_date_pt(date_iso), ""        # sem horário: mostra só a data local
    hh,mm,off=int(m.group(1)),int(m.group(2)),int(m.group(3))
    y,mo,d=map(int,date_iso.split('-'))
    brt=datetime.datetime(y,mo,d,hh,mm)-datetime.timedelta(hours=off)-datetime.timedelta(hours=3)
    data=f"{_DOW[brt.weekday()]}, {brt.day:02d}/{_MON[brt.month-1]}"
    hora=f"{brt.hour}h"+(f"{brt.minute:02d}" if brt.minute else "")
    return data, hora
def parse_min(s):
    import re
    nums=re.findall(r'\d+', str(s))
    if not nums: return None
    v=int(nums[0])
    if len(nums)>1: v+=int(nums[1])   # 45+5 -> 50
    return v
def age_on(iso, ref=datetime.date(2026,6,11)):
    try:
        y,m,d=map(int,iso.split("-")); return (ref-datetime.date(y,m,d)).days/365.25
    except Exception:
        return None
def fetch_json(url):
    if requests is None: return None
    try:
        r=requests.get(url,timeout=30); r.raise_for_status(); return r.json()
    except Exception as e:
        print("[aviso] falha ao buscar", url.rsplit('/',1)[-1], ":", e); return None
def aslist(d, key):
    if isinstance(d, list): return d
    if isinstance(d, dict): return d.get(key) or d.get("data") or []
    return []

# ---------- dados estaticos ----------
F = {"ESP":92,"FRA":90,"ENG":88,"ARG":86,"POR":82,"BRA":81,"GER":78,"NED":75,"CRO":71,"NOR":70,
 "BEL":69,"COL":67,"URU":66,"MAR":65,"SEN":64,"SUI":63,"JPN":62,"MEX":61,"ECU":60,"USA":59,
 "AUT":58,"TUR":57,"ALG":56,"EGY":55,"CAN":54,"SWE":53,"IRN":52,"AUS":51,"PAR":50,"CIV":49,
 "KOR":48,"GHA":47,"SCO":46,"CZE":45,"BIH":44,"RSA":43,"KSA":42,"TUN":41,"UZB":40,"QAT":39,
 "COD":38,"NZL":37,"JOR":36,"IRQ":35,"PAN":34,"HAI":33,"CPV":32,"CUW":30}
GR = {"A":["MEX","KOR","RSA","CZE"],"B":["CAN","SUI","QAT","BIH"],"C":["BRA","MAR","SCO","HAI"],
 "D":["USA","AUS","PAR","TUR"],"E":["GER","ECU","CIV","CUW"],"F":["NED","JPN","TUN","SWE"],
 "G":["BEL","IRN","EGY","NZL"],"H":["ESP","URU","KSA","CPV"],"I":["FRA","SEN","NOR","IRQ"],
 "J":["ARG","AUT","ALG","JOR"],"K":["POR","COL","UZB","COD"],"L":["ENG","CRO","PAN","GHA"]}
NAME = {"MEX":"México","KOR":"Coreia do Sul","RSA":"África do Sul","CZE":"Tchéquia","CAN":"Canadá","SUI":"Suíça","QAT":"Catar","BIH":"Bósnia","BRA":"Brasil","MAR":"Marrocos","SCO":"Escócia","HAI":"Haiti","USA":"EUA","AUS":"Austrália","PAR":"Paraguai","TUR":"Turquia","GER":"Alemanha","ECU":"Equador","CIV":"Costa do Marfim","CUW":"Curaçao","NED":"Holanda","JPN":"Japão","TUN":"Tunísia","SWE":"Suécia","BEL":"Bélgica","IRN":"Irã","EGY":"Egito","NZL":"Nova Zelândia","ESP":"Espanha","URU":"Uruguai","KSA":"Arábia Saudita","CPV":"Cabo Verde","FRA":"França","SEN":"Senegal","NOR":"Noruega","IRQ":"Iraque","ARG":"Argentina","AUT":"Áustria","ALG":"Argélia","JOR":"Jordânia","POR":"Portugal","COL":"Colômbia","UZB":"Uzbequistão","COD":"RD Congo","ENG":"Inglaterra","CRO":"Croácia","PAN":"Panamá","GHA":"Gana"}
FLAG = {"MEX":"🇲🇽","KOR":"🇰🇷","RSA":"🇿🇦","CZE":"🇨🇿","CAN":"🇨🇦","SUI":"🇨🇭","QAT":"🇶🇦","BIH":"🇧🇦","BRA":"🇧🇷","MAR":"🇲🇦","SCO":"🏴\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f","HAI":"🇭🇹","USA":"🇺🇸","AUS":"🇦🇺","PAR":"🇵🇾","TUR":"🇹🇷","GER":"🇩🇪","ECU":"🇪🇨","CIV":"🇨🇮","CUW":"🇨🇼","NED":"🇳🇱","JPN":"🇯🇵","TUN":"🇹🇳","SWE":"🇸🇪","BEL":"🇧🇪","IRN":"🇮🇷","EGY":"🇪🇬","NZL":"🇳🇿","ESP":"🇪🇸","URU":"🇺🇾","KSA":"🇸🇦","CPV":"🇨🇻","FRA":"🇫🇷","SEN":"🇸🇳","NOR":"🇳🇴","IRQ":"🇮🇶","ARG":"🇦🇷","AUT":"🇦🇹","ALG":"🇩🇿","JOR":"🇯🇴","POR":"🇵🇹","COL":"🇨🇴","UZB":"🇺🇿","COD":"🇨🇩","ENG":"🏴\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f","CRO":"🇭🇷","PAN":"🇵🇦","GHA":"🇬🇭"}

# nomes possiveis da API -> codigo (varias variacoes; casamos por forma normalizada)
ALIASES = {
 "MEX":["Mexico"],"KOR":["South Korea","Korea Republic","Republic of Korea"],"RSA":["South Africa"],
 "CZE":["Czech Republic","Czechia"],"CAN":["Canada"],"SUI":["Switzerland"],"QAT":["Qatar"],
 "BIH":["Bosnia and Herzegovina","Bosnia & Herzegovina","Bosnia"],"BRA":["Brazil"],"MAR":["Morocco"],
 "SCO":["Scotland"],"HAI":["Haiti"],"USA":["USA","United States","United States of America"],
 "AUS":["Australia"],"PAR":["Paraguay"],"TUR":["Turkey","Turkiye","Türkiye"],"GER":["Germany"],
 "ECU":["Ecuador"],"CIV":["Ivory Coast","Cote d'Ivoire","Côte d'Ivoire"],"CUW":["Curacao","Curaçao"],
 "NED":["Netherlands","Holland"],"JPN":["Japan"],"TUN":["Tunisia"],"SWE":["Sweden"],"BEL":["Belgium"],
 "IRN":["Iran","IR Iran"],"EGY":["Egypt"],"NZL":["New Zealand"],"ESP":["Spain"],"URU":["Uruguay"],
 "KSA":["Saudi Arabia"],"CPV":["Cape Verde","Cabo Verde","Cape Verde Islands"],"FRA":["France"],
 "SEN":["Senegal"],"NOR":["Norway"],"IRQ":["Iraq"],"ARG":["Argentina"],"AUT":["Austria"],
 "ALG":["Algeria"],"JOR":["Jordan"],"POR":["Portugal"],"COL":["Colombia"],"UZB":["Uzbekistan"],
 "COD":["DR Congo","Congo DR","Democratic Republic of the Congo","Congo Democratic Republic"],
 "ENG":["England"],"CRO":["Croatia"],"PAN":["Panama"],"GHA":["Ghana"]}

def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return "".join(c for c in s.lower() if c.isalnum())

LOOKUP = {}
for code, names in ALIASES.items():
    LOOKUP[norm(NAME[code])] = code
    for n in names:
        LOOKUP[norm(n)] = code
def code_from_name(n):
    return LOOKUP.get(norm(n))

KO = {73:{"a":{"ru":"A"},"b":{"ru":"B"}},74:{"a":{"wn":"E"},"b":{"th":"E"}},75:{"a":{"wn":"F"},"b":{"ru":"C"}},76:{"a":{"wn":"C"},"b":{"ru":"F"}},77:{"a":{"wn":"I"},"b":{"th":"I"}},78:{"a":{"ru":"E"},"b":{"ru":"I"}},79:{"a":{"wn":"A"},"b":{"th":"A"}},80:{"a":{"wn":"L"},"b":{"th":"L"}},81:{"a":{"wn":"D"},"b":{"th":"D"}},82:{"a":{"wn":"G"},"b":{"th":"G"}},83:{"a":{"ru":"K"},"b":{"ru":"L"}},84:{"a":{"wn":"H"},"b":{"ru":"J"}},85:{"a":{"wn":"B"},"b":{"th":"B"}},86:{"a":{"wn":"J"},"b":{"ru":"H"}},87:{"a":{"wn":"K"},"b":{"th":"K"}},88:{"a":{"ru":"D"},"b":{"ru":"G"}},89:{"a":{"win":74},"b":{"win":77}},90:{"a":{"win":73},"b":{"win":75}},91:{"a":{"win":76},"b":{"win":78}},92:{"a":{"win":79},"b":{"win":80}},93:{"a":{"win":83},"b":{"win":84}},94:{"a":{"win":81},"b":{"win":82}},95:{"a":{"win":86},"b":{"win":88}},96:{"a":{"win":85},"b":{"win":87}},97:{"a":{"win":89},"b":{"win":90}},98:{"a":{"win":93},"b":{"win":94}},99:{"a":{"win":91},"b":{"win":92}},100:{"a":{"win":95},"b":{"win":96}},101:{"a":{"win":97},"b":{"win":98}},102:{"a":{"win":99},"b":{"win":100}},103:{"a":{"lose":101},"b":{"lose":102}},104:{"a":{"win":101},"b":{"win":102}}}
KO_IDS = sorted(KO)

def pred_score(a,b):
    d=abs(F[a]-F[b]); hi,lo=(a,b) if F[a]>=F[b] else (b,a)
    s=(3,0) if d>=25 else (2,0) if d>=18 else (2,1) if d>=11 else (1,0)
    return hi,lo,s

# ---- palpite original do mata-mata (pre-computado) e fase de cada jogo ----
def phase_of(i):
    if i<=88: return "R32"
    if i<=96: return "R16"
    if i<=100: return "QF"
    if i<=102: return "SF"
    if i==103: return "3P"
    return "F"
def original_phases(alloc_map):
    pg={}
    for g,ts in GR.items():
        st={t:{"P":0,"GF":0,"GA":0} for t in ts}
        for a,b in itertools.combinations(ts,2):
            hi,lo,s=pred_score(a,b)
            gh=s[0] if hi==a else s[1]; ga=s[0] if hi==b else s[1]
            st[a]["GF"]+=gh;st[a]["GA"]+=ga;st[b]["GF"]+=ga;st[b]["GA"]+=gh
            if gh>ga: st[a]["P"]+=3
            elif gh<ga: st[b]["P"]+=3
            else: st[a]["P"]+=1;st[b]["P"]+=1
        order=sorted(ts,key=lambda t:(-st[t]["P"],-(st[t]["GF"]-st[t]["GA"]),-st[t]["GF"],-F[t]))
        pg[g]=(order,st)
    thirds=[]
    for g in GR:
        t=pg[g][0][2]; s=pg[g][1][t]
        thirds.append((g,s["P"],s["GF"]-s["GA"],s["GF"],t))
    thirds.sort(key=lambda x:(-x[1],-x[2],-x[3],-F[x[4]]))
    top8="".join(sorted(x[0] for x in thirds[:8]))
    alloc=alloc_map.get(top8)
    posp=lambda g,rk: pg[g][0][rk-1]
    RESp={}
    def slot(spec):
        if "wn" in spec: return posp(spec["wn"],1)
        if "ru" in spec: return posp(spec["ru"],2)
        if "th" in spec:
            if not alloc: return None
            g=alloc.get(spec["th"]); return posp(g,3) if g else None
        if "win" in spec: r=RESp.get(spec["win"]); return r["w"] if r else None
        if "lose" in spec: r=RESp.get(spec["lose"]); return (r["b"] if r["a"]==r["w"] else r["a"]) if r else None
        return None
    phases={"R32":[],"R16":[],"QF":[],"SF":[],"F":[],"CH":[]}
    for i in sorted(KO):
        a=slot(KO[i]["a"]); b=slot(KO[i]["b"])
        w = b if not a else a if not b else (a if F[a]>=F[b] else b)
        RESp[i]={"a":a,"b":b,"w":w}
        ph=phase_of(i)
        if ph in phases:
            if a: phases[ph].append(a)
            if b: phases[ph].append(b)
        if i==104 and w: phases["CH"].append(w)
    return phases

# fase do mata-mata a partir do texto "round" da API (defensivo)
def ko_phase(round_str):
    r=(round_str or "").lower()
    if "group" in r: return None
    if "32" in r: return "R32"
    if "16" in r: return "R16"
    if "quart" in r: return "QF"
    if "semi" in r: return "SF"
    if "3rd" in r or "third" in r or "place" in r: return "3P"
    if "final" in r: return "F"
    return None

# matchday (rodada) por confronto — preenchido pela API; no seed, tudo rodada 1
ROUNDS={}
KO_REAL=[]   # jogos reais do mata-mata: {"ph","h","a","gh","ga","w"}
GOALS=[]     # gols dos jogos encerrados: {"c"(code),"who","min"(int),"pen","og"}
META_GRP={}  # frozenset({c1,c2}) -> {"dt"(iso),"gr"(cidade)}  (todos os 72 jogos de grupo)
META_KO={}   # num(73..104) -> {"dt"(iso),"gr"(cidade)}        (todos os 32 do mata-mata)
def parse_round(s):
    import re
    m=re.search(r'(\d+)', s or '')
    return int(m.group(1)) if m else None

# ---------- fontes de resultado ----------
# rede de seguranca: usada SO se a API falhar (1a rodada, grupos A-D)
SEED = {("MEX","RSA"):(2,0),("KOR","CZE"):(2,1),("QAT","SUI"):(1,1),("CAN","BIH"):(1,1),
        ("BRA","MAR"):(1,1),("HAI","SCO"):(0,1),("USA","PAR"):(4,1),("AUS","TUR"):(2,0)}
def load_seed():
    for k in SEED: ROUNDS.setdefault(k,1)   # os 8 jogos do seed sao da rodada 1
    return dict(SEED)

def fetch_results():
    if requests is None:
        print("[aviso] sem 'requests' — usando seed local"); return {}
    try:
        r=requests.get(OF_URL, timeout=30); r.raise_for_status(); data=r.json()
    except Exception as e:
        print("[aviso] falha ao buscar openfootball:", e, "— usando seed"); return {}
    out={}; grp_games=[]; ko_n=0; bad=set()
    for m in data.get("matches", []):
        date=m.get("date",""); ground=m.get("ground","")
        grp=(m.get("group") or "")
        t1=OF_NAMES.get((m.get("team1") or "").strip())
        t2=OF_NAMES.get((m.get("team2") or "").strip())
        # --- metadados de sede/data de TODOS os jogos (mesmo os ainda não jogados) ---
        if grp.startswith("Group") and t1 and t2:
            META_GRP[frozenset((t1,t2))]={"dt":date,"tm":m.get("time",""),"gr":ground}
        elif m.get("num"):
            META_KO[int(m["num"])]={"dt":date,"tm":m.get("time",""),"gr":ground}
        # --- placar e gols só dos jogos encerrados ---
        ft=(m.get("score") or {}).get("ft")
        if not ft: continue
        if not t1 or not t2:                          # placeholders (1A, W73...) ou nome novo
            n1,n2=m.get("team1",""),m.get("team2","")
            if n1 and n2 and not any(c.isdigit() for c in n1+n2) and "/" not in n1+n2:
                bad.add((n1,n2))
            continue
        for side,code in ((m.get("goals1"),t1),(m.get("goals2"),t2)):
            for gg in (side or []):
                GOALS.append({"c":code,"who":gg.get("name",""),"min":parse_min(gg.get("minute","")),
                              "pen":bool(gg.get("penalty")),"og":bool(gg.get("owngoal")),"g":f"{t1}-{t2}"})
        if grp.startswith("Group"):
            out[(t1,t2)]=(int(ft[0]),int(ft[1]))
            grp_games.append((grp,date,m.get("time",""),t1,t2))
        else:
            ph=OF_KO.get((m.get("round") or "").strip())
            if not ph: continue                       # 3o lugar ou rodada desconhecida
            w = t1 if ft[0]>ft[1] else t2 if ft[1]>ft[0] else None
            KO_REAL.append({"ph":ph,"h":t1,"a":t2,"gh":int(ft[0]),"ga":int(ft[1]),"w":w}); ko_n+=1
    # rodada do grupo = ordem cronologica dos jogos JA encerrados de cada grupo (2 por rodada)
    from collections import defaultdict
    bg=defaultdict(list)
    for g,date,time,t1,t2 in grp_games: bg[g].append((date,time,t1,t2))
    for g,lst in bg.items():
        lst.sort()
        for i,(d,t,t1,t2) in enumerate(lst): ROUNDS[(t1,t2)] = i//2 + 1
    if bad: print("[aviso] selecoes nao reconhecidas (ajustar OF_NAMES):", sorted(bad))
    print(f"[ok] openfootball: {len(out)} jogos de grupo + {ko_n} de mata-mata; {len(GOALS)} gols")
    return out

# ---------- curiosidades (pre-computadas no Python; o HTML so exibe) ----------
def venue_of(city, sbc):
    s=sbc.get(city)
    if not s: return {"vn":city,"cc":"","co":"","cap":None}
    cc=s.get("cc","")
    return {"vn":s.get("name",city),"cc":cc,"co":COUNTRY.get(cc,""),"cap":s.get("capacity")}

def compute_curios(games, squads, stadiums, teams):
    from collections import Counter, defaultdict
    flag=lambda c: FLAG.get(c,""); nm=lambda c: NAME.get(c,c)
    tpt=lambda e: NAME.get(OF_NAMES.get((e or '').strip(),''), e)   # nome ingles do squad -> pt
    fpt=lambda e: FLAG.get(OF_NAMES.get((e or '').strip(),''),"")
    realg=[g for g in games if g["r"]]
    C={"games_real":len(realg),"hero":[],"sections":[]}

    # ===== GOLS & JOGOS =====
    gi=[]
    if GOALS:
        sc=Counter(g["who"] for g in GOALS if g["who"] and not g["og"])
        tof={}
        for g in GOALS:
            if g["who"] and not g["og"]: tof.setdefault(g["who"],g["c"])
        top=sc.most_common(6)
        if top:
            gi.append({"ico":"👟","label":"Artilheiros","rows":[{"n":w,"v":str(n),"s":flag(tof.get(w,''))+" "+nm(tof.get(w,''))} for w,n in top]})
            C["hero"].append({"ico":"👟","label":"Artilheiro","value":top[0][0],"detail":f"{top[0][1]} gol(s) · {flag(tof.get(top[0][0],''))} {nm(tof.get(top[0][0],''))}"})
        perpg=defaultdict(Counter)
        for g in GOALS:
            if g["who"] and not g["og"]: perpg[g["g"]][g["who"]]+=1
        hats=[(w,n) for _,cc in perpg.items() for w,n in cc.items() if n>=3]
        gi.append({"ico":"🎩","label":"Hat-tricks","rows":[{"n":w,"v":f"{n} gols","s":flag(tof.get(w,''))+" "+nm(tof.get(w,''))} for w,n in hats]} if hats else {"ico":"🎩","label":"Hat-tricks","value":"nenhum ainda"})
        pens=[g for g in GOALS if g["pen"]]
        if pens: gi.append({"ico":"🎯","label":"Gols de pênalti","value":str(len(pens)),"detail":", ".join(g["who"] for g in pens[:5])})
        ogs=[g for g in GOALS if g["og"]]
        if ogs: gi.append({"ico":"🙃","label":"Gols contra","rows":[{"n":g["who"],"v":"contra","s":flag(g["c"])+" "+nm(g["c"])} for g in ogs]})
        timed=[g for g in GOALS if g["min"] is not None]
        if timed:
            fa=min(timed,key=lambda g:g["min"]); la=max(timed,key=lambda g:g["min"])
            gi.append({"ico":"⚡","label":"Gol mais rápido","value":f"{fa['min']}'","detail":f"{fa['who']} · {flag(fa['c'])} {nm(fa['c'])}"})
            gi.append({"ico":"🕘","label":"Gol mais tardio","value":f"{la['min']}'","detail":f"{la['who']} · {flag(la['c'])} {nm(la['c'])}"})
            h1=sum(1 for g in timed if g["min"]<=45)
            gi.append({"ico":"⏱️","label":"Gols por tempo","value":f"{h1} no 1ºT · {len(timed)-h1} no 2ºT"})
    if realg:
        bigd=max(realg,key=lambda m:abs(m["gh"]-m["ga"])); most=max(realg,key=lambda m:m["gh"]+m["ga"])
        gi.append({"ico":"💥","label":"Maior goleada","value":f"{max(bigd['gh'],bigd['ga'])}–{min(bigd['gh'],bigd['ga'])}","detail":f"{flag(bigd['h'])} {nm(bigd['h'])} x {nm(bigd['a'])} {flag(bigd['a'])}"})
        C["hero"].append({"ico":"💥","label":"Maior goleada","value":f"{max(bigd['gh'],bigd['ga'])}–{min(bigd['gh'],bigd['ga'])}","detail":f"{nm(bigd['h'])} x {nm(bigd['a'])}"})
        gi.append({"ico":"🥅","label":"Jogo com mais gols","value":f"{most['gh']+most['ga']} gols","detail":f"{flag(most['h'])} {nm(most['h'])} {most['gh']}–{most['ga']} {nm(most['a'])} {flag(most['a'])}"})
        gf=Counter(); gax=Counter()
        for m in realg: gf[m["h"]]+=m["gh"]; gf[m["a"]]+=m["ga"]; gax[m["h"]]+=m["ga"]; gax[m["a"]]+=m["gh"]
        if gf:
            mk=gf.most_common(1)[0]; ms=gax.most_common(1)[0]
            gi.append({"ico":"🔥","label":"Ataque mais positivo","value":f"{mk[1]} gols","detail":f"{flag(mk[0])} {nm(mk[0])}"})
            gi.append({"ico":"🧤","label":"Defesa mais vazada","value":f"{ms[1]} sofridos","detail":f"{flag(ms[0])} {nm(ms[0])}"})
        pc=Counter((max(m["gh"],m["ga"]),min(m["gh"],m["ga"])) for m in realg).most_common(1)[0]
        gi.append({"ico":"📊","label":"Placar mais comum","value":f"{pc[0][0]}–{pc[0][1]}","detail":f"{pc[1]}x até agora"})
        dr=sum(1 for m in realg if m["gh"]==m["ga"])
        gi.append({"ico":"🤝","label":"Empates","value":f"{dr} de {len(realg)}","detail":f"{round(100*dr/len(realg))}% dos jogos"})
        tot=sum(m["gh"]+m["ga"] for m in realg)
        gi.append({"ico":"📈","label":"Média de gols","value":f"{tot/len(realg):.2f}/jogo","detail":f"{tot} gols em {len(realg)} jogos"})
    if gi:
        C["sections"].append({"ico":"⚽","title":"Gols & Jogos","note":f"baseado em {len(realg)} jogo(s) já disputado(s)","items":gi})

    # ===== ELENCOS =====
    if squads:
        pls=[]
        for t in squads:
            for p in t.get("players",[]):
                p2=dict(p); p2["_t"]=t.get("name",""); pls.append(p2)
        ei=[]
        ages=[(age_on(p.get("date_of_birth","")),p) for p in pls]; ages=[(a,p) for a,p in ages if a]
        if ages:
            ages.sort(key=lambda x:x[0]); yo=ages[0]; ol=ages[-1]
            C["hero"].append({"ico":"👶","label":"Mais novo da Copa","value":f"{yo[0]:.0f} anos","detail":f"{yo[1]['name']} · {fpt(yo[1]['_t'])} {tpt(yo[1]['_t'])}"})
            C["hero"].append({"ico":"🧓","label":"Mais veterano","value":f"{ol[0]:.0f} anos","detail":f"{ol[1]['name']} · {fpt(ol[1]['_t'])} {tpt(ol[1]['_t'])}"})
            ei.append({"ico":"👶","label":"Jogador mais novo","value":f"{yo[1]['name']} ({yo[0]:.0f})","detail":f"{fpt(yo[1]['_t'])} {tpt(yo[1]['_t'])}"})
            ei.append({"ico":"🧓","label":"Jogador mais veterano","value":f"{ol[1]['name']} ({ol[0]:.0f})","detail":f"{fpt(ol[1]['_t'])} {tpt(ol[1]['_t'])}"})
            byteam=defaultdict(list)
            for a,p in ages: byteam[p["_t"]].append(a)
            avg=sorted((sum(v)/len(v),t) for t,v in byteam.items() if len(v)>=11)
            if avg:
                yt=avg[0]; ot=avg[-1]
                ei.append({"ico":"🐣","label":"Elenco mais jovem","value":f"{fpt(yt[1])} {tpt(yt[1])}","detail":f"média {yt[0]:.1f} anos"})
                ei.append({"ico":"🦉","label":"Elenco mais veterano","value":f"{fpt(ot[1])} {tpt(ot[1])}","detail":f"média {ot[0]:.1f} anos"})
        clubs=Counter(p["club"]["name"] for p in pls if p.get("club"))
        if clubs: ei.append({"ico":"🏟️","label":"Clube que mais cede jogadores","rows":[{"n":c,"v":str(n),"s":""} for c,n in clubs.most_common(5)]})
        ccs=Counter(p["club"]["country"] for p in pls if p.get("club") and p["club"].get("country"))
        LCC={"ENG":"Inglaterra","GER":"Alemanha","ESP":"Espanha","ITA":"Itália","FRA":"França","NED":"Holanda","POR":"Portugal","USA":"EUA","SAU":"Ar. Saudita","TUR":"Turquia","MEX":"México","BEL":"Bélgica","BRA":"Brasil","SCO":"Escócia","KSA":"Ar. Saudita"}
        if ccs: ei.append({"ico":"🌐","label":"Onde os convocados atuam","rows":[{"n":LCC.get(c,c),"v":str(n),"s":"jogadores"} for c,n in ccs.most_common(5)]})
        pos=Counter(p.get("pos") for p in pls); POSN=[("GK","goleiros"),("DF","zagueiros"),("MF","meias"),("FW","atacantes")]
        if pos: ei.append({"ico":"📋","label":"Por posição","value":" · ".join(f"{pos.get(k,0)} {v}" for k,v in POSN)})
        ei.append({"ico":"👥","label":"Total de convocados","value":str(len(pls)),"detail":f"{len(squads)} seleções"})
        if ei: C["sections"].append({"ico":"👥","title":"Elencos","items":ei})

    # ===== SEDES =====
    if stadiums:
        si=[]; sd=sorted(stadiums,key=lambda s:s.get("capacity",0)); big=sd[-1]; sm=sd[0]
        fmtn=lambda n: f"{n:,}".replace(",",".")
        si.append({"ico":"🏟️","label":"Maior estádio","value":fmtn(big.get('capacity',0))+" lugares","detail":f"{big.get('name')} · {big.get('city')}"})
        si.append({"ico":"🏕️","label":"Menor estádio","value":fmtn(sm.get('capacity',0))+" lugares","detail":f"{sm.get('name')} · {sm.get('city')}"})
        bycc=Counter(s.get("cc") for s in stadiums)
        si.append({"ico":"🗺️","label":"Sedes por país","value":" · ".join(f"{n} {COUNTRY.get(c,c)}" for c,n in bycc.most_common())})
        capt=sum(s.get("capacity",0) for s in stadiums)
        si.append({"ico":"🪑","label":"Capacidade somada","value":fmtn(capt)+" lugares","detail":f"{len(stadiums)} estádios · média {fmtn(capt//len(stadiums))}"})
        C["sections"].append({"ico":"🏟️","title":"Sedes","items":si})

    # ===== CONFEDERAÇÕES =====
    if teams:
        ci=[]; conf=Counter(t.get("confed") for t in teams if t.get("confed"))
        CONFN={"UEFA":"Europa","CONMEBOL":"América do Sul","CONCACAF":"Am. Norte/Central","CAF":"África","AFC":"Ásia","OFC":"Oceania"}
        if conf: ci.append({"ico":"🌍","label":"Seleções por confederação","rows":[{"n":CONFN.get(c,c),"v":str(n),"s":c} for c,n in conf.most_common()]})
        cont=Counter(t.get("continent") for t in teams if t.get("continent"))
        CONTN={"Europe":"Europa","Africa":"África","Asia":"Ásia","North America":"Am. do Norte","South America":"Am. do Sul","Oceania":"Oceania"}
        if cont: ci.append({"ico":"🧭","label":"Por continente","value":" · ".join(f"{n} {CONTN.get(c,c)}" for c,n in cont.most_common())})
        if ci: C["sections"].append({"ico":"🌍","title":"Confederações","items":ci})

    return C

# ---------- Brasil nas Copas (historico curado + verificado; 2026 vem do openfootball) ----------
def compute_brasil(games):
    flag=lambda c: FLAG.get(c,""); nm=lambda c: NAME.get(c,c)
    B={"hero":[],"sections":[]}
    B["hero"]=[
        {"ico":"🏆","label":"Pentacampeão","value":"5 títulos","detail":"1958 · 1962 · 1970 · 1994 · 2002"},
        {"ico":"⭐","label":"Presença 100%","value":"23 Copas","detail":"única seleção em todas as edições"},
        {"ico":"👑","label":"Pelé","value":"Tricampeão","detail":"único jogador com 3 títulos mundiais"},
        {"ico":"👟","label":"Ronaldo","value":"15 gols","detail":"maior artilheiro do Brasil em Copas"},
    ]
    # Títulos & campanhas
    B["sections"].append({"ico":"🏆","title":"Títulos & campanhas","items":[
        {"ico":"🏆","label":"Os 5 títulos mundiais","rows":[
            {"n":"1958 · Suécia","s":"final vs Suécia","v":"5–2"},
            {"n":"1962 · Chile","s":"final vs Tchecoslováquia","v":"3–1"},
            {"n":"1970 · México","s":"final vs Itália","v":"4–1"},
            {"n":"1994 · EUA","s":"final vs Itália (pên.)","v":"3–2"},
            {"n":"2002 · Coreia/Japão","s":"final vs Alemanha","v":"2–0"}]},
        {"ico":"🥈","label":"Vice-campeão","value":"2 vezes","detail":"1950 (Uruguai) e 1998 (França)"},
        {"ico":"🎯","label":"Finais disputadas","value":"7 finais","detail":"5 títulos · 2 vices"},
        {"ico":"🌟","label":"Melhor campanha","value":"México 1970","detail":"6 jogos, 6 vitórias, 19 gols"},
        {"ico":"💯","label":"Campanhas perfeitas","value":"2 (1970 e 2002)","detail":"único país a vencer todos os jogos duas vezes"},
        {"ico":"🏅","label":"Entre os 5 primeiros","value":"15 vezes","detail":"em 22 edições — recorde da competição"}]})
    # Recordes & números
    B["sections"].append({"ico":"🥇","title":"Recordes & números","note":"até a Copa de 2022","items":[
        {"ico":"📊","label":"Jogos em Copas","value":"114 jogos","detail":"76 V · 19 E · 19 D"},
        {"ico":"⚽","label":"Gols","value":"237 a favor","detail":"108 sofridos · saldo +129"},
        {"ico":"👑","label":"Maior vencedor","value":"76 vitórias","detail":"mais que qualquer seleção na história"},
        {"ico":"🔥","label":"Maiores sequências","value":"11 vitórias","detail":"e 13 jogos invicto — recordes do torneio"},
        {"ico":"⭐","label":"Participações","value":"23 (todas)","detail":"única sempre presente desde 1930"}]})
    # Artilheiros
    B["sections"].append({"ico":"👟","title":"Maiores artilheiros em Copas","note":"até a Copa de 2022","items":[
        {"ico":"👟","label":"Gols em Copas do Mundo","rows":[
            {"n":"Ronaldo","s":"1998·2002·2006","v":"15"},
            {"n":"Pelé","s":"1958–1970","v":"12"},
            {"n":"Ademir","s":"1950","v":"9"},
            {"n":"Vavá","s":"1958·1962","v":"9"},
            {"n":"Jairzinho","s":"1970·1974","v":"9"},
            {"n":"Leônidas","s":"1938","v":"8"},
            {"n":"Neymar","s":"2014·2018·2022","v":"8"},
            {"n":"Rivaldo","s":"1998·2002","v":"8"}]}]})
    # Craques & feitos
    B["sections"].append({"ico":"⭐","title":"Craques & feitos","items":[
        {"ico":"🅰️","label":"Recordista de jogos","value":"Cafu — 20","detail":"único com 3 finais seguidas (94·98·02)"},
        {"ico":"👑","label":"Pelé","value":"Campeão aos 17","detail":"o mais jovem a vencer uma Copa (1958)"},
        {"ico":"🎯","label":"Jairzinho","value":"Marcou em todos","detail":"gol em cada jogo do título de 1970"},
        {"ico":"💥","label":"Ademir","value":"4 gols num jogo","detail":"no 7–1 sobre a Suécia (1950)"},
        {"ico":"🧠","label":"Zagallo","value":"Tetracampeão","detail":"jogador (58·62), técnico (70), coord. (94)"}]})
    # Jogos para a história
    B["sections"].append({"ico":"🎭","title":"Jogos para a história","items":[
        {"ico":"💥","label":"Maior goleada","value":"7–1 vs Suécia","detail":"Copa de 1950, no Maracanã"},
        {"ico":"💔","label":"Pior derrota","value":"1–7 vs Alemanha","detail":"semifinal de 2014, no Mineirão"},
        {"ico":"😱","label":"Maracanaço","value":"1950","detail":"perdeu o título em casa para o Uruguai (2–1)"},
        {"ico":"🎉","label":"Tetra de 1994","value":"24 anos depois","detail":"1ª final decidida nos pênaltis"},
        {"ico":"🏆","label":"Penta de 2002","value":"7 vitórias em 7","detail":"final 2–0, dois gols de Ronaldo"}]})
    # Técnicos campeões
    B["sections"].append({"ico":"👔","title":"Técnicos campeões","items":[
        {"ico":"👔","label":"Quem levantou a taça","rows":[
            {"n":"Vicente Feola","s":"Suécia","v":"1958"},
            {"n":"Aymoré Moreira","s":"Chile","v":"1962"},
            {"n":"Mário Zagallo","s":"México","v":"1970"},
            {"n":"C. A. Parreira","s":"EUA","v":"1994"},
            {"n":"Felipão","s":"Coreia/Japão","v":"2002"}]}]})
    # Brasil na Copa 2026 (dinamico — vem do openfootball)
    br=[g for g in games if g["h"]=="BRA" or g["a"]=="BRA"]
    j2026=[]
    for g in br:
        opp = g["a"] if g["h"]=="BRA" else g["h"]
        gb,go = (g["gh"],g["ga"]) if g["h"]=="BRA" else (g["ga"],g["gh"])
        if g["r"]:
            res="✓ V" if gb>go else "✗ D" if gb<go else "= E"
            j2026.append({"n":f"{flag(opp)} {nm(opp)}","s":g.get("dt",""),"v":f"{gb}–{go} {res}"})
        else:
            j2026.append({"n":f"{flag(opp)} {nm(opp)}","s":(g.get("dt","") or "a definir"),"v":"a jogar"})
    sec26=[{"ico":"🇧🇷","label":"Onde está","value":"Grupo C","detail":"com Marrocos, Escócia e Haiti · téc. Carlo Ancelotti"}]
    if j2026: sec26.append({"ico":"📅","label":"Jogos do Brasil em 2026","rows":j2026})
    B["sections"].append({"ico":"🇧🇷","title":"Brasil na Copa 2026","note":"atualiza sozinho","items":sec26})
    return B

# ---------- perfil de cada seleção (histórico fixo + Copa 2026 dinâmica) ----------
def _titulo_pt(n):
    return {5:"Pentacampeão",4:"Tetracampeão",3:"Tricampeão",2:"Bicampeão",1:"Campeão mundial"}.get(n,"")
def _best_pt(h):
    if h["t"]: return {5:"Pentacampeão",4:"Tetracampeão",3:"Tricampeão",2:"Bicampeão",1:"Campeão"}.get(len(h["t"]),"Campeão")
    if h["v"]: return "Vice-campeão"
    if h["sf"]: return "Semifinalista (3º/4º)"
    return {3:"Quartas de final",2:"Oitavas de final",1:"16-avos de final"}.get(h["bl"],"Fase de grupos")

def compute_profiles(games, squads):
    from collections import Counter, defaultdict
    flag=lambda c: FLAG.get(c,""); nm=lambda c: NAME.get(c,c)
    sct=defaultdict(Counter)
    for g in GOALS:
        if g["who"] and not g["og"]: sct[g["c"]][g["who"]]+=1
    sqc=defaultdict(list)
    for t in (squads or []):
        c=OF_NAMES.get((t.get("name") or "").strip())
        if c:
            for pl in t.get("players",[]): sqc[c].append(pl)
    grp_of={c:gl for gl,cs in GR.items() for c in cs}
    gby=defaultdict(list)
    for m in games: gby[m["h"]].append(m); gby[m["a"]].append(m)
    PRO={}
    for code in NAME:
        h=HIST.get(code) or {"p":0,"t":[],"v":[],"sf":0,"j":0,"w":0,"dr":0,"l":0,"gf":0,"ga":0,"fr":None,"bl":0}
        # 2026 conta como participação; os jogos JÁ disputados de 2026 entram no balanço
        real26=[m for m in gby.get(code,[]) if m.get("r")]
        w26=e26=l26=gf26=ga26=0
        for m in real26:
            gf,ga=(m["gh"],m["ga"]) if m["h"]==code else (m["ga"],m["gh"])
            gf26+=gf; ga26+=ga
            if gf>ga: w26+=1
            elif gf<ga: l26+=1
            else: e26+=1
        part=h["p"]+1
        jt=h["j"]+len(real26); wt=h["w"]+w26; et=h["dr"]+e26; lt=h["l"]+l26
        gft=h["gf"]+gf26; gat=h["ga"]+ga26
        estreia=h["fr"] or 2026
        if h["p"]==0: sub=f"Estreante · Grupo {grp_of.get(code,'?')}"
        elif h["t"]: sub=f"{_titulo_pt(len(h['t']))} · {part} Copas"
        else: sub=f"{_best_pt(h)} · {part} Copas"
        secs=[]
        # história
        hi=[]
        if h["p"]==0:
            hi.append({"ico":"🌟","label":"Estreante","value":"1ª Copa da história","detail":"2026 é a estreia desta seleção em Copas"})
            if real26:
                hi.append({"ico":"📊","label":"Estreia em 2026","value":f"{len(real26)} jogo(s) até agora","detail":f"{wt}V · {et}E · {lt}D · {gft}–{gat} gols"})
        else:
            if h["t"]: hi.append({"ico":"🏆","label":"Títulos mundiais","value":f"{len(h['t'])}× campeão","detail":", ".join(map(str,h['t']))})
            if h["v"]: hi.append({"ico":"🥈","label":"Vice-campeão","value":f"{len(h['v'])}×","detail":", ".join(map(str,h['v']))})
            hi.append({"ico":"📅","label":"Participações","value":f"{part} Copas","detail":f"desde {estreia}"})
            if not h["t"]: hi.append({"ico":"🎯","label":"Melhor campanha","value":_best_pt(h)})
            if h["sf"]: hi.append({"ico":"🥉","label":"Semifinais","value":f"{h['sf']}×","detail":"entre os 4 melhores"})
            hi.append({"ico":"📊","label":"Balanço","value":f"{jt} jogos","detail":f"{wt}V · {et}E · {lt}D"})
            hi.append({"ico":"⚽","label":"Gols","value":f"{gft} feitos","detail":f"{gat} sofridos · saldo {gft-gat:+d}"})
        note="números já incluem a Copa de 2026" if h["p"]>0 else ""
        secs.append({"ico":"🏆","title":"Nas Copas do Mundo","note":note,"items":hi})
        # Copa 2026
        c2=[{"ico":"📍","label":"Onde está em 2026","value":f"Grupo {grp_of.get(code,'?')}"}]
        rows=[]
        for m in gby.get(code,[]):
            opp=m["a"] if m["h"]==code else m["h"]
            gb,go=(m["gh"],m["ga"]) if m["h"]==code else (m["ga"],m["gh"])
            if m["r"]:
                res="✓" if gb>go else "✗" if gb<go else "="
                rows.append({"n":f"{flag(opp)} {nm(opp)}","s":m.get("dt",""),"v":f"{gb}–{go} {res}"})
            else:
                rows.append({"n":f"{flag(opp)} {nm(opp)}","s":(m.get('dt','') or 'a definir'),"v":"a jogar"})
        if rows: c2.append({"ico":"📅","label":"Jogos na fase de grupos","rows":rows})
        if sct.get(code):
            w,q=sct[code].most_common(1)[0]
            c2.append({"ico":"👟","label":"Artilheiro em 2026","value":w,"detail":f"{q} gol(s)"})
        pls=sqc.get(code,[])
        if pls:
            ages=[(age_on(p.get("date_of_birth","")),p) for p in pls]; ages=[(a,p) for a,p in ages if a]
            if ages:
                ages.sort(key=lambda x:x[0])
                c2.append({"ico":"👶","label":"Mais novo do elenco","value":ages[0][1]["name"],"detail":f"{ages[0][0]:.0f} anos"})
                c2.append({"ico":"🧓","label":"Mais veterano","value":ages[-1][1]["name"],"detail":f"{ages[-1][0]:.0f} anos"})
            clubs=Counter(p["club"]["name"] for p in pls if p.get("club"))
            if clubs:
                cl,q=clubs.most_common(1)[0]
                c2.append({"ico":"🏟️","label":"Clube que mais cede","value":cl,"detail":f"{q} jogador(es)"})
        secs.append({"ico":"📅","title":"Na Copa 2026","items":c2})
        PRO[code]={"nm":nm(code),"fl":flag(code),"sub":sub,"sections":secs}
    return PRO

# ---------- montar / calcular ----------
def build():
    real=load_seed(); real.update(fetch_results())   # openfootball tem prioridade sobre o seed
    games=[]
    for g,ts in GR.items():
        for a,b in itertools.combinations(ts,2):
            if (a,b) in real:   H,A=a,b; gh,ga=real[(a,b)]; rr=True
            elif (b,a) in real: H,A=b,a; gh,ga=real[(b,a)]; rr=True
            else: H,A,s=pred_score(a,b); gh,ga=s; rr=False
            rd=ROUNDS.get((H,A)) or ROUNDS.get((A,H))
            meta=META_GRP.get(frozenset((H,A))) or {}
            _d,_h=fmt_when_brt(meta.get("dt",""),meta.get("tm",""))
            games.append({"g":g,"h":H,"a":A,"gh":gh,"ga":ga,"r":rr,"rd":rd,
                          "dt":_d,"hr":_h,"gr":meta.get("gr","")})
    return games

def standings(games):
    tab={}
    for g,ts in GR.items():
        st={t:{"P":0,"W":0,"D":0,"L":0,"GF":0,"GA":0} for t in ts}
        for m in games:
            if m["g"]!=g: continue
            h,a,gh,ga=m["h"],m["a"],m["gh"],m["ga"]
            st[h]["GF"]+=gh; st[h]["GA"]+=ga; st[a]["GF"]+=ga; st[a]["GA"]+=gh
            if gh>ga: st[h]["P"]+=3;st[h]["W"]+=1;st[a]["L"]+=1
            elif gh<ga: st[a]["P"]+=3;st[a]["W"]+=1;st[h]["L"]+=1
            else: st[h]["P"]+=1;st[a]["P"]+=1;st[h]["D"]+=1;st[a]["D"]+=1
        order=sorted(ts,key=lambda t:(-st[t]["P"],-(st[t]["GF"]-st[t]["GA"]),-st[t]["GF"],-F[t]))
        tab[g]=(order,st)
    return tab

def main():
    games=build()
    tab=standings(games)
    real_n=sum(1 for m in games if m["r"])
    # --- arquivos extras do openfootball (sede / elencos / seleções) ---
    stadiums=aslist(fetch_json(OF_STADIUMS),"stadiums")
    squads  =aslist(fetch_json(OF_SQUADS),  "squads")
    teams   =aslist(fetch_json(OF_TEAMS),   "teams")
    sbc={s["city"]:s for s in stadiums} if stadiums else {}
    # enriquecer cada jogo de grupo com estádio + país
    for m in games:
        v=venue_of(m.get("gr",""), sbc)
        m["vn"]=v["vn"]; m["co"]=v["co"]; m["cf"]=CFLAG.get(v["cc"],"")
    # sede/data dos jogos do mata-mata (indexados pelo número 73..104)
    VENUE_KO={}
    for num,meta in META_KO.items():
        v=venue_of(meta.get("gr",""), sbc)
        _d,_h=fmt_when_brt(meta.get("dt",""),meta.get("tm",""))
        VENUE_KO[str(num)]={"dt":_d,"hr":_h,"vn":v["vn"],"co":v["co"],"cf":CFLAG.get(v["cc"],"")}
    CURIOS=compute_curios(games, squads, stadiums, teams)
    BRASIL=compute_brasil(games)
    PROFILES=compute_profiles(games, squads)
    # REALLIST p/ rodape
    rg=[m for m in games if m["r"]]; rg.sort(key=lambda m:m["g"])
    reallist=" · ".join(f"{NAME[m['h']]} {m['gh']}–{m['ga']} {NAME[m['a']]}" for m in rg) or "(nenhum ainda)"
    now=datetime.datetime.now(TZ) if TZ else datetime.datetime.utcnow()
    asof=now.strftime("%d/%m/%Y %H:%M")+(" (Brasília)" if TZ else " UTC")
    # injetar no template
    ALLOC=json.load(open(os.path.join(HERE,"third_alloc.json"),encoding="utf-8"))
    DATA={"F":F,"GR":GR,"NAME":NAME,"FLAG":FLAG,"GAMES":games,
          "PRED_PHASES":original_phases(ALLOC),"KO_REAL":KO_REAL,
          "CURIOS":CURIOS,"VENUE_KO":VENUE_KO,"BRASIL":BRASIL,"PROFILES":PROFILES,"H2H":H2H}
    tpl=open(os.path.join(HERE,"template2.html"),encoding="utf-8").read()
    html=(tpl.replace("/*__DATA__*/",json.dumps(DATA,ensure_ascii=False,separators=(",",":")))
             .replace("/*__ALLOC__*/",json.dumps(ALLOC,ensure_ascii=False,separators=(",",":")))
             .replace("__REALLIST__",reallist).replace("__ASOF__",asof))
    site=os.path.join(HERE,"site")
    os.makedirs(site,exist_ok=True)
    open(os.path.join(site,"index.html"),"w",encoding="utf-8").write(html)
    # arquivos de indexação (SEO)
    open(os.path.join(site,"robots.txt"),"w",encoding="utf-8").write(
        "User-agent: *\nAllow: /\nSitemap: https://evandroback.github.io/Copa-2026/sitemap.xml\n")
    today=now.strftime("%Y-%m-%d")
    open(os.path.join(site,"sitemap.xml"),"w",encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url>\n    <loc>https://evandroback.github.io/Copa-2026/</loc>\n'
        f'    <lastmod>{today}</lastmod>\n    <changefreq>hourly</changefreq>\n    <priority>1.0</priority>\n'
        '  </url>\n</urlset>\n')
    print(f"[ok] site gerado — {real_n} jogos reais — {len(CURIOS.get('sections',[]))} seções de curiosidades — {asof}")

if __name__=="__main__":
    main()
