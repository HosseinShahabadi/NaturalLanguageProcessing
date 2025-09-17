import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://fa.wikipedia.org"
list_urls = [
    "/wiki/رده:معاهده%E2%80%8Cهای_ایران",
    '/wiki/رده:ائتلاف%E2%80%8Cهای_نظامی_ایران',
    '/wiki/رده:پیمان%E2%80%8Cنامه%E2%80%8Cهای_شاهنشاهی_ساسانی',
    '/wiki/رده:پیمان%E2%80%8Cهای_شاهنشahi_اشکانیان',
    '/wiki/رده:معاهده%E2%80%8Cهای_افشاریان',
    '/wiki/رده:معاهده%E2%80%8Cهای_دودمان_پهلوی',
    '/wiki/رده:معاهده%E2%80%8Cهای_سلسله_قاجاریان',
    '/wiki/رده:معاهده%E2%80%8Cهای_صفویان',
    '/wiki/رده:معاهده%E2%80%8Cهای_صلح_ایران',
    '/wiki/رده:معاهده%E2%80%8Cهای_معاصر_ایران',
    '/wiki/رده:معاهده%E2%80%8Cهای_هخامنشیان'
]

def get_treaty_links(category_url):
    resp = requests.get(category_url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    pages_section = soup.find('h2', string="صفحه‌ها")
    if pages_section:
        pages_div = pages_section.find_next('div', id="mw-pages")
        if not pages_div:
            pages_div = pages_section.find_next('div', class_="mw-category")
        if pages_div:
            links = pages_div.find_all('a', href=lambda href: href and href.startswith("/wiki/") and "رده:" not in href)
            return [link['href'] for link in links]
    return []

def extract_structured_data(soup):
    for ref in soup.select('sup.reference'):
        ref.decompose()

    data = {
        "title": "<TBD>",
        "description": "<TBD>",
        "period": {
            "start_year": "<TBD>",
            "end_year": "<TBD>"
        },
        "location": {
            "position": "<TBD>",
            "province": "<TBD>",
            "city": "<TBD>",
            "coordinates": {
                "latitude": 0,
                "longitude": 0
            }
        },
        "causes": ["<TBD>"],
        "belligerents": ["<TBD>"],  # Initialized as an empty list to dynamically add parties
        "result": "<TBD>",
        "casualties": {},
        "impact": ["<TBD>"],
        "historical_significance": "<TBD>",
        "references": ["<TBD>"],
        "source": {
            "title": "<TBD>",
            "author": "<TBD>",
            "publication_date": "<TBD>",
            "url": "<TBD>"
        },
        "text": "<TBD>"  # Ensure this field is initialized
    }

    # Extract title
    title_tag = soup.find('h1', {'id': 'firstHeading'})
    if title_tag:
        data["title"] = title_tag.get_text(strip=True)

    # Extract full text for keyword matching and fallback
    content_div = soup.find('div', class_='mw-parser-output')
    full_text = ""
    if content_div:
        paragraphs = content_div.find_all('p')
        for p in paragraphs:
            for sup in p.find_all("sup", class_="reference"):
                sup.decompose()
            text = p.get_text(strip=True)
            if text:
                full_text += text + "\n"
    data["text"] = full_text.strip() if full_text.strip() else "<TBD>"

    # Check if the page is treaty-related using keywords
    treaty_keywords = ["معاهده", "پیمان", "توافق", "صلح", "قرارداد"]
    is_treaty = any(keyword in data["title"] or keyword in full_text for keyword in treaty_keywords)

    # Extract description
    infobox = soup.find('table', {'class': 'infobox'})
    description = ""
    if infobox:
        next_sibling = infobox.find_next_sibling()
        while next_sibling and next_sibling.name not in ['h2', 'h3']:
            if next_sibling.name == 'p':
                description += next_sibling.get_text(strip=True) + " "
            next_sibling = next_sibling.find_next_sibling()
    data["description"] = description.strip() if description.strip() else "<TBD>"

    # Extract period
    try:
        signature_date_tag = soup.find('th', text="تاریخ امضا")
        creation_date_tag = soup.find('th', text="تاریخ ایجاد")
        if signature_date_tag:
            td = signature_date_tag.find_next('td')
            if td:
                data["period"]["start_year"] = td.get_text(strip=True).replace('–', '-').replace('—', '-')
        elif creation_date_tag:
            td = creation_date_tag.find_next('td')
            if td:
                data["period"]["start_year"] = td.get_text(strip=True).replace('–', '-').replace('—', '-')
        else:
            date_tag = soup.find('th', text="تاریخ")
            if date_tag:
                td = date_tag.find_next('td')
                if td:
                    date_data = td.get_text(strip=True).replace('–', '-').replace('—', '-')
                    years = [y.strip() for y in date_data.split('-') if y.strip()]
                    if len(years) == 2:
                        data["period"]["start_year"], data["period"]["end_year"] = years
                    elif len(years) == 1:
                        data["period"]["start_year"] = data["period"]["end_year"] = years[0]
        effective_date_tag = soup.find('th', text="تاریخ اجرا")
        if effective_date_tag:
            td = effective_date_tag.find_next('td')
            if td:
                data["period"]["end_year"] = td.get_text(strip=True).replace('–', '-').replace('—', '-')
    except Exception as e:
        print(f"Error processing dates: {e}")

    # Extract belligerents
    signatories_tag = soup.find('th', text="امضاکنندگان")
    if signatories_tag:
        td = signatories_tag.find_next('td')
        if td:
            for hr in td.find_all('hr'):
                hr.replace_with('، ')
            for br in td.find_all('br'):
                br.replace_with('، ')
            belligerents = [a.get_text(strip=True) for a in td.find_all('a') if 'title' in a.attrs and not a['href'].startswith('/wiki/پرونده:')]
            for belligerent in belligerents:
                data["belligerents"].append({"name": belligerent.strip()})
    else:
        belligerents_tag = soup.find('th', text="طرف‌ها")
        if belligerents_tag:
            belligerents_data = belligerents_tag.find_next('td').get_text(strip=True)
            belligerents = belligerents_data.replace('،', 'و').split('و')
            for belligerent in belligerents:
                belligerent = belligerent.strip()
                if belligerent:
                    data["belligerents"].append({"name": belligerent})

    # Extract result
    result_tag = soup.find('th', text="نتیجه")
    if result_tag:
        result_data = result_tag.find_next('td').get_text(strip=True)
        data["result"] = result_data if result_data else "<TBD>"

    # Extract impact
    try:
        results_tag = soup.find('th', string="نتایج")
        if results_tag:
            results_td = results_tag.find_next('td')
            if results_td:
                for ref in results_td.find_all("sup", class_="reference"):
                    ref.decompose()
                p_tag = results_td.find('p')
                if p_tag:
                    p_text = p_tag.get_text(strip=True)
                    if p_text:
                        data["impact"].append(p_text)
                for li in results_td.find_all('li'):
                    li_text = li.get_text(strip=True)
                    if li_text:
                        data["impact"].append(li_text)
    except:
        pass

    # Extract location
    try:
        signature_location_tag = soup.find('th', text="مکان امضا")
        if signature_location_tag:
            location_td = signature_location_tag.find_next('td')
            if location_td:
                for ref in location_td.find_all("sup", class_="reference"):
                    ref.decompose()
                for br in location_td.find_all("br"):
                    br.replace_with(", ")
                location_text = location_td.get_text(strip=True)
                data["location"]["position"] = location_text if location_text else "<TBD>"
        else:
            location_tag = soup.find('th', string="موقعیت")
            if location_tag:
                location_td = location_tag.find_next('td')
                if location_td:
                    for ref in location_td.find_all("sup", class_="reference"):
                        ref.decompose()
                    location_text = location_td.get_text(strip=True)
                    data["location"]["position"] = location_text if location_text else "<TBD>"
    except Exception as e:
        print(f"Error processing location: {e}")

    # Extract historical significance
    impact_tag = soup.find('span', text="اهمیت تاریخی")
    if impact_tag:
        impact_data = impact_tag.find_parent().get_text(strip=True)
        data["historical_significance"] = impact_data if impact_data else "<TBD>"

    # Extract references
    references = soup.find_all('cite')
    for ref in references[:5]:
        ref_title = ref.find('a')
        if ref_title:
            data["references"].append({
                "title": ref_title.get_text(strip=True),
                "author": ref.get_text(strip=True),
                "year": "Unknown"
            })

    # Extract source
    data["source"]["title"] = data["title"]
    data["source"]["author"] = "Wikipedia"
    data["source"]["publication_date"] = "Unknown"
    data["source"]["url"] = soup.find('link', {'rel': 'canonical'})['href'] if soup.find('link', {'rel': 'canonical'}) else "<TBD>"

    return data, is_treaty

# Collect unique treaty links from all category URLs
unique_hrefs = set()
for category_url in list_urls:
    full_category_url = BASE_URL + category_url
    links = get_treaty_links(full_category_url)
    for link in links:
        unique_hrefs.add(link)
    print(f"Found {len(links)} treaty links in {category_url}")

results = []

for idx, href in enumerate(unique_hrefs, 1):
    full_url = BASE_URL + href
    print(f"[{idx}] Processing: {full_url}")
    try:
        detail_resp = requests.get(full_url)
        detail_resp.encoding = 'utf-8'
        detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')

        structured_data, is_treaty = extract_structured_data(detail_soup)

        # Only skip if it's explicitly not a treaty based on keyword check
        if not is_treaty:
            print(f"   ⚠️ Skipping: {structured_data['title']} does not appear to be a treaty based on keyword check.")
            continue

        results.append(structured_data)
        print(f"   ✅ Successfully processed: {structured_data['title']}")

    except Exception as e:
        print(f"   ❌ Error processing {full_url}: {e}")
        continue

    time.sleep(1)  # Increased delay to be polite to Wikipedia servers

# Save final result
try:
    with open("iran_histroy_with_details.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Collected {len(results)} treaties with detailed info.")
except Exception as e:
    print(f"Error writing to JSON file: {e}")

# Log missing entries
expected_count = len(unique_hrefs)
if len(results) < expected_count:
    print(f"Warning: Expected {expected_count} treaties, but only {len(results)} were processed.")