import re
from datetime import datetime

def parse_coords(coord_str: str):
    """
    Преобразует строку координат формата DDMMNDDDMME в десятичные градусы.
    Пример: 4620N07805E -> (46.3333, 78.0833)
    533957N0913642E -> (53.6658, 91.6117)
    """
    match = re.match(
        r"(\d{2})(\d{2})(\d{2})([NS])(\d{3})(\d{2})(\d{2})([EW])",
        coord_str
    )
    if not match:
        return None

    lat_d, lat_m, lat_s, ns, lon_d, lon_m, lon_s, ew = match.groups()

    lat = int(lat_d) + int(lat_m) / 60 + int(lat_s) / 3600
    lon = int(lon_d) + int(lon_m) / 60 + int(lon_s) / 3600

    if ns == "S":
        lat = -lat
    if ew == "W":
        lon = -lon

    return lat, lon


def parse_time_hhmm(hhmm: str, dof: str = None):
    """
    Преобразует время HHMM (например '0830') в datetime.
    Если указан DOF (YYMMDD), добавляется дата.
    """
    if not re.match(r"^\d{4}$", hhmm):
        return None

    hour, minute = int(hhmm[:2]), int(hhmm[2:])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None

    if dof and re.match(r"^\d{6}$", dof):
        year = 2000 + int(dof[:2])
        month = int(dof[2:4])
        day = int(dof[4:6])
        return datetime(year, month, day, hour, minute)

    return {"hour": hour, "minute": minute}


def extract_times(result):
    """
    Извлекает departure_time и arrival_time только из полей 13 и 16.
    """
    if "DOF" not in result.get("extra", {}):
        return result

    dof = result["extra"]["DOF"]

    # поле 13 -> время вылета
    if "ZZZZ0800" in result["fields"]:
        hhmm = re.search(r"(\d{4})", result["fields"]["ZZZZ0800"])
        if hhmm:
            result["departure_time"] = parse_time_hhmm(hhmm.group(1), dof)

    # поле 16 -> время прилёта
    if "ZZZZ0900" in result["fields"]:
        hhmm = re.search(r"(\d{4})", result["fields"]["ZZZZ0900"])
        if hhmm:
            result["arrival_time"] = parse_time_hhmm(hhmm.group(1), dof)

    return result


def parse_shr(raw: str):
    """
    Парсит SHR-сообщение и возвращает словарь.
    """
    raw = raw[raw.find("("):]
    result = {"raw": raw.strip(), "fields": {}, "extra": {}}

    # Убираем скобки
    body = raw.strip()
    if body.startswith("(") and body.endswith(")"):
        body = body[1:-1]

    # Определяем тип сообщения
    m = re.match(r"^(\w{3})", body)
    if m:
        result["msg_type"] = m.group(1)
        body = body[len(m.group(1)):].strip()
    else:
        result["msg_type"] = None

    # Разделяем поля по дефису
    parts = re.split(r"\s-(?=[A-Z0-9])", body)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        key = part.split("/")[0].split()[0]
        result["fields"][key] = part

        # Извлечение тегов из поля (TYP/, DEP/, DEST/, DOF/, RMK/ и т.д.)
        if "/" in part:
            tags = re.findall(r"([A-Z]{2,5})/([^ ]+)", part)
            for t, v in tags:
                result["extra"][t] = v

    # Дополнительная нормализация
    if "DOF" in result["extra"]:
        result["dof_date"] = result["extra"]["DOF"]

    if "DEP" in result["extra"]:
        dep_coords = parse_coords(result["extra"]["DEP"])
        if dep_coords:
            result["dep_coords"] = dep_coords

    if "DEST" in result["extra"]:
        dest_coords = parse_coords(result["extra"]["DEST"])
        if dest_coords:
            result["dest_coords"] = dest_coords

    # Извлекаем времена
    result = extract_times(result)

    return result
