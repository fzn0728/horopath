from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from utils import *

load_dotenv() # load environment variables from .env file

app = FastAPI()

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"),)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/query")
async def query_astro_info(query: Query):
    horoscope = get_horoscope(query)
    astro_tbl = extract_astro_table(horoscope)
    aspect_tbl = extract_aspects(horoscope)
    claude_output = get_astro_summary(anthropic, astro_tbl)

    resp_json =  {**astro_tbl, **aspect_tbl, **claude_output}

    return {"response": resp_json}

@app.post("/query2")
async def query_astro_answer(q: Query2):
    claude_answer = get_astro_answer(anthropic, q)
    return claude_answer