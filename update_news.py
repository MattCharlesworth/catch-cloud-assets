import os
import urllib.request
import xml.etree.ElementTree as ET
from google import genai
from google.genai import types

# 1. Setup Gemini API Client
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 2. Fetch raw news, actively filtering OUT the word "strike" using Google search operators
print("Fetching raw news data...")
url = "https://news.google.com/rss/search?q=UK+school+(closure+OR+merger+OR+VAT+OR+deficit+OR+independent)+-strike+-strikes+-weather&hl=en-GB&gl=GB&ceid=GB:en"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = urllib.request.urlopen(req)
root = ET.fromstring(response.read())

news_items = []
# Grab the top 25 articles to give Gemini a wide pool of data
for item in root.findall('.//item')[:25]: 
    title = item.find('title').text
    link = item.find('link').text
    pubDate = item.find('pubDate').text
    news_items.append(f"Title: {title}\nDate: {pubDate}\nLink: {link}")

news_text = "\n\n".join(news_items)

# 3. Your updated prompt with strict exclusions
prompt = f"""Role: Act as a specialist market researcher for the UK independent education sector.

Task: I am providing you with a list of recent UK school news articles. Read through them and select the 5 most important stories. While the main focus should be on news that interests the independent (private) school sector, highly relevant news regarding state schools should also be included.

STRICT EXCLUSIONS: You MUST ignore any news about temporary closures. Do NOT include closures due to strikes, industrial action, weather, or short-term emergencies. 

Focus Areas: Prioritise news involving PERMANENT operational and structural changes, specifically:
- Permanent school closures (e.g., due to deficit, dropping student numbers, or VAT rollout)
- Mergers, acquisitions, or partnerships (including cancelled or delayed mergers)
- Severe financial pressures, major deficits, or significant fee restructuring
- Major leadership changes or structural overhauls

Language Requirement: All responses must be written in standard British English spelling and grammar (e.g., categorise, programme, centre).

Output Formatting Rules:
- Provide only the results formatted as a valid JSON array.
- Absolutely no conversational filler, introductory text, markdown formatting outside of the JSON block, or concluding remarks.
- Each result must be a single JSON object within the array containing exactly four keys: "Headline", "Date", "Info", and "Link".
- "Headline": Must be short and concise. It must start with a relevant category tag (e.g., "Closure - ", "Merger - ", "Financial - ", "News - "), followed by the school name, and must include a suitable geographic location (e.g., city or county). Indicate if it is a state school if applicable.
- "Date": The publication date of the news article, written in a standard British date format (e.g., 10 March 2026).
- "Info": A 1-2 sentence summary providing slightly more detail on the core event (e.g., mention the deficit amount, pupil numbers, or VAT impact if applicable).
- "Link": Use the exact URL provided in the raw data.

Here is the raw news data to analyze:
{news_text}
"""

print("Sending curated list to Gemini...")

# 4. Call the API
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0.1 # Lowered slightly to make it even more strictly compliant with your rules
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
