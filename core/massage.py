from dataclasses import dataclass, field, is_dataclass
from typing import Optional, List, Dict, BinaryIO, Union
import requests
import json
import random
import os

@dataclass
class DiscordMsgImgDict:
    images: Dict[str, BinaryIO]

    def __str__(self, indent = 0):
        return"    "*indent + str(self.images)


@dataclass
class DiscordEmbedMsgField:
    name: str
    value: str
    inline: bool = False

    def __str__(self, indent = 0):
        return f"{"    "*indent + self.name}\n{"    "*indent + self.inline}"

@dataclass(frozen=True)
class AttachmentRef:
    key: str

    def __str__(self, indent = 0) -> str:
        return indent*"    " + f"attachment://{self.key}"

@dataclass
class DiscordEmbedImg:
    url: Union[str, AttachmentRef]

    @property
    def key(self):
        if isinstance(self.url, str):
            if "//" not in self.url:
                raise ValueError(f"worse attachment argument {self.url}")
            return self.url.split("//")[1]
        else:
            return self.url.key

    def __eq__(self, value):
        if isinstance(value, DiscordEmbedImg):
            return self.key == value.key
        return False

    def __str__(self, indent = 0):
        return str(self.url)

@dataclass
class DiscordEmbedMessage:
    title: Optional[str] = None
    image: Optional[DiscordEmbedImg] = None
    fields: List[DiscordEmbedMsgField] = field(default_factory=list)
    color: Optional[int] = field(default_factory=lambda: random.randint(0, 0xFFFFFF))

    def __str__(self, indent = 1):
        str_ = (
            indent*"    " + self.title,
            str(self.image, indent+1),
            *[str(fld, indent+1) for fld in self.fields],
            indent*"    " + str(self.color)
        )
        return "\n".join(str_)

@dataclass
class DiscordMessage:
    target_url: str
    files: Optional[DiscordMsgImgDict] = None
    embeds: List[DiscordEmbedMessage] = field(default_factory=list)

    def __str__(self, indent = 0):
        str_ = (
            "    " * indent + self.target_url,
            str(self.files),
            str(self.embeds)
        )
        return "\n".join(str_)

    def send(self):
        multipart_files = {}

        # files varsa multipart'a ekle
        if self.files:
            for i, (key, bio) in enumerate(self.files.images.items()):
                filename = os.path.basename(bio.name)
                multipart_files[f"files[{i}]"] = (filename, bio)
                for embed in self.embeds:
                    if embed.image.key == key:
                        embed.image.url = AttachmentRef(filename)

        payload = {
            "embeds": [to_dict(embed) for embed in self.embeds]
        }

        multipart_files["payload_json"] = (
            None,
            json.dumps(payload, ensure_ascii=False),
            "application/json"
        )
        print(multipart_files)
        response = requests.post(
            self.target_url,
            files=multipart_files
        )

        response.raise_for_status()

    def __add__(self, other):
        if isinstance(other, DiscordMessage):
            if self.target_url != other.target_url:
                raise KeyError(f"you cant add different targeted massages")
            msgimgdict = {}
            embeds = self.embeds + other.embeds
            print(embeds)

            for i, kv in enumerate(self.files.images.items()):
                k, v = kv
                for embed in embeds:
                    if embed.image.key == k:
                        embed.image.url = AttachmentRef(f"key{i}")
                        msgimgdict[f"key{i}.img"] = v
            for i, kv in enumerate(other.files.images.items(), start=len(msgimgdict.keys())):
                k, v = kv
                for embed in embeds:
                    if embed.image.key == k:
                        embed.image.url = AttachmentRef(f"key{i}.img")
                        msgimgdict[f"key{i}"] = v
            
            return DiscordMessage(
                self.target_url,
                DiscordMsgImgDict(msgimgdict),
                embeds
            )
        raise ValueError(f"you cant add {DiscordMessage} and {type(other)}")

def to_dict(obj):
    if isinstance(obj, AttachmentRef):
        return str(obj)
    if is_dataclass(obj):
        return {
            k: to_dict(v)
            for k, v in obj.__dict__.items()
            if v not in (None, [], {})
        }
    elif isinstance(obj, list):
        return [to_dict(i) for i in obj if i not in (None, [], {})]
    else:
        return obj
