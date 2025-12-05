from variables import *
from bs4 import BeautifulSoup
import bs4
import requests
import json

def parse_index_html(html:str):
    soup = BeautifulSoup(html, "html.parser")
    gunluk_yemek = soup.find("section", id="gunluk_yemek")
    yemekler = gunluk_yemek.find_all("li")

    results = []
    for yemek in yemekler:
        results.append(parse_yemek_html(yemek))

    return results

def parse_yemek_html(tag:bs4.Tag):
    # 1) Resim kaynağı
    img_src = tag.find("img")["src"]

    # 2) Malzemeler + kalori (ID yerine class seçiyoruz)
    content_div = tag.find("div", class_="tp-caption FoodCarousel-Content tp-resizeme")
    lines = content_div.get_text("\n", strip=True).split("\n")

    title = lines[0]
    kcal = " ".join(lines[-2:])
    ingredients = lines[1:-2]

    return {"img":img_src, "title":title, "ingredients":ingredients, "kcal":kcal}

def send_discord(data_dict:dict):
    files = {
        "img":open(cache_folder / data_dict["img"], "rb")
    }
    ingredients_text = "\n".join(f"- {x}" for x in data_dict["ingredients"])

    data = {"embeds": [{
        "title": data_dict["title"],
        "image": {"url": f"attachment://img"},
        "fields": [{
        "name": "Malzemeler",
        "value": ingredients_text,
        },{
          "name": "Kalori",
          "value": data_dict["kcal"],
          "inline": True}],
    "color": 16742400}]}

    requests.post(CU_YEMEKHANE, files=files, data={"payload_json": json.dumps(data)})

def main():
    index_html = requests.get(CU_YEMEKHANE_URL).text
    result = parse_index_html(index_html)

    with open(cache_folder / "yemekler.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    for res in result:
        img_path:Path = cache_folder / res["img"]
        if not img_path.exists():
            response = requests.get(CU_YEMEKHANE_URL+res["img"])
            with open(img_path, "wb") as f:
                f.write(response.content) 
        send_discord(res)

if __name__ == "__main__":
    main()


