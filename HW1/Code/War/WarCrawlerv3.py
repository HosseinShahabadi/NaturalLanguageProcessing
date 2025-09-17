import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://fa.wikipedia.org"
MAIN_URL = BASE_URL + "/wiki/فهرست_جنگ‌های_ایران"


def extract_structured_data(soup):
    # Remove reference superscripts (e.g. [1], [2])
    for ref in soup.select('sup.reference'):
        ref.decompose()

    # Template for storing extracted data
    data = {
        "title": "",
        "description": "",
        "period": {"start_year": "", "end_year": ""},
        "position": "",
        "causes": [],
        "belligerents": {"names": "", "leaders": ""},
        "result": "",
        "casualties": {},
        "impact": "",
        "historical_significance": "",
        "references": [],
        "source": {
            "title": "", "author": "", "publication_date": "", "url": ""
        }
    }

    # ====================== Extract title ======================
    title_tag = soup.find('h1', {'id': 'firstHeading'})
    if title_tag:
        data["title"] = title_tag.get_text(strip=True)

    # ====================== Extract description ======================
    print(f"Working on description ...")
    infobox = soup.find('table', {'class': 'infobox'})
    description = ""
    if infobox:
        next_sibling = infobox.find_next_sibling()
        while next_sibling and next_sibling.name not in ['h2', 'h3']:
            if next_sibling.name == 'p':
                description += next_sibling.get_text(strip=True) + " "
            next_sibling = next_sibling.find_next_sibling()
    if description:
        data["description"] = description.strip()

    # ====================== Extract period (date) ======================
    print(f"Working on period ...")
    try:
        date_tag = soup.find('th', text="تاریخ")
        if date_tag:
            td = date_tag.find_next('td')
            if td:
                date_data = td.get_text(strip=True).replace('–', '-').replace('—', '-')
                is_bc = 'پ.م' in date_data or 'پیش' in date_data
                years = [y.strip() for y in date_data.split('-') if y.strip()]
                if len(years) == 2:
                    data["period"]["start_year"], data["period"]["end_year"] = years
                elif len(years) == 1:
                    data["period"]["start_year"] = data["period"]["end_year"] = years[0]
    except:
        pass

    # ====================== Extract location ======================
    try:
        location_tag = soup.find('th', string="موقعیت")
        if location_tag:
            location_td = location_tag.find_next('td')
            for ref in location_td.find_all("sup", class_="reference"):
                ref.decompose()
            data["location"]["position"] = location_td.get_text(strip=True)
    except:
        pass
    
    # ====================== Extract belligerents ======================
    belligerents_tag = soup.find('th', text="طرف‌ها")
    if belligerents_tag:
        belligerents_data = belligerents_tag.find_next('td').get_text(strip=True)
        belligerents = belligerents_data.split('و')
        for i, belligerent in enumerate(belligerents[:2]):
            data["belligerents"][i]["name"] = belligerent.strip()

    # ====================== Extract result ======================
    result_tag = soup.find('th', text="نتیجه")
    if result_tag:
        data["result"] = result_tag.find_next('td').get_text(strip=True)

    # ====================== Extract impact ("نتایج") ======================
    try:
        results_tag = soup.find('th', string="نتایج")
        if results_tag:
            results_td = results_tag.find_next('td')
            for ref in results_td.find_all("sup", class_="reference"):
                ref.decompose()
            p_tag = results_td.find('p')
            if p_tag:
                data["impact"].append(p_tag.get_text(strip=True))
            for li in results_td.find_all('li'):
                data["impact"].append(li.get_text(strip=True))
    except:
        pass

    # ====================== Extract commanders ("فرماندهان و رهبران") ======================
    try:
        commanders_tag = soup.find('th', string="فرماندهان و رهبران")
        if commanders_tag:
            commanders_td = commanders_tag.find_next('td')
            for ref in commanders_td.find_all("sup", class_="reference"):
                ref.decompose()
            commanders = [c.strip() for c in commanders_td.get_text(separator="|", strip=True).split('|')]
            for i, commander in enumerate(commanders[:2]):
                data["belligerents"][i]["leader"] = commander
    except:
        pass

    # ====================== Extract casualties ("تلفات و خسارات") ======================
    try:
        casualties_tag = soup.find('th', string="تلفات و خسارات")
        if casualties_tag:
            casualties_td = casualties_tag.find_next('td')
            for ref in casualties_td.find_all("sup", class_="reference"):
                ref.decompose()
            casualties = [c.strip() for c in casualties_td.get_text(separator="|", strip=True).split('|')]
            if len(casualties) == 2:
                data["casualties"]["side_1"] = casualties[0]
                data["casualties"]["side_2"] = casualties[1]
            else:
                data["casualties"]["summary"] = " - ".join(casualties)
    except:
        pass

    # ====================== Extract historical significance ======================
    impact_tag = soup.find('span', text="اهمیت تاریخی")
    if impact_tag:
        data["historical_significance"] = impact_tag.find_parent().get_text(strip=True)

    # ====================== Extract references ======================
    citation = 0
    for ref in soup.find_all('cite'):
        ref_title = ref.find('a')
        if ref_title:
            data["references"].append({
                "title": ref_title.get_text(strip=True),
                "author": ref.get_text(strip=True),
                "year": "Unknown"
            })
            
        citation += 1
        if citation > 5:
            break

    # ====================== Extract source ======================
    data["source"]["title"] = data["title"]
    data["source"]["author"] = "Wikipedia"
    data["source"]["publication_date"] = "Unknown"
    data["source"]["url"] = soup.find('link', {'rel': 'canonical'})['href'] if soup.find('link', {'rel': 'canonical'}) else MAIN_URL

    # ====================== Normalize missing fields ======================
    for key, value in data.items():
        if not value:
            data[key] = [] if isinstance(value, list) else {} if isinstance(value, dict) else "نامشخص"

    return data


