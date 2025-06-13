import os
import re
import json
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://centrocoasting.com"
NICARAGUA_PAGE = urljoin(BASE_URL, "nicaragua/")
OUTPUT_DIR = os.path.join("data", "json_routes")

# Matches times like 5:30 am, 17:45, 6am, etc.
TIME_REGEX = re.compile(r"\b((?:[01]?\d|2[0-3])[:h][0-5]\d(?:\s*(?:am|pm))?|(?:[01]?\d|2[0-3])\s*(?:am|pm))", re.I)


def get_city_links():
    """Return dict mapping city name to url."""
    resp = requests.get(NICARAGUA_PAGE, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    cities = {}
    for city_div in soup.select("div.city"):
        link = city_div.find("a")
        name_tag = city_div.find("h3")
        if link and name_tag:
            url = urljoin(BASE_URL, link.get("href"))
            name = name_tag.get_text(strip=True)
            cities[name] = url
    return cities


def parse_city_page(name, url):
    """Parse routes for a single city."""
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    routes = []
    for header in soup.find_all("h2"):
        route_name = header.get_text(strip=True)
        if not route_name or "help your fellow" in route_name.lower():
            continue
        text_parts = []
        for sib in header.find_next_siblings():
            if sib.name == "h2":
                break
            if sib.name in {"p", "ul", "ol"}:
                text_parts.append(sib.get_text(" ", strip=True))
        text = " ".join(text_parts)
        times = TIME_REGEX.findall(text)
        times_clean = []
        for t in times:
            t = t.replace("h", ":")
            t = t.replace("AM", " am").replace("PM", " pm")
            times_clean.append(t.strip())
        stops = []
        via = re.search(r"via\s+([A-Za-z\s,]+)", text)
        if via:
            stops = [s.strip() for s in re.split(r",| and ", via.group(1)) if s.strip()]
        route = {
            "region": name,
            "ruta": route_name.replace(" to ", " - "),
            "operador": None,
            "frecuencia": None,
            "salidas": [{"hora": h, "desde": name, "hacia": None} for h in times_clean],
            "paradas": stops,
        }
        routes.append(route)
    return routes


def save_routes(routes):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for route in routes:
        slug = route["ruta"].replace(" ", "_").replace("/", "-")
        path = os.path.join(OUTPUT_DIR, f"{slug}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(route, f, ensure_ascii=False, indent=2)


def scrape_all():
    cities = get_city_links()
    for name, url in cities.items():
        try:
            routes = parse_city_page(name, url)
            for route in routes:
                save_routes([route])
        except Exception as exc:
            print(f"Failed to scrape {name}: {exc}")


if __name__ == "__main__":
    scrape_all()
