import os
import json
import requests
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# 1. Setup Gemini API Client
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 2. Read the EXISTING headlines so we don't overwrite them
existing_headlines = []
if os.path.exists('headlines.json'):
    try:
        with open('headlines.json', 'r', encoding='utf-8') as f:
            existing_headlines = json.load(f)
    except Exception as e:
        print(f"Could not read existing headlines: {e}")

# 3. Your Full Masterclass Prompt (Adapted for the 24-hour rolling window)
prompt = """Role: Act as a specialist market researcher for the UK independent education sector.

Task: Search the web using Google Search for news published STRICTLY WITHIN THE LAST 24 HOURS regarding UK schools. While the main focus should be on news that interests the independent (private) school sector, do not strictly limit results to independent schools. Highly relevant news regarding state schools (such as state school closures, capacity issues, or local demographic shifts) should also be included.

CRITICAL EXCLUSIONS - READ CAREFULLY:
You MUST completely ignore any news about temporary closures. 
If an article mentions "strike", "strikes", "industrial action", "EIS", "NEU", "teachers union", "weather", "snow", "boiler", or "repairs", you MUST DISCARD IT entirely. Do not include it.

Focus Areas: Prioritise news involving operational and structural changes, specifically:
- School closures or potential closures (both independent and state schools)
- Mergers, acquisitions, or partnerships
- Severe financial pressures or significant fee restructuring
- Major leadership changes or restructuring

Source Requirements: Do not limit your search to major national outlets (e.g., BBC, The Times, Telegraph). You must actively search local and regional UK news sites (e.g., Chronicle Live, regional publishers) and specialist education press (e.g., Independent Education Today, Tes) to capture grassroots sector shifts.

Language Requirement: All responses must be written in standard British English spelling and grammar (e.g., categorise, programme, centre).

Output Formatting Rules:
- Provide only the results formatted as a valid JSON array. If there is no relevant news from the past 24 hours, output an empty array: []
- Absolutely no conversational filler, introductory text, markdown formatting outside of the JSON block, or concluding remarks.
- Each result must be a single JSON object within the array containing exactly four keys: "Headline", "Date", "Info", and "Link".
- "Headline": Must be short and concise. It must start with a relevant category tag (e.g., "Closure - ", "Merger - ", "Financial - ", "News - "), followed by the school name, and must include a suitable geographic location (e.g., city or county). Indicate if it is a state school if applicable.
- "Date": The publication date of the news article, written in a standard British date format exactly like this: "10 March 2026".
- "Info": A 1-2 sentence summary providing slightly more detail on the core event.
- "Link": The direct URL to the source article.

Example Format:
[
  {
    "Headline": "Closure - Alderley Edge School for Girls, Cheshire",
    "Date": "18 February 2026",
    "Info": "Alderley Edge School for Girls has proposed the permanent closure of its entire operation at the end of the current academic year due to significant financial pressures exacerbated by the introduction of VAT on fees.",
    "Link": "https://www.manchestereveningnews.co.uk/news/greater-manchester-news/top-private-school-cheshire-set-33487647"
  },
  {
    "Headline": "Closure - St Mary's Primary (State), London",
    "Date": "9 March 2026",
    "Info": "The local council has announced the potential closure of St Mary's Primary due to falling pupil numbers in the borough, a demographic shift that may impact local independent feeder schools.",
    "Link": "https://www.mylondon.news/news/local-school-closures-london-pupils-12345678"
  }
]
"""

print("Fetching news from the past 24 hours...")

response = client.models.generate_content(
    model='gemini-3.1-pro-preview',
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.1
    )
)

# Clean up the output string
output_text = response.text.strip()
if output_text.startswith("
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1
http://googleusercontent.com/immersive_entry_chip/2

Update your GitHub file with this one, and you will have the absolute best of both worlds: the strict formatting and rules of your original masterclass prompt, powered by the 3.1 Pro engine, seamlessly maintaining a rolling 7-day feed.