# ====================== Main execution ======================
resp = requests.get(MAIN_URL)
resp.encoding = 'utf-8'
soup = BeautifulSoup(resp.text, 'html.parser')

# Get table of wars
table = soup.find('table', {'class': 'wikitable'})
headers = [th.text.strip() for th in table.find_all('tr')[0].find_all('th')]

results = []

# Iterate through table rows
for idx, row in enumerate(table.find_all('tr')[1:], 1):
    cells = row.find_all(['td', 'th'])
    if len(cells) != len(headers):
        continue

    item = {}
    for i, header in enumerate(headers):
        text = cells[i].get_text(strip=True)
        link_tag = cells[i].find('a')
        item[header] = text
        if i == 0 and link_tag and link_tag.get('href'):
            item['link'] = BASE_URL + link_tag['href']

    print(f"[{idx}] Processing: {item.get(headers[0], 'Unknown')}")
    if 'link' in item:
        try:
            print(f"   ↪ Fetching details from: {item['link']}")
            detail_resp = requests.get(item['link'])
            detail_resp.encoding = 'utf-8'
            detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
            for ref in detail_soup.select('sup.reference'):
                ref.decompose()

            structured_data = extract_structured_data(detail_soup)

            # Override result with summary from table (4th column)
            if len(cells) >= 4:
                result_cell = cells[3]
                for ref in result_cell.select('sup.reference'):
                    ref.decompose()
                bold_tag = result_cell.find('b')
                ul_tag = result_cell.find('ul')
                result_text = ""
                if bold_tag:
                    title = bold_tag.get_text(strip=True)
                    description = ul_tag.find('li').get_text(strip=True) if ul_tag and ul_tag.find('li') else ""
                    result_text = f"{title}: {description}" if description else title
                else:
                    result_text = result_cell.get_text(strip=True)
                if result_text:
                    structured_data["result"] = result_text

            # Extract full article text for LLM or NLP purposes
            content_div = detail_soup.find('div', {'class': 'mw-parser-output'})
            if content_div:
                structured_data['text'] = "\n".join(tag.get_text(strip=True) for tag in content_div.find_all(['p', 'h2', 'h3']) if tag.get_text(strip=True))

            results.append(structured_data)

        except Exception as e:
            print(f"   ❌ Error fetching detail page: {e}")

        time.sleep(0.2)

        # Limit for testing (can remove for full scrape)
        # if len(results) > 10:
        #     break

# ====================== Save results to JSON ======================
with open("iran_wars_with_details.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Collected {len(results)} wars with detailed info.")
