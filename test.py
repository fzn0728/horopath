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
    claude_output = get_astro_summary(anthropic, astro_tbl)

    resp_json =  {**astro_tbl, **aspect_tbl, **claude_output}

if __name__ == "__main__":
    main()