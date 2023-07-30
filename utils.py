from pydantic import BaseModel
import json
import requests
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

class Query(BaseModel):
    birthday: str
    birthtime: str
    birthplace: str

class Query2(BaseModel):
    test: str


def get_horoscope(query: Query):
    BASE_URL = 'https://astrology-api-3ipo.onrender.com/horoscope'
    # use fixed right now. TODO replace to query context
    params = {
        'time': '1993-08-06T20:50:00Z',
        'latitude': '-33.41167',
        'longitude': '-70.66647',
        'houseSystem': 'P'
    }

    response = requests.get(BASE_URL, params=params)

    # Convert the response to a Python dictionary
    data = response.json()

    # Now you can interact with the data as a normal dictionary
    return data


def get_sign_name(sign_number):
    # Replace this function with your own logic to map sign numbers to sign names.
    # For example, you can use a list or a dictionary to do the mapping.
    # Here, I'm just returning some placeholder sign names.
    sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    return sign_names[sign_number - 1]

def extract_astro_table(input_json):
  output_json = {
      "astro_table": []
  }
  encountered_signs = set()

  for idx, house_data in enumerate(input_json['data']['houses']):
      sign_name = get_sign_name(house_data["sign"])
      if sign_name in encountered_signs:
          continue

      astro_entry = {
          "sign": sign_name,
          "astros": [],
          "houses": idx+1
      }
      encountered_signs.add(sign_name)

      # ADD ASTROS
      for astro, astro_data in input_json["data"]["astros"].items():
          if astro_data["sign"] == house_data["sign"]:
              astro_entry["astros"].append(astro)

      # ADD ASCENDANT      
      axe_asc_data = input_json['data']['axes']['asc']
      if axe_asc_data["sign"] == house_data["sign"]:
          astro_entry["astros"].append("ascendant")

      output_json["astro_table"].append(astro_entry)
  return output_json

def extract_aspects(input_json):
    output_json = {"aspects": []}
    
    for aspects in input_json['data']['aspects'].values():
    # loop over each aspect
        for aspect in aspects:
            # if the first planet exists, append the simplified aspect to the output
            if aspect['first']['exist']:
                simplified_aspect = {
                    'first_planet': aspect['first']['name'],
                    'second_planet': aspect['second']['name'],
                    'name': aspect['name'],
                    'direction': aspect['direction']
                }
                output_json['aspects'].append(simplified_aspect)
    return output_json
    
# without few-shots, hard to force it only output json
def get_top_summary_prompt(input_json_astro_tbl: dict) -> str:
    json_str = json.dumps(input_json_astro_tbl, indent=4)  # For pretty print
    
    return f'''
    Hey Claude, you are an expert in horoscope. Based on the provided json regarding the planet, zodiacs and house information, can you output the sun, moon and ascendant information, in a json struct like [{{"header": "Sun in Leo", "short_summary": "A short summary about the reading on the planet", "Long description": "A long description expanding on the short summary"}}, {{...}}]?

    Input info:

    {json_str}

    Output json (Please wrap the json code with <json>):
    '''

def get_top_summary(anthropic_session, input_json_astro_tbl):
    prompt = get_top_summary_prompt(input_json_astro_tbl)
    
    completion = anthropic_session.completions.create(
        model="claude-2",
        max_tokens_to_sample=1000,
        prompt=f"{HUMAN_PROMPT} {prompt} {AI_PROMPT}",
    )
    response = completion.completion
    print(response)
    json_resp = response.split('<json>')[1].split('</json>')[0]
    return {"descriptions" : json.loads(json_resp)}
