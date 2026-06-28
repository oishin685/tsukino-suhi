def _digit_sum(n: int) -> int:
    return sum(int(c) for c in str(n))


def _reduce(n: int, stops: set) -> int:
    while n > 9 and n not in stops:
        n = _digit_sum(n)
    return n


_KAKO_STOPS = {11, 22}
_GENZAI_STOPS = {11, 22, 33}
_MIRAI_STOPS = {11}
_STD_STOPS = {11, 22, 33}


def calc_kako(day: int) -> tuple:
    moto = day
    kanzen = _reduce(moto, _KAKO_STOPS)
    return moto, kanzen


def calc_genzai(year: int, month: int, day: int) -> tuple:
    moto = sum(int(c) for c in f"{year}{month:02d}{day:02d}")
    kanzen = _reduce(moto, _GENZAI_STOPS)
    return moto, kanzen


def calc_mirai(month: int, day: int) -> tuple:
    moto = sum(int(c) for c in f"{month:02d}{day:02d}")
    kanzen = _reduce(moto, _MIRAI_STOPS)
    return moto, kanzen


def calc_message(kako_moto: int, genzai_moto: int, mirai_moto: int) -> tuple:
    moto = kako_moto + genzai_moto + mirai_moto
    kanzen = _reduce(moto, _STD_STOPS)
    return moto, kanzen


def calc_answer(message_moto: int, message_kanzen: int) -> tuple:
    moto = message_moto + message_kanzen
    kanzen = _reduce(moto, _STD_STOPS)
    return moto, kanzen


def calc_star(answer_moto: int, mirai_moto: int) -> tuple:
    moto = answer_moto + mirai_moto
    kanzen = _reduce(moto, _STD_STOPS)
    return moto, kanzen


def calc_honshitsu(kako_moto: int, genzai_moto: int) -> tuple:
    moto = kako_moto + genzai_moto
    kanzen = _reduce(moto, _STD_STOPS)
    return moto, kanzen


def calc_seikaku(genzai_moto: int, mirai_moto: int) -> tuple:
    moto = genzai_moto + mirai_moto
    kanzen = _reduce(moto, _STD_STOPS)
    return moto, kanzen


def calc_tougou(mirai_moto: int, message_moto: int) -> tuple:
    moto = mirai_moto + message_moto
    kanzen = _reduce(moto, _STD_STOPS)
    return moto, kanzen


def calc_soshitsu(message_moto: int, answer_moto: int) -> tuple:
    moto = message_moto + answer_moto
    kanzen = _reduce(moto, set())   # 止めない → 3/6/9 に収束
    return moto, kanzen


def calc_all(year: int, month: int, day: int) -> dict:
    kako_m, kako_k = calc_kako(day)
    genzai_m, genzai_k = calc_genzai(year, month, day)
    mirai_m, mirai_k = calc_mirai(month, day)
    msg_m, msg_k = calc_message(kako_m, genzai_m, mirai_m)
    ans_m, ans_k = calc_answer(msg_m, msg_k)
    star_m, star_k = calc_star(ans_m, mirai_m)
    hon_m, hon_k = calc_honshitsu(kako_m, genzai_m)
    sei_m, sei_k = calc_seikaku(genzai_m, mirai_m)
    tou_m, tou_k = calc_tougou(mirai_m, msg_m)
    sos_m, sos_k = calc_soshitsu(msg_m, ans_m)

    return {
        "kako_moto": kako_m,       "kako_kanzen": kako_k,
        "genzai_moto": genzai_m,   "genzai_kanzen": genzai_k,
        "mirai_moto": mirai_m,     "mirai_kanzen": mirai_k,
        "message_moto": msg_m,     "message_kanzen": msg_k,
        "answer_moto": ans_m,      "answer_kanzen": ans_k,
        "star_moto": star_m,       "star_kanzen": star_k,
        "honshitsu_moto": hon_m,   "honshitsu_kanzen": hon_k,
        "seikaku_moto": sei_m,     "seikaku_kanzen": sei_k,
        "tougou_moto": tou_m,      "tougou_kanzen": tou_k,
        "soshitsu_moto": sos_m,    "soshitsu_kanzen": sos_k,
    }
