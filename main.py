from typing import List
import re

from ipytv import m3u
from ipytv.exceptions import WrongTypeException, MalformedPlaylistException
from ipytv.m3u import M3U_HEADER_TAG
from ipytv.playlist import (
    log,
    _remove_blank_rows,
    M3UPlaylist,
    _parse_header,
    _chunk_body,
    _populate,
)


def loadl(rows: List) -> "M3UPlaylist":
    if not isinstance(rows, List):
        log.error("expected %s, got %s", type([]), type(rows))
        raise WrongTypeException("Wrong type: List expected")
    rows = _remove_blank_rows(rows)
    pl_len = len(rows)
    if pl_len < 1:
        log.error("a playlist should have at least 1 row")
        raise MalformedPlaylistException("a playlist should have at least 1 row")
    header = rows[0].strip()
    if not m3u.is_m3u_header_row(header):
        log.error(
            'the playlist\'s first row should start with "%s", but it\'s "%s"',
            M3U_HEADER_TAG,
            header,
        )
        raise MalformedPlaylistException(f"Missing or misplaced {M3U_HEADER_TAG} row")
    out_pl = M3UPlaylist()
    out_pl.add_attributes(_parse_header(header))
    # We're parsing an empty playlist, so we return an empty playlist object
    if pl_len <= 1:
        return out_pl
    body = rows[1:]
    chunks = _chunk_body(body, 1)
    results: List[M3UPlaylist] = []
    log.debug("spawning a pool of processes (one per core) to parse the playlist")
    for chunk in chunks:
        beginning = chunk["beginning"]
        end = chunk["end"]
        log.debug(
            'assigning a "populate" task (beginning: %s, end: %s) to a process in the pool',
            beginning,
            end,
        )
        result = _populate(body, beginning, end)
        results.append(result)
    log.debug("closing workers")
    log.debug("workers closed")
    log.debug("waiting for workers termination")
    log.debug("workers terminated")
    for result in results:
        p_list = result
        out_pl.append_channels(p_list.get_channels())
    return out_pl


def loadf(filename: str) -> "M3UPlaylist":
    if not isinstance(filename, str):
        log.error("expected %s, got %s", type(""), type(filename))
        raise WrongTypeException("Wrong type: string expected")
    with open(filename, encoding="utf-8") as file:
        buffer = file.readlines()
        return loadl(buffer)


data = loadf("playlist.m3u")

pattern = re.compile(
    r"(?P<name>[\w\s!]+?)\s*"  # Channel name (letters, spaces, exclamation marks, and underscores until we find other patterns)
    r"(?P<quality>HD|FHD)?\s*"  # Optional quality indicator (HD or FHD)
    r"(?P<orig>orig)?\s*"  # Optional "orig" label
    r"(?P<offset>[\+\-]?\d+)?\s*"  # Optional time offset with + or - sign
    r"(?:\((?P<region>[^)]+)\))?\s*"  # Optional region in parentheses
    r"(?<=\s)(?P<country_code>[A-Z]{2})?$"  # Optional country code (two capital letters, only if preceded by a space)
)

CHANELS_LIST = [
    "Первый канал HD orig",
    "Первый канал (+2)",
    "Первый канал HD +4",
    "Россия 1 HD orig",
    'Россия-1 +2',
    'Россия-1 +4',
    "НТВ HD orig",
    "НТВ (+2)",
    "НТВ +4",
    "Россия 24",
    'ТВЦ HD',
    'Рен ТВ HD orig',
    'СТС HD orig',
    'СТС +2',
    'Домашний HD',
    'ТВ3 HD',
    'Пятница! HD',
    'Мир HD',
    'ТНТ HD orig',
    'Кинохит HD',
    'Кинопремьера HD orig',
    'Киносемья HD orig',
    'Киносвидание HD',
    'Мужское Кино HD orig',
    'Viju TV1000 HD orig',
    'Viju TV1000 Action HD orig',
    'Viju TV1000 Русское HD orig',
    'Viju+ Megahit HD orig',
    'Viju+ Premiere HD orig',
    'Viju+ Comedy HD orig',
    'Viju+ Serial HD orig',
    'Кино ТВ HD orig',
    'Киномикс HD',
    'Кинокомедия HD',
    'Киноужас HD orig',
]

