import json
import random
import string


input_file = '/Users/jinlongli/Desktop/projekt/200testsæt.jsonl'
output_file = '200testsæt_level5.jsonl'
error_percentage = 100 #skrives i procent


def introduce_errors(text, error_percentage):

    error_ratio = (error_percentage / 100) ** 1.5 
    characters = list(text)
    new_list = []
    
    for char in characters:
        if char == " ":
            new_list.append(" ")
            continue

        r = random.random()
        #kan ændres hvis sætning bliver for underlig
        if r < error_ratio * 0.3:
            continue
        elif r < error_ratio:
            new_list.append(random.choice(string.ascii_letters))
        else:
            new_list.append(char)
            
    return "".join(new_list)



with open(input_file, 'r', encoding='utf-8') as f_in, \
     open(output_file, 'w', encoding='utf-8') as f_out:
    
    for line in f_in:
        if line.strip():
            item = json.loads(line)
            
            scrambled_text = introduce_errors(item["spørgsmål"], error_percentage)
            
            new_item = {
                "id": item.get("id"),
                "spørgsmål": item.get("spørgsmål"),
                "scramble": scrambled_text,
                "score": error_percentage/100,
                "svar": item.get("svar")
            }
        
            f_out.write(json.dumps(new_item, ensure_ascii=False) + '\n')

print(f"saved in '{output_file}'")