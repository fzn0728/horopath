from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

load_dotenv() # load environment variables from .env file

app = FastAPI()

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"),)


@app.get("/")
async def root():
    return {"message": "Hello World"}


def get_horoscope():
    BASE_URL = 'https://astrology-api-3ipo.onrender.com/horoscope'

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
    print(data)
    return data

class Query(BaseModel):
    birthday: str
    birthtime: str
    birthplace: str


@app.post("/query")
async def query_anthropic(query: Query):
    prompt = f"""
        Hi Claude!
        My birthday is {query.birthday},
        my birthtime is {query.birthtime},
        my birthplace is {query.birthplace}.
        Can you give me my horoscope details?
        Including my Zodiacs, houses and aspects.
    """
    completion = anthropic.completions.create(
        model="claude-2",
        max_tokens_to_sample=1000,
        prompt=f"{HUMAN_PROMPT} {prompt} {AI_PROMPT}",
    )
    print(completion.completion)

    horoscope = get_horoscope()
    print(horoscope)

    return {"response": completion.completion}