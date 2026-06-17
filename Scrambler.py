#AI er i dette dokument brugt til at assistere med ideer til opsætning af funktioners struktur og udvikling og hvilke moduler der kunne være en god ide at bruge.
#Der er også inspiration fra online kodeeksempler givet på givne hjemmesider, bl.a. stackoverflow
#Der er lavet meget individuelt arbejde, men AI har hovedsageligt været brugt til struktur og ideer til opsætningen af evt. problemløsninger i Python.
import json
import random
import editdistance
filepath = "/Users/oliverbach/Documents/627endeligtsæt.jsonl"
newfile = []



#filåbner
with open(filepath, "r") as docs:
   for line in docs:
    newfile.append(json.loads(line))



def scramble_ord(ord):
        liste_ord = list(ord)
        random.shuffle(liste_ord)
        return "".join(liste_ord)

def scramble_sætning(sentence):
        scrambled = []
        words = sentence.split()
        random.shuffle(words)
        for ord in words:
            scrambled.append(scramble_ord(ord))
        return " ".join(scrambled)


def sletningsfunktion(ord): #sletter et bogstav ved et uheld
    if len(ord)==1:
        return ord
    valg = random.randint(0,len(ord)-1)
    edited_word = ord[:valg]+ord[valg+1:]
    return edited_word

def cer(spørgsmål, scrambled): #rating
      v1 = editdistance.eval(spørgsmål, scrambled) #editdistance module udregner distance i et rum
      v2 = len(spørgsmål)
      value = v1/v2
      return value

def indsætningsfunktion(ord): #indsætter et bogstav (missclickerror)
     valg = random.randint(0,len(ord)) #Der er teknisk set 6 indsættelsesfelter
     bogstav = random.choice("abcdefghijklmnopqrstuvwxyz")
     return ord[:valg]+bogstav+ord[valg:]

def skift_bog(ord): #skifter et bogstav med et forkert bogstav
     valg = random.randint(0,len(ord)-1)
     skiftning = random.choice("abcdefghijklmnopqrstuvwxyz")
     return ord[:valg]+ skiftning+ord[valg+1:]

def ombytningsfunktion(ord): #Bytter om på bogstaver
    if len(ord) == 1:
         return ord
    else:   
          valg = random.randint(0,len(ord)-2) #skal være -2 grundet parkrav
          udskiftning = random.choice("abcdefghijklmnopqrstuvwxyz")
          return ord[:valg]+ord[valg+1]+ord[valg]+ord[valg+2:]

def genereringsfunktion(sentence): #denne funktion generer fejl tilfældigt. Den tager et stykke kode splitter den, applier en fejl til et random ord og samler igen.
        words = sentence.split()
        index = random.randint(0,len(words)-1)
        fejltype = random.choice([sletningsfunktion, indsætningsfunktion, skift_bog, ombytningsfunktion])
        words[index] = fejltype(words[index])
        return " ".join(words)

upper_cer = 0.4
lower_cer = 0.001

for række in newfile:
    spørgsmål = række["spørgsmål"]
    scrambled = spørgsmål
    cer(spørgsmål, scrambled)
    fordelingbinding = random.uniform(lower_cer, upper_cer) #Ide om fordeling fra Joel Sperenza Math
    while cer(spørgsmål, scrambled) < fordelingbinding: 
        scrambled = genereringsfunktion(scrambled)
    række["scrambled"] = scrambled
    række["CER"] = cer(spørgsmål, scrambled)

#Nu indsætter vi det !!!! :D :D :D :D :D - opdaterer rækker til ny jsonl fil.
with open("/Users/oliverbach/Documents/scrambleddata.jsonl", "w") as docs:
    for række in newfile:
        docs.write(json.dumps(række)+"\n")