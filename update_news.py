import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from google import genai
from google.genai import types

# 1. Setup Gemini API Client
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 2. The "Super-Scraper": Run multiple targeted Google News searches
print("Running targeted Google News sweeps...")

# These specific queries guarantee we catch niche independent/prep school news
queries = [
    '"independent school" (closure OR close OR closing OR deficit)',
    '"independent school" (merger OR merge OR merging)',
    '"prep school" (closure OR merger OR VAT)',
    'UK school (closure OR merger) -"strike" -"weather"'
]

news_dict = {}

# Fetch and combine top results from all 4 searches
for q in queries:
    url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&hl=en-GB&gl=GB&ceid=GB:en"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        root = ET.fromstring(response.read())
        for item in root.findall('.//item')[:15]: # Take top 15 from each query
            title = item.find('title').text
            link = item.find('link').text
            pubDate = item.find('pubDate').text
            # Use link as dictionary key to automatically remove duplicates
            if link not in news_dict:
                news_dict[link] = f"Title: {title}\nDate: {pubDate}\nLink: {link}"
    except Exception as e:
        print(f"Failed to fetch query '{q}': {e}")

# Combine into one massive text block for Gemini (up to 40 unique articles)
news_text = "\n\n".join(list(news_dict.values())[:40])

# 3. Your prompt, enhanced for stricter formatting
prompt = f"""Role: Act as a specialist market researcher for the UK independent education sector.

Task: I am providing you with a large master-list of recent UK school news articles. Read through them and select the 5 most important stories. The main focus is the independent (private) school sector, but highly relevant state school news must be included.

STRICT EXCLUSIONS: You MUST ignore temporary closures (e.g., strikes, weather).

Focus Areas (Prioritise PERMANENT changes):
- Permanent school closures (due to deficit, low numbers, or VAT)
- Mergers, acquisitions, or partnerships (including cancelled or delayed mergers)
- Severe financial pressures or major deficits

Output Formatting Rules:
- Provide ONLY a valid JSON array. No markdown, no intro/outro text.
- Each object must have exactly four keys: "Headline", "Date", "Info", "Link".
- "Headline": Must start with a highly descriptive category tag (e.g., "Closure", "Merger", "Merger Cancelled", "Closure & Merger Delayed"). Then the school name. You MUST append "(State School)" or "(Independent)" to the name. End with the geographic location. 
  Example: "Closure & Merger Delayed - Flintshire Catholic Schools (State Schools), North Wales"
- "Date": Standard British date format (e.g., 10 March 2026).
- "Info": A detailed 1-2 sentence summary containing specific hard facts (e.g., specific deficit amounts, pupil numbers, or VAT impacts).
- "Link": Use the exact URL provided in the raw data.

Here is the raw news data to analyze:
{news_text}
"""

print("Sending compiled data to Gemini...")

# 4. Call the API
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0.1 
    )
)

# 5. Clean up the output
output_text = response.text.strip()

if output_text.startswith("```json"):
    output_text = output_text[7:]
if output_text.startswith("```"):
    output_text = output_text[3:]
if output_text.endswith("```"):
    output_text = output_text[:-3]
    
output_text = output_text.strip()

# 6. Overwrite the JSON file
print("Saving new headlines...")
with open('headlines.json', 'w', encoding='utf-8') as f:
    f.write(output_text)
print("Update complete!")
