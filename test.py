from dotenv import load_dotenv
import os
from utils import *

load_dotenv() # load environment variables from .env file

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"),)

def main():
    query = Query(
        birthday="19900101",
        birthtime="1200",
        birthplace="New York, USA"
    )

    horoscope = get_horoscope(query)
    astro_tbl = extract_astro_table(horoscope)
    aspect_tbl = extract_aspects(horoscope)
    claude_summary = get_astro_summary(anthropic, astro_tbl)

    resp_json =  {**astro_tbl, **aspect_tbl, **claude_summary}

    user_question = "Hi, I just started a new relationship and it's been a bit tough. Can you tell me how would my relationship go? What should I do?"
    query2 = Query2(
        question = user_question,
        astro_table = astro_tbl,
        aspect = aspect_tbl
    )
    claude_answer = get_astro_answer(anthropic, query2)

if __name__ == "__main__":
    main()