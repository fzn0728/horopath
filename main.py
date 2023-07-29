from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

load_dotenv() # load environment variables from .env file

app = FastAPI()

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"),)


@app.get("/")
async def root():
    return {"message": "Hello World"}


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

    return {"response": completion.completion}