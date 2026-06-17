
#### Pakete ######
import json
import openai
import os
from tqdm import tqdm
import re


from sentence_transformers import SentenceTransformer, util
from gpt4all import GPT4All

##### Die Konfiguration #####
input_fil = r""
output_fil = "627udvidet.jsonl"
model_id = "gpt-4o-mini" #  "gpt-3.5-turbo"
openai.api_key = os.getenv("MY_OAK")
Ensartethedsgrænse = 0.70 # Grænsen for sentence transformer

instruks = "Answer the following queestion in one word or short phrase. Always give an answer - no matter how unclear or scrambled the question is. Answer only, no explanation. Just the answer. If message completely unreadable, give your best guess."


### Modellauswahl ####
model_st = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
model_gpt4all= GPT4All(model_name="Phi-3-mini-4k-instruct.Q4_0.gguf", model_path=r"C:\Users\e3074\.cache\gpt4all",allow_download=False)

"""
model_gpt4all = GPT4All("Phi-3-mini-4k-instruct.Q4_0.gguf")
"""
print("multi-qa-MiniLM-L6-cos-v1 og Phi-3-mini er blevet indlæst")

#### Chat forespørgsel ####
def gpt_forespørgsel(scramb):
    svar = openai.chat.completions.create(
        model = model_id,
        temperature = 0,
        messages= [{"role":"system", "content": f"{instruks}"},{"role":"user", "content": scramb}])
    return svar.choices[0].message.content.strip().lower()

#### Første tjek; Det præcise match #####
def præcist_match(svar_model,korrekt):
    svar_model = svar_model.lower().strip(" .")
    korrekt = korrekt.lower().strip(". ")
    skm = [korrekt, "the "+ korrekt, "a " + korrekt, "an "+korrekt]
    return any(svar_model == ms for ms in skm)

#### Andet tjek; Semantisk tjek #######
def sem_match(svar_model, korrekt):
    emb_svar = model_st.encode(svar_model, convert_to_tensor= True)
    emb_korrekt = model_st.encode(korrekt, convert_to_tensor=True)
    score = util.cos_sim(emb_svar, emb_korrekt).item()
    return score >=Ensartethedsgrænse, round(score, 3)

##### Tredje tjek; GPT4ALL #####
def dies_irae(spørgsmål, svar_model, korrekt):
    prompt = f"""QUESTION: {spørgsmål}
CORRECT ANSWER:{korrekt}
GIVEN ANSWER: {svar_model}

Role:
You are strict binary grading system.

Task:
Decide if the GIVEN ANSWER is CORRECT.

Rules:
- output SI ONLY if the GIVEN ANSWER is clearly a correct answer to the QUESTION or with the exact same meaning of the CORRECT ANSWER
- Reject all partial, related, broader, narrower, or similar concepts
- ONLY EXCEPTION: If question is about a head of state and the GIVEN ANSWER is prime minister, then accept
- if there is any doubt, output NON. 

Important:
- !!!!Answers like "unclear", "uncertain", "unknown", and similar are under no circumstances acceptable!!!!!
- If Given ANSWER is "unknown", "unclear", "not clear", "uncertain" or similar DO NOT ACCEPT.
- If the GIVEN ANSWER is in the QUESTION DO NOT ACCEPT (e.g. q: WHat is the capital of the Neatherlands? a: Capital --> DO NOT ACCEPT)

Return only ONE token:
SI or NON"""
    with model_gpt4all.chat_session():
        svar = model_gpt4all.generate(prompt, max_tokens= 10)
    return "SI" in svar.upper()


### Uheldige mønstre ###
til_helvede = re.compile(
    r"""
    \b(
        unclear|
        unknown|
        uncertain|
        not\s*sure|
        no\s*idea|
        i\s*don'?t\s*know|
        not\s*certain|
        idk                        
    )\b
    """,
    re.IGNORECASE|re.VERBOSE)

def ugyldigt_svar(svar):
    if not svar:
        return True
    s = svar.strip().lower()
    s = re.sub(r"\s+"," ",s)
    return bool(til_helvede.search(s))



### Evaluering ###
def evalu(spørgsmål, svar_model, korrekt):
    if ugyldigt_svar(svar_model):
        return 0, 0, None
    if præcist_match(svar_model, korrekt):
        return 1,0, None
    mad, score = sem_match(svar_model, korrekt)
    if mad:
        return 1,1, score
    if score>=0.25 and dies_irae(spørgsmål, svar_model, korrekt):
        return 1, 2, score
    else:
        return 0, 2, score

#### Gotta make sure, ae? ######
bearbejdet = set()
try:
    with open(output_fil, "r", encoding = "utf-8") as m:
        for linje in m:
            if linje.strip():
                bearbejdet.add(json.loads(linje)["id"])
except FileNotFoundError:
    pass


## Outputtets indlæsning #
with open(input_fil, "r", encoding="utf-8") as m:
    prompts = [json.loads(n) for n in m if n.strip()]


### Un bel dì, vedremo ##########
stopfilnavn = "Hold_så_kæft.txt"
def stop_det_så():
    if os.path.exists(stopfilnavn):
        print("Stopper")
        os.remove(stopfilnavn)
        return True
    return False

with open(output_fil, "a", encoding="utf-8") as outta_here:
    for prompt in tqdm(prompts, desc="The game's afoot"):
        if stop_det_så():
            break
        if prompt["id"] in bearbejdet:
            continue
        svar_model = gpt_forespørgsel(prompt["scramble"])
        forstået, forsøg, score = evalu(
            prompt["spørgsmål"],
            svar_model,
            prompt["svar"]
        )
        resultat = {"id": prompt["id"], "spørgsmål": prompt["spørgsmål"],"scramble":prompt["scramble"],"score":prompt["score"], "svar":prompt["svar"], "Mod_svar_s":svar_model, "sem_score": score, "forstået":forstået,"forsøg":forsøg}
        outta_here.write(json.dumps(resultat, ensure_ascii=False)+ "\n")



