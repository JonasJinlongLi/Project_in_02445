

## Les notres paquets ###
import random
import editdistance
import sys
import string
import json



#### Configuration ####
input_fil =r""
output_fil = ""


antal_levels = 6 #kontrol og de fem støjintervaller
indstilling = "Divide" #"Divide" og "impera"

nabotaster = {"q":"wa", "w":"easq", "e":"wrds", "r":"etdf", "t":"rfgy", "y":"tghu","u":"yijh","i":"ujok", "o":"ipkl", "p":"lo","a":"szwq","s":"awedxz","d":"serfcx","f":"drgtvc","g":"tyhvbf","h":"hyjbnu","j":"hukimn","k":"jloim","l":"kpo","z":"sax","x":"dczs","c":"dfxv","v":"gbfc","b":"gvhn","n":"jmbh", "m":"jnk"}

### Besoin d'aide? ####

def liste_split(liste, andele):
    m, n =divmod(len(liste),andele)
    return [liste[i*m+min(i,n):(i+1)*m+min(i+1,n)] for i in range(andele)]

def ordstillingsskifte(ord,rate):
    ord = ord.copy()
    n = len(ord)
    if n < 2 or 0>=rate:
        return ord
    antal_skift = round(rate*n*0.5)
    for nihilo in range(antal_skift):
        i,j = random.sample(range(n),2)
        ord[i], ord[j] = ord[j], ord[i]
    return ord

def taste_fejl(bogstav):
    lille = bogstav.lower()
    if lille not in nabotaster:
        return random.choice(string.ascii_letters)
    nabo = random.choice(nabotaster[lille])
    return nabo.upper() if bogstav.isupper() else nabo

def fejlvalg(tekst, rate):
    if 0>=rate or not tekst:
        return tekst
    fejlrate = rate**1.5
    bogstaver = list(tekst)
    n = len(bogstaver)
    resultat = []
    i = 0
    while i<n:
        bogstav = bogstaver[i]
        if bogstav == " ":
            resultat.append(" ")
            i+=1
            continue
        r = random.random()
        if r < fejlrate * 0.2:
            i +=1
        elif r < fejlrate*0.5:
            resultat.append(taste_fejl(bogstav))
            i+=1
        elif r < fejlrate * 0.7:
            resultat.append(bogstav)
            resultat.append(taste_fejl(bogstav) if random.random() > 0.5 else bogstav)
            i+=1
        elif r < fejlrate *0.9 and i+ 1 < n and bogstaver[i+1]!=" ":
            resultat.append(bogstaver[i+1])
            resultat.append(bogstav)
            i+=2
        elif r < fejlrate:
            resultat.append(random.choice(string.ascii_lowercase))
            i+=1
        else:
            resultat.append(bogstav)
            i+=1
    return "".join(resultat) if resultat else tekst

def drop_mellemrum(ord, rate):
    if not ord:
        return ""
    sammensmeltningssandsynlighed = rate *0.2
    resultat = [ord[0]]
    for et_ord in ord[1:]:
        if random.random() < sammensmeltningssandsynlighed:
            resultat.append(et_ord)
        else:
            resultat.append(" " + et_ord)
    return "".join(resultat)

def tekstscrambler(tekst, rate):
    if rate<= 0:
        return tekst
    ord = tekst.split(" ")
    ord = ordstillingsskifte(ord, rate)
    ord = [fejlvalg(o,rate) for o in ord]
    return drop_mellemrum(ord, rate)

#### Evaluering: ####

def ordstillings_score(originale_ord, scramblede_ord):
    n = max(len(originale_ord), len(scramblede_ord))
    if n == 0:
        return 0.0
    mismatch = 0
    for i in range(n):
        og_ord = originale_ord[i] if i < len(originale_ord) else None
        scramb_ord =  scramblede_ord[i] if i < len(scramblede_ord) else None
        if og_ord != scramb_ord:
            mismatch +=1
    return mismatch/n

def score_mål(original, scrambled, vægt_rækkefølge=0.5):
    if original == scrambled:
        return 0.0
    v1 = editdistance.eval(original, scrambled)
    v2 = len(original) if len(original) > 0 else 1
    bogstav_score = min(1, v1/v2)
    rækkefølge_score = ordstillings_score(original.split(" "), scrambled.split(" ")) 
    kombineret = (1-vægt_rækkefølge)*bogstav_score + vægt_rækkefølge*rækkefølge_score
    return round(kombineret, 4)

#### Outputtets fordeling og format #####
def Eris(item, mål_rate, gruppe_indeks, unikke_id):
    original = item["spørgsmål"]
    if gruppe_indeks == 0:
        return {"id":unikke_id,"spørgsmål":original,"scramble":original,"score":0.0,"svar":item.get("svar")}
    faktisk_mål = max(0.0001, mål_rate)
    bedste_scramble = original
    bedste_score = 0.0
    bedste_diff = 1
    indre_rate = faktisk_mål

    # Ye thought it'd be enough with random, but ye ain't got no way to avoid 0.0 (killing me softly) ####
    for attempt in range(25):
        scrambled_tekst = tekstscrambler(original, indre_rate)
        faktisk_score = score_mål(original, scrambled_tekst)
        if faktisk_score == 0.0:
            indre_rate = min(2, indre_rate*1.5)
            continue
        difference = abs(faktisk_score-faktisk_mål)
        if difference < bedste_diff:
            bedste_diff = difference
            bedste_scramble = scrambled_tekst
            bedste_score = faktisk_score
        if difference <= 0.04:
            break
        indre_rate = max(0.001, indre_rate*0.75) if faktisk_score > faktisk_mål else min(2, indre_rate*1.25)
    return {"id":unikke_id, "spørgsmål":original,"scramble":bedste_scramble,"score":round(bedste_score,4),"svar": item.get("svar")}

def gid(level_indeks):
    if level_indeks == 0:
        return 0.0, "0.0"
    nedre_grænse = (level_indeks-1)*0.2
    øvre_grænse = level_indeks*0.2
    gruppe_label = f"]{nedre_grænse:.1f};{øvre_grænse:.1f}]"
    if nedre_grænse == 0.0:
        nedre_grænse = 0.0001
    rate = random.uniform(nedre_grænse,øvre_grænse)
    return rate, gruppe_label

##### Gotta learn..... #####
if __name__ == "__main__":
    try:
        with open(input_fil, "r", encoding="utf-8") as m_in:
            items = [json.loads(linje) for linje in m_in if linje.strip()]
    except FileNotFoundError:
        sys.exit(1)
    with open(output_fil, "w", encoding="utf-8") as m_out:
        if indstilling == "Divide":
            nanimoshiranai = liste_split(items, antal_levels)
            for indeks, nani in enumerate(nanimoshiranai):
                for item in nani:
                    rate, gruppe_label = gid(indeks)
                    unikke_id = int(item.get("id"))
                    m_out.write(json.dumps(Eris(item, rate, indeks, unikke_id), ensure_ascii=False)+"\n")
        elif indstilling == "impera":
            for item in items:
                bid = int(item.get("id"))
                for indeks in range(antal_levels):
                    rate, rien  = gid(indeks)
                    unikke_id = (bid*10) + indeks
                    m_out.write(json.dumps(Eris(item, rate, indeks, unikke_id), ensure_ascii=False)+"\n")
        else:
            sys.exit(1)
    print(f"Output gemt i {output_fil}")


