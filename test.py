from dotenv import load_dotenv
import os
from utils import *

load_dotenv() # load environment variables from .env file

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"),)

def main():
    # Here you need to define what Query is before using it
    # For instance, if it is a class you have defined, you might need to create an instance of it
    # Query = YourClass()
    horoscope = get_horoscope(Query)
    astro_tbl = extract_astro_table(horoscope)
    aspect_tbl = extract_aspects(horoscope)
    claude_output = get_top_summary(anthropic, astro_tbl)

    resp_json =  {**astro_tbl, **aspect_tbl, **claude_output}
    print(resp_json)

if __name__ == "__main__":
    main()