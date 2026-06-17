
#Vores pakker
import json
import openai
from tqdm import tqdm
import time
import os
import random


##### Konfiguration #####
output_fil = ""
n_sp = 2000
bs = 20
model_id = "gpt-4o-mini"  #Alternativt "gpt-4o-mini" "gpt-3.5-turbo"
max_tokens = 2000 #Arbitrært valg


##### Regulering af spørgsmålenes joie de vivre #####
temptess = (0.3,0.6) #Interval for kreativiteten - kinda. Vi ønsker det i nogen grad ift. spørgsmålene.
#temp_var_prob = 0.2



##### In need of a key? Tant pis I ain't sharing no such thing here #####
openai.api_key = os.getenv("MY_OAK")


###### HF'er ########

def g_t():
    return round(random.uniform(*temptess),2)

suffikser = ["ians", "ese","ans","ish","ian","i"]
def noller(land):
    land = land.lower().strip()
    for suffiks in suffikser:
        if land.endswith(suffiks) and len(land)>= len(suffiks) + 3:
            return land[:-len(suffiks)]
    return land



def openai_kald(messages):
    try:
        chat = openai.chat.completions.create(
            model = model_id,
            messages = messages,
            temperature=g_t(),
            max_tokens = max_tokens
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error {e}")
        time.sleep(1.5)
        return "Tant pis"

def spørgsmålsgenerator(antal, brugte_lande = None):
    messages = [{"role":"system", "content": ("You are a strict trivia generation bot. You must follow formatting rules perfectly" "You master historical and geographical accuracy")}]
    prompt = (f"Generate exactly {antal} unique trivia questions that cover just a single country or historical state of your choice\n\n"
        "Critical Rules:\n")
    
    if brugte_lande:
        black_list = ", ".join(sorted(list(brugte_lande))) 
        prompt += f"DO NOT GENERATE QUESTIONS ABOUT ANY OF THESE COUNTRIES/STATES {black_list}"
        prompt += "Pick a completely different country or state that is not mentioned in the list above\n\n"
    else:
        prompt += "Pick any country or historical state\n\n"
    
    prompt += (
        "1. Every question myst explicitly name the country or state. Never use vauges references.\n"
        "2. Answers must be a specific proper noun or numerical year. Never answer with generic titles\n"
        "3. YEARS IN QUESTIONS: You ARE allowed to include historical years in the questions, but they MUST always be written in digits(e.g. 1867 and 1789')\n"
        "4. IMPORTANT: Only write years as numbers in the answers\n"
        "5. FACTUAL ACCURACY: You must be 100'%' historically adn geographically accurate. Ensure historical figures, battles, and dates are correctly assigned to the specified country\n"
        "6. UNAMBIGUOUS: Each question must have exactly one short, definitive correct answer.\n"
        "7. Do not mix questions from different countries in one batch\n\n"
        "TOPIC ORDER TO COVER FIRST:\n"
        "Capital city, currency, official language, famous wars/battles with their full title, famous people(with a clear unique identifier), dominant ethnic group"
        "After covering these, you may pursue other unique cultural or geographical topics\n\n"
        "FORMATTING:\n"
        "DO NOT use numbers to mark the order of the questions\n"
        "Every question and its associated answer must be written on a new line, seperated by '|'.\n"
        "Format: question|answer|country/state\n"
        "Keep the anser as short and concise as possible"
    )

    messages.append({"role":"user","content":prompt})
   

    svar = openai_kald(messages)
    if svar == "Tant pis":
        return []
    sp_svar = [] #midlertidig liste til at holde svarene

    for linje in svar.split("\n"):
        if "|" in linje:
            dele = linje.split("|")

            if len(dele)>=3:
                s = dele[0].strip()
                sv = dele[1].strip()
                land = noller(dele[2].strip())
                sp_svar.append({"s":s,"sv": sv,"land":land})

    return sp_svar

#### Gør klar til filen  #####
unica_sp = set()
unica_sv = set()
post_udrensning_data = []
nuværende_id = 1

try:
    with open("brugte_lande.json", "r") as ohno:
        brugte_lande = set(json.load(ohno))
except FileNotFoundError:
    brugte_lande = set()


try:
    with open(output_fil,"r",encoding="utf-8") as m:
        for linje in m:
            if linje.strip():
                data = json.loads(linje)
                mod_sp = data["spørgsmål"].lower().strip(". ?")
                mod_sv = data["svar"].lower().strip(". ")
                if mod_sp not in unica_sp and mod_sv not in unica_sv:
                    unica_sp.add(mod_sp)
                    unica_sv.add(mod_sv)
                    data["id"] = nuværende_id
                    post_udrensning_data.append(data)
                    nuværende_id += 1
    with open(output_fil, "w", encoding="utf-8") as m:
        for data in post_udrensning_data:
            m.write(json.dumps(data,ensure_ascii=False)+"\n")
except FileNotFoundError:
    pass
antal_genereret = len(unica_sp)
"""
antal_genereret = 0

try:
    with open(output_fil, "r", encoding="utf-8") as m:
        for linje in m:
            if linje.strip():
                antal_genereret += 1
    id_liste = [json.loads(linje)["id"] for linje in open(output_fil,"r",encoding="utf-8") if linje.strip()]
    nuværende_id = max(id_liste)+ 1 if id_liste else 1
except FileNotFoundError:
    nuværende_id = 1
"""

#### Bearbejdning af data ######
Tilbageværende_spørgsmål = n_sp - antal_genereret

if Tilbageværende_spørgsmål > 0:
    with tqdm(total=Tilbageværende_spørgsmål, desc="Genererer spørgsmål") as pbar:
        while Tilbageværende_spørgsmål > 0:
            ny_bs = min(bs,Tilbageværende_spørgsmål)
            ai_svar = spørgsmålsgenerator(ny_bs, brugte_lande)
            if not ai_svar:
                time.sleep(1)
                continue
            batch_output =[]
            anvendt_land = None
            for ssv in ai_svar:
                if Tilbageværende_spørgsmål == 0:
                    break
                mod_sp = ssv["s"].lower().strip("? .")
                mod_sv = ssv["sv"].lower().strip(" .")
                if mod_sp in unica_sp or mod_sv in unica_sv:
                    continue
                unica_sp.add(mod_sp)
                unica_sv.add(mod_sv)
                anvendt_land = ssv["land"]
                batch_output.append({"id":nuværende_id, "spørgsmål": ssv["s"],"svar": ssv["sv"]})
                nuværende_id += 1
                Tilbageværende_spørgsmål -= 1
                pbar.update(1)
            if anvendt_land:
                brugte_lande.add(noller(anvendt_land.lower().strip()))
                with open("brugte_lande.json", "w") as mochi:
                    json.dump(list(brugte_lande), mochi)
            with open(output_fil,"a",encoding="utf-8") as m:
                for gs in batch_output:
                    m.write(json.dumps(gs,ensure_ascii=False)+"\n")

print(f"Endelig færdig. Data er gemt til {output_fil}")



