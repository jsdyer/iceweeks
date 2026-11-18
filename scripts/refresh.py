"""Index published weekly concentration charts in the International Ice Charting Working Group portal."""
from calendar import monthrange
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "web/data/index.json"
PORTAL = "https://www.icelogistics.info/ice-charts"


class ChartScripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_script = False
        self.data = []

    def handle_starttag(self, tag, attrs):
        self.in_script = tag == "script"

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False

    def handle_data(self, text):
        prefix = "self.__next_f.push("
        if self.in_script and text.startswith(prefix):
            payload = json.loads(text[len(prefix):].rstrip(");"))[1]
            if isinstance(payload, str) and '"currentPageData":' in payload:
                self.data.append(json.JSONDecoder().raw_decode(payload.split('"currentPageData":', 1)[1])[0])


def parse(page, start, end):
    parser = ChartScripts()
    parser.feed(page)
    if len(parser.data) != 1:
        raise ValueError("Unrecognized chart catalogue")
    rows = []
    for item in parser.data[0]:
        issued = date.fromisoformat(item["issueDate"][:10])
        if item["providerShortName"] != "CIS" or str(item["productId"]) != "2213" or not start <= issued <= end:
            raise ValueError("Unexpected provider, series or date")
        assets = {a['role']: a['href'] for a in item["assets"]}
        links = [assets["quicklook"], assets["product"]]
        if any(urlsplit(u).scheme != 'https' or urlsplit(u).hostname != 'www.polarview.aq' for u in links):
            raise ValueError("Unexpected chart asset origin")
        rows.append(dict(date=issued.isoformat(), id=item["itemName"], image=links[0], pdf=links[1]))
    return rows


def fetch(window):
    start, end = window
    url = PORTAL + "?" + urlencode(dict(dateRange=f"{start}/{end}", iceChartProductId="2213"))
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={"User-Agent":"CoolCode Ice Weeks/1.0"}), timeout=35) as res:
                return parse(res.read(4_000_000).decode(), start, end)
        except OSError:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)


def main():
    today = datetime.now(timezone.utc).date()
    windows = []
    for year in range(2023, today.year + 1):
        for month in (12, 1, 2, 3, 4):
            season_year = year if month == 12 else year + 1
            start = date(season_year, month, 1)
            if start <= today:
                windows.append((start, min(today, date(season_year, month, monthrange(season_year, month)[1]))))
    with ThreadPoolExecutor(max_workers=3) as pool:
        charts = sorted((c for batch in pool.map(fetch, windows) for c in batch), key=lambda c:c['date'])
    if len(charts) < 12 or len({x['date'] for x in charts}) != len(charts):
        raise ValueError("Insufficient or duplicate chart dates")
    if INDEX.exists():
        old = json.loads(INDEX.read_text())
        if not {x['date'] for x in old['charts']}.issubset(c['date'] for c in charts):
            raise ValueError("Listings lost prior dates; review the archive before replacing them")
    result = dict(retrieved=str(today), count=len(charts), first=charts[0]['date'], latest=charts[-1]['date'], charts=charts)
    tmp = INDEX.with_suffix('.tmp')
    tmp.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
    tmp.replace(INDEX)
    print(len(charts),result['first'],result['latest'])


if __name__ == "__main__":
    main()
