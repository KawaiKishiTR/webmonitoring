from .variables import *
import requests
from bs4 import BeautifulSoup
import json
import bs4


def send_discord(url: str, data: dict):
    payload = {
        "embeds": [
            {
                "title": data["title"],
                "url": data["url"],
                "description": data["date"],
                "color": 0xFF0000
            }
        ]
    }
    requests.post(url, json=payload)


class WebsiteMonitor:
    CACHE_ROOT = cache_folder / "websites"

    def __init__(self, url: str):
        self.url = url
        self.cache_dir = WebsiteMonitor.CACHE_ROOT / url.split("//", 1)[1].replace("/", "-")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "last_announcement.json"

        WebsiteMonitor.CACHE_ROOT.mkdir(exist_ok=True)

        self.html = None
        self.announcements = []

    # -------------------------
    # 1) HTML GET
    # -------------------------
    def fetch(self):
        try:
            response = requests.get(self.url, timeout=5)
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            return False
        
        if response.status_code != 200:
            print(f"Hata: HTTP {response.status_code}")
            return False
        
        self.html = response.text
        return True

    # -------------------------
    # 2) PARSE
    # -------------------------
    def parse(self):
        if not self.html:
            return
        
        soup = BeautifulSoup(self.html, "html.parser")
        block = soup.find("ul", class_="search-results__links")
        if not block:
            print("Duyuru listesi bulunamadı!")
            return

        ann_list = block.find_all("li")

        results = []
        for a in ann_list:
            item = self._parse_single(a)
            if item:
                results.append(item)

        self.announcements = results

    @staticmethod
    def _parse_single(node: bs4.Tag):
        try:
            # Title
            title = node.find("a", class_="search-results-links__title").get_text(strip=True)

            # URL (Kasıtlı tasarım: text'ten çekiliyor)
            url_text = node.find("a", class_="search-results-links__url").get_text(strip=True)

            # Tarih
            date_text = node.find("small").get_text(strip=True)
            start, stop = [x.strip() for x in date_text.split("/")]

            return {
                "title": title,
                "url": url_text,       # isteğin doğrultusunda burada düz metin
                "date": f"{start} / {stop}"
            }
        except Exception as e:
            print(f"Parse hatası: {e}")
            return None

    # -------------------------
    # 3) CACHE YÖNETİMİ
    # -------------------------
    def load_cache(self):
        if not self.cache_file.exists():
            return None
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None

    def save_cache(self, data):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # -------------------------
    # 4) ANA AKIŞ
    # -------------------------
    def run(self):
        if not self.fetch():
            return

        self.parse()
        if not self.announcements:
            return

        last_sent = self.load_cache()

        if last_sent and last_sent in self.announcements:
            idx = self.announcements.index(last_sent)
            new_items = self.announcements[:idx]
        else:
            new_items = self.announcements

        # En eski yeni duyurudan başlayarak gönder
        for item in reversed(new_items):
            send_discord(CU_DUYURU, item)

        # En son duyuruyu cache’e yaz
        self.save_cache(self.announcements[0])

def main():
    for url in CU_DUYURU_URLS:
        WebsiteMonitor(url).run()

if __name__ == "__main__":
    main()