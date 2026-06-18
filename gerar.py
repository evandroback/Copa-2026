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
    # REALLIST p/ rodape
    rg=[m for m in games if m["r"]]; rg.sort(key=lambda m:m["g"])
    reallist=" · ".join(f"{NAME[m['h']]} {m['gh']}–{m['ga']} {NAME[m['a']]}" for m in rg) or "(nenhum ainda)"
    now=datetime.datetime.now(TZ) if TZ else datetime.datetime.utcnow()
    asof=now.strftime("%d/%m/%Y %H:%M")+(" (Brasília)" if TZ else " UTC")
    # injetar no template
    ALLOC=json.load(open(os.path.join(HERE,"third_alloc.json"),encoding="utf-8"))
    DATA={"F":F,"GR":GR,"NAME":NAME,"FLAG":FLAG,"GAMES":games,
          "PRED_PHASES":original_phases(ALLOC),"KO_REAL":KO_REAL,
          "CURIOS":CURIOS,"VENUE_KO":VENUE_KO,"BRASIL":BRASIL}
    tpl=open(os.path.join(HERE,"template2.html"),encoding="utf-8").read()
    html=(tpl.replace("/*__DATA__*/",json.dumps(DATA,ensure_ascii=False,separators=(",",":")))
             .replace("/*__ALLOC__*/",json.dumps(ALLOC,ensure_ascii=False,separators=(",",":")))
             .replace("__REALLIST__",reallist).replace("__ASOF__",asof))
    os.makedirs(os.path.join(HERE,"site"),exist_ok=True)
    open(os.path.join(HERE,"site","index.html"),"w",encoding="utf-8").write(html)
    print(f"[ok] site gerado — {real_n} jogos reais — {len(CURIOS.get('sections',[]))} seções de curiosidades — {asof}")

if __name__=="__main__":
    main()
