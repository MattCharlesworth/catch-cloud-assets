import os
from google import genai
from google.genai import types

# 1. Setup Gemini API Client using the new SDK
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 2. Your exact prompt
prompt = """Role: Act as a specialist market researcher for the UK independent education sector.

Task: Search the web for news published strictly within the last 7 days regarding UK schools. While the main focus should be on news that interests the independent (private) school sector, do not strictly limit results to independent schools. Highly relevant news regarding state schools (such as state school closures, capacity issues, or local demographic shifts) should also be included.

Focus Areas: Prioritise news involving operational and structural changes, specifically:
- School closures or potential closures (both independent and state schools)
- Mergers, acquisitions, or partnerships
- Severe financial pressures or significant fee restructuring
- Major leadership changes or restructuring

Source Requirements: Do not limit your search to major national outlets (e.g., BBC, The Times, Telegraph). You must actively search local and regional UK news sites (e.g., Chronicle Live, regional publishers) and specialist education press (e.g., Independent Education Today, Tes) to capture grassroots sector shifts.

Language Requirement: All responses must be written in standard British English spelling and grammar (e.g., categorise, programme, centre).

Output Formatting Rules:
- Provide only the results formatted as a valid JSON array.
- Absolutely no conversational filler, introductory text, markdown formatting outside of the JSON block, or concluding remarks.
- Each result must be a single JSON object within the array containing exactly four keys: "Headline", "Date", "Info", and "Link".
- "Headline": Must be short and concise. It must start with a relevant category tag (e.g., "Closure - ", "Merger - ", "Financial - ", "News - "), followed by the school name, and must include a suitable geographic location (e.g., city or county). Indicate if it is a state school if applicable.
- "Date": The publication date of the news article, written in a standard British date format (e.g., 10 March 2026).
- "Info": A 1-2 sentence summary providing slightly more detail on the core event.
- "Link": The direct URL to the source article.
"""

print("Sending prompt to Gemini with Live Search enabled...")

# 3. Call the API using the new modern configuration
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2
    )
)

# 4. Clean up the output
output_text = response.text.strip()

# Strip markdown if Gemini adds it
if output_text.startswith("```json"):
    output_text = output_text[7:]
if output_text.startswith("```"):
    output_text = output_text[3:]
if output_text.endswith("```"):
    output_text = output_text[:-3]
    
output_text = output_text.strip()

# 5. Overwrite the JSON file
print("Saving new headlines...")
with open('headlines.json', 'w', encoding='utf-8') as f:
    f.write(output_text)
print("Update complete!")
