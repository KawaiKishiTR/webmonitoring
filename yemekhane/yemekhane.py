from yemekhane.variables import *
from bs4 import BeautifulSoup
import bs4
import requests
import json
from core.massage import DiscordMessage, DiscordEmbedMessage, DiscordEmbedImg, DiscordEmbedMsgField, DiscordMsgImgDict, AttachmentRef

def parse_index_html(html:str):
    soup = BeautifulSoup(html, "html.parser")
    gunluk_yemek = soup.find("section", id="gunluk_yemek")
    yemekler = gunluk_yemek.find_all("li")

    return [parse_yemek_html(yemek) for yemek in yemekler]

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

def create_discord_massage(data_dict:dict):
    ingredients_text = "\n".join(f"- {x}" for x in data_dict["ingredients"])
    
    msg =  DiscordMessage(
        CU_YEMEKHANE,
        DiscordMsgImgDict(
            {"img":open(cache_folder / data_dict["img"], "rb")}
        ),
        [DiscordEmbedMessage(
            data_dict["title"],
            DiscordEmbedImg(AttachmentRef("img")),
            [
                DiscordEmbedMsgField("Malzemeler", ingredients_text),
                DiscordEmbedMsgField("Kalori", data_dict["kcal"], True)
            ],
        )]
    )
    return msg

def main():
    index_html = requests.get(CU_YEMEKHANE_URL).text
    result = parse_index_html(index_html)

    with open(cache_folder / "yemekler.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    massages = []

    for res in result:
        img_path:Path = cache_folder / res["img"]
        if not img_path.exists():
            response = requests.get(CU_YEMEKHANE_URL+res["img"])
            with open(img_path, "wb") as f:
                f.write(response.content)
        
        create_discord_massage(res).send()





if __name__ == "__main__":
    main()


