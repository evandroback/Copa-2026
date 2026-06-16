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
        ft=(m.get("score") or {}).get("ft")
        if not ft: continue                          # so jogos com placar final
        t1=OF_NAMES.get((m.get("team1") or "").strip())
        t2=OF_NAMES.get((m.get("team2") or "").strip())
        if not t1 or not t2:                          # placeholders (1A, W73...) ou nome novo
            n1,n2=m.get("team1",""),m.get("team2","")
            if n1 and n2 and not any(c.isdigit() for c in n1+n2) and "/" not in n1+n2:
                bad.add((n1,n2))
            continue
        if (m.get("group") or "").startswith("Group"):
            out[(t1,t2)]=(int(ft[0]),int(ft[1]))
            grp_games.append((m.get("group",""), m.get("date",""), m.get("time",""), t1, t2))
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
    print(f"[ok] openfootball: {len(out)} jogos de grupo + {ko_n} de mata-mata encerrados")
    return out

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
            games.append({"g":g,"h":H,"a":A,"gh":gh,"ga":ga,"r":rr,"rd":rd})
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
    # REALLIST p/ rodape
    rg=[m for m in games if m["r"]]; rg.sort(key=lambda m:m["g"])
    reallist=" · ".join(f"{NAME[m['h']]} {m['gh']}–{m['ga']} {NAME[m['a']]}" for m in rg) or "(nenhum ainda)"
    now=datetime.datetime.now(TZ) if TZ else datetime.datetime.utcnow()
    asof=now.strftime("%d/%m/%Y %H:%M")+(" (Brasília)" if TZ else " UTC")
    # injetar no template
    ALLOC=json.load(open(os.path.join(HERE,"third_alloc.json"),encoding="utf-8"))
    DATA={"F":F,"GR":GR,"NAME":NAME,"FLAG":FLAG,"GAMES":games,
          "PRED_PHASES":original_phases(ALLOC),"KO_REAL":KO_REAL}
    tpl=open(os.path.join(HERE,"template2.html"),encoding="utf-8").read()
    html=(tpl.replace("/*__DATA__*/",json.dumps(DATA,ensure_ascii=False,separators=(",",":")))
             .replace("/*__ALLOC__*/",json.dumps(ALLOC,ensure_ascii=False,separators=(",",":")))
             .replace("__REALLIST__",reallist).replace("__ASOF__",asof))
    os.makedirs(os.path.join(HERE,"site"),exist_ok=True)
    open(os.path.join(HERE,"site","index.html"),"w",encoding="utf-8").write(html)
    print(f"[ok] site/index.html gerado — {real_n} jogos reais — atualizado {asof}")

if __name__=="__main__":
    main()
