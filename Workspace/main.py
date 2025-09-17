import requests
from typing import List

def get_sub_categories(slug: str) -> List[str]:
    """Fetches sub-categories for a given category slug."""
    url = f"https://api.digikala.com/v1/categories/{slug}/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Assume the structure is data['data']['category']['child_categories'] 
        # Each child is a dict with 'code' or 'slug', or extract from 'url'['uri']
        # Adjust based on actual structure; here assuming 'child_categories' is list of dicts with 'code' as slug
        child_categories = data.get('data', {}).get('category', {}).get('child_categories', [])
        sub_slugs = [child['code'] for child in child_categories if 'code' in child]
        return sub_slugs
    except requests.exceptions.RequestException as e:
        print(f"Error fetching categories for {slug}: {e}")
        return []
    except KeyError:
        print(f"Unexpected JSON structure for {slug}")
        return []


def get_all_categories(main_slugs: List[str]) -> List[str]:
    """Recursively gets all category slugs starting from main slugs."""
    all_slugs = []
    to_process = main_slugs[:]
    
    while to_process:
        current = to_process.pop(0)
        if current not in all_slugs:
            all_slugs.append(current)
            sub_slugs = get_sub_categories(current)
            to_process.extend(sub_slugs)
    
    return all_slugs


# List of main category slugs (compiled from sources)
main_slugs = [
    "electronic-devices",
    "home-and-kitchen",
    "apparel",
    "food-beverage",
    "book-and-media",
    "mother-and-child",
    "personal-appliance",
    "sport-entertainment",
    "vehicles",
    "vehicles-spare-parts",
    "rural-products",
    "dk-ds-gift-card"
]

# Get all categories
all_categories = get_all_categories(main_slugs)

# Print the list
print("All available category slugs:")
for slug in all_categories:
    print(slug)

# Now you can use these slugs to fetch products, e.g., https://api.digikala.com/v1/categories/{slug}/search/?page={page}