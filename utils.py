from pydantic import BaseModel
import json
import requests
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

class Query(BaseModel):
    birthday: str
    birthtime: str
    birthplace: str

class Query2(BaseModel):
    question: str
    astro_table: dict
    aspect: dict

list_sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def get_horoscope(query: Query):
    # TODO (Renee): hard-coded to NYC coordinate for now. Find the right API for city -> coordinates
    def _convertCoordinate(bplace):
        lat = 40.7128
        lng = -74.0060
        return lat, lng

    def _convertTimeZone(lat, lng, bday, btime):
        tf = TimezoneFinder()
        # Use the timezone_at method to get the timezone name
        timezone_str = tf.timezone_at(lat=lat, lng=lng)
        time_obj = datetime.strptime(bday + btime, '%Y%m%d%H%M')
        time_obj = pytz.timezone(timezone_str).localize(time_obj)
        # Convert the localized datetime object to UTC
        time_obj_utc = time_obj.astimezone(pytz.UTC).isoformat()
        return time_obj_utc.replace('+00:00', '') + 'Z'

    BASE_URL = 'https://astrology-api-3ipo.onrender.com/horoscope'
    lati, lngi = _convertCoordinate(query.birthplace)
    time = _convertTimeZone(lati, lngi, query.birthday, query.birthtime)
    params = {
        'time': time,
        # fixed the city to be NYC for now
        'latitude': str(lati),
        'longitude': str(lngi),
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
    return list_sign_names[sign_number - 1]

def extract_astro_table(input_json):
  output_json = {
      "astro_table": []
  }
  encountered_signs = set()

  for sign_name in list_sign_names:
    astro_entry = {
          "sign": sign_name,
          "planets": [],
          "houses": []
      }

    # ADD HOUSES
    for house_idx, house_data in enumerate(input_json['data']['houses']):
        house_sign_name = get_sign_name(house_data["sign"])
        if house_sign_name == sign_name:
            astro_entry["houses"].append(house_idx+1)

    # ADD PLANETS
    for astro, astro_data in input_json["data"]["astros"].items():
        if get_sign_name(astro_data["sign"]) == sign_name:
            astro_entry["planets"].append(astro)

    # ADD ASCENDANT      
    axe_asc_data = input_json['data']['axes']['asc']
    if get_sign_name(axe_asc_data["sign"]) == sign_name:
        astro_entry["planets"].append("ascendant")

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
def get_astro_summary_prompt(input_json_astro_tbl: dict) -> str:
    json_str = json.dumps(input_json_astro_tbl, indent=4)  # For pretty print
    
    return f'''
    Hey Claude, you are an expert in horoscope. Based on the provided json regarding the planet, zodiacs and house information, can you output the sun, moon and ascendant information, in a json struct like [{{"header": "Sun in Leo", "short_summary": "A short summary about the reading on the planet", "long_description": "A long description expanding on the short summary"}}, {{...}}]?

    Input info:

    {json_str}

    Output json (Please wrap the json code with <json>):
    '''

def get_astro_answer_prompt(q:Query2) -> str:
    astro_tbl_str = json.dumps(q.astro_table)
    aspect_str = json.dumps(q.aspect)

    return f'''
    Hey Claude! you are an expert in horoscope and very inspirational helper that try to give people encouragement and guide them through their problems. Given the user sign/planet/house/aspect information, as well as the input question, can you curated answers to user's question? Be sure to use the horoscope knowledge to answer, and the tune should be positive. Answer in below json construct: [{{"short_summary": "a short summary of your answer", "long_description": "a more elaborated version of your answer"}}]

    User's sign: {astro_tbl_str}
    User's aspect: {aspect_str}
    User's question: {q.question}

    Output json (Please wrap the json code with <json>):
    '''

def get_astro_summary(anthropic_session, input_json_astro_tbl):
    prompt = get_astro_summary_prompt(input_json_astro_tbl)
    
    completion = anthropic_session.completions.create(
        model="claude-2",
        max_tokens_to_sample=1000,
        prompt=f"{HUMAN_PROMPT} {prompt} {AI_PROMPT}",
    )
    response = completion.completion
    json_resp = response.split('<json>')[1].split('</json>')[0]
    return {"descriptions" : json.loads(json_resp)}

def get_astro_answer(anthropic_session, q):
    prompt = get_astro_answer_prompt(q)
    
    completion = anthropic_session.completions.create(
        model="claude-2",
        max_tokens_to_sample=1000,
        prompt=f"{HUMAN_PROMPT} {prompt} {AI_PROMPT}",
    )
    response = completion.completion
    json_resp = response.split('<json>')[1].split('</json>')[0]
    return {"answer" : json.loads(json_resp)}
