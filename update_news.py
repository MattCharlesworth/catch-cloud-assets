import os
import json
import requests
from google import genai
from google.genai import types

# 1. Setup Gemini API Client
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 2. Your exact prompt, using the Web-Chat methodology
prompt = """Role: Act as a specialist market researcher for the UK independent education sector.

Task: Search the web using Google Search for news published STRICTLY WITHIN THE LAST 7 DAYS regarding UK schools. While the main focus should be on news that interests the independent (private) school sector, do not strictly limit results to independent schools. Highly relevant news regarding state schools (such as state school closures, capacity issues, or local demographic shifts) should also be included.

Focus Areas: Prioritise news involving operational and structural changes, specifically:
- School closures or potential closures (both independent and state schools)
- Mergers, acquisitions, or partnerships
- Severe financial pressures or significant fee restructuring
- Major leadership changes or restructuring

Source Requirements: Do not limit your search to major national outlets. You must actively search local and regional UK news sites.

Language Requirement: All responses must be written in standard British English spelling and grammar.

Output Formatting Rules:
- Provide only the results formatted as a valid JSON array.
- Absolutely no conversational filler, introductory text, markdown formatting outside of the JSON block, or concluding remarks.
- DO NOT include any citation markers (e.g., [1], [2]) inside the text.
- Each result must be a single JSON object within the array containing exactly four keys: "Headline", "Date", "Info", and "Link".
- "Headline": Must be short and concise. It must start with a relevant category tag (e.g., "Closure - ", "Merger - ", "Financial - ", "News - "), followed by the school name, and must include a suitable geographic location (e.g., city or county). Indicate if it is a state school if applicable.
- "Date": The publication date of the news article, written in a standard British date format (e.g., 10 March 2026).
- "Info": A 1-2 sentence summary providing slightly more detail on the core event.
- "Link": The direct URL to the source article.
"""

print("Sending prompt to Gemini with Live Search enabled...")

# 3. Call the API using the Live Search tool
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2
    )
)

# 4. Clean up the output string
output_text = response.text.strip()

if output_text.startswith("```json"):
    output_text = output_text[7:]
if output_text.startswith("```"):
    output_text = output_text[3:]
if output_text.endswith("```"):
    output_text = output_text[:-3]
    
output_text = output_text.strip()

# 5. Clean the ugly Google Tracking URLs automatically
print("Cleaning up tracking URLs...")
try:
    data = json.loads(output_text)
    for item in data:
        ugly_url = item.get("Link", "")
        # If the API gave us an ugly tracking link, we resolve it to the real publisher link
        if "vertexaisearch.cloud.google.com" in ugly_url or "[google.com/url](https://google.com/url)" in ugly_url:
            try:
                r = requests.get(ugly_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                item["Link"] = r.url
            except Exception:
                pass # If it fails to unfurl, keep the original link
    
    # Re-encode back to formatted text
    output_text = json.dumps(data, indent=2)
except Exception as e:
    print(f"URL cleaning skipped due to JSON parsing error: {e}")

# 6. Overwrite the JSON file
print("Saving new headlines...")
with open('headlines.json', 'w', encoding='utf-8') as f:
    f.write(output_text)
print("Update complete!")