exclude_regions = [
    "#EXTGRP:Азербайджан | Azərbaycan",
    "#EXTGRP:Беларусь | Беларускія",
    "#EXTGRP:Германия | Germany",
    "#EXTGRP:Бразилия | Brasil",
    "#EXTGRP:Грузия | ქართული",
    "#EXTGRP:Израиль | ישראלי",
    "#EXTGRP:Индия | India",
    "#EXTGRP:Италия | Italy",
    "#EXTGRP:Казахстан | Қазақстан",
    "#EXTGRP:Латвия | Latvia",
    "#EXTGRP:Литва | Lithuania",
    "#EXTGRP:Молдавия | Moldovenească",
    "#EXTGRP:Польша | Poland",
    "#EXTGRP:Румыния | Romania",
    "#EXTGRP:Турция | Türk",
    "#EXTGRP:Узбекистан | O'zbek",
    "#EXTGRP:Украина | Українські",
    "#EXTGRP:Франция | France",
    "#EXTGRP:Хорватия | Croatia",
    "#EXTGRP:Чехия | Czech Republic",
    "#EXTGRP:Швеция | Sweden",
    "#EXTGRP:Южная Корея | Korea",
    "#EXTGRP:Эстония | Estonia",
    "#EXTGRP:Таджикистан | Точик",
    "#EXTGRP:Финляндия | Finland",
    "#EXTGRP:Португалия | Portugal",
    "#EXTGRP:Нидерланды | Netherlands",
    "#EXTGRP:Норвегия | Norway",
    "#EXTGRP:ОАЭ | UAE",
    "#EXTGRP:Дания | Denmark",
    "#EXTGRP:Армения | Հայկական",
    "#EXTGRP:Испания | Spain",
    "#EXTGRP:Арабские | عربي",
    "#EXTGRP:Египет | Egypt",
    "#EXTGRP:Австралия | Australia",
    "#EXTGRP:Словакия | Slovakia",
    "#EXTGRP:Болгария | Bulgaria",
    "#EXTGRP:Телемагазины",
]

exclude_name_in = {
    "(Омск)",
    "(Томск)",
    "(Иркутск",
    "(Братск",
    "(Канск",
    "(Канск",
    "(Элиста)",
    "(Пермь)",
    "(Нефтекамск",
    "(Абакан-Орион)",
    "(Приволжье, Китеж)",
    "(Алтай, Дианэт)",
    "(Уфа)",
    "(Липецк)",
    "(Невинномысск)",
    "(Уфа, ЗТ)",
    "(Владивосток)",
    "(Кузбасс)",
    "(Алания",
    "(Тамбов",
    "(Белорецк",
    "(Белгород",
    "(Орион",
    "(ЗТ Владивосток)",
    "(Тест)",
    "(Орск",
    "(Нижневартовск",
    "(Китеж",
    "(Красноярск",
    "(Новый Уренгой",
    # llll
    'Sport TV+ HD PT',
}

exclude_country_codes = [
    "UA",
    "CZ",
    "DE",
    "IT",
    "BY",
    "AT",
    "PL",
    "PL",
    "KZ",
    "TR",
    "LV",
    'FR',
    'PT',
    'GR',
    'BR',
    'RO',
    'ES',
    'DK',
    'EE',
    'NL',
    'RS',
    'HU',
    'ER',
    'AL',
    'SE',
]


def skip_region(extras):
    for extra in extras:
        if extra in exclude_regions:
            return True
        return False


def skip_name(name):
    for ex_name in exclude_name_in:
        if ex_name in name:
            return True
    return False


r = set()
cc = set()
i = 1

sorted_pl = M3UPlaylist()
sorted_pl.add_attributes(data.get_attributes())

sorted_ch = [None] * len(CHANELS_LIST)
orig_ch = []

for index, channel in enumerate(data.get_channels()):
    if skip_region(channel.extras):
        continue

    if skip_name(channel.name):
        continue

    r.add(channel.extras[0])
    name = channel.name
    m = pattern.match(name)
    res = None
    if m:
        res = {k: v for k, v in m.groupdict().items() if v is not None}

        if "country_code" in res.keys():
            if res["country_code"] in exclude_country_codes:
                continue
            cc.add(res["country_code"])

    if name in CHANELS_LIST:
        c_index = CHANELS_LIST.index(name)
        sorted_ch[c_index] = channel
    else:
        orig_ch.append(channel)

    msg = f'{index}\t{name}'
    if res:
        msg += f' -> {res}'
    else:
        msg += f' -> no match'

    # print(msg)

    i += 1

print('totlal', i)
print(cc)

sorted_pl.append_channels(sorted_ch)
sorted_pl.append_channels(orig_ch)

with open('playlist.sorted.m3u', 'w') as fd:
    fd.write(sorted_pl.to_m3u_plus_playlist())
