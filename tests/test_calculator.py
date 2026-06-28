import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from calc.calculator import calc_all


# ── 浅田真央（1990-09-25）──────────────────────────────────
def test_asada_mao():
    r = calc_all(1990, 9, 25)
    assert r["kako_moto"] == 25
    assert r["kako_kanzen"] == 7
    assert r["genzai_moto"] == 35
    assert r["genzai_kanzen"] == 8
    assert r["mirai_moto"] == 16
    assert r["mirai_kanzen"] == 7
    assert r["message_moto"] == 76
    assert r["message_kanzen"] == 4
    assert r["answer_moto"] == 80
    assert r["answer_kanzen"] == 8
    assert r["star_moto"] == 96
    assert r["star_kanzen"] == 6


# ── 吉高ゆり子（1988-07-22）マスターナンバーテスト ─────────
def test_yoshitaka_yuriko():
    r = calc_all(1988, 7, 22)
    assert r["kako_moto"] == 22
    assert r["kako_kanzen"] == 22   # 22日生まれ → マスターナンバー
    assert r["genzai_moto"] == 37
    assert r["genzai_kanzen"] == 1
    assert r["mirai_moto"] == 11
    assert r["mirai_kanzen"] == 11  # 7+2+2=11 → マスターナンバー
    assert r["message_moto"] == 70
    assert r["message_kanzen"] == 7
    assert r["answer_moto"] == 77
    assert r["answer_kanzen"] == 5
    assert r["star_moto"] == 88
    assert r["star_kanzen"] == 7


# ── 清さん（1964-04-28）さらに見ていく数字のテスト ─────────
def test_kiyo_san():
    r = calc_all(1964, 4, 28)
    assert r["kako_moto"] == 28
    assert r["kako_kanzen"] == 1
    assert r["genzai_moto"] == 34
    assert r["genzai_kanzen"] == 7
    assert r["mirai_moto"] == 14
    assert r["mirai_kanzen"] == 5
    assert r["message_moto"] == 76
    assert r["message_kanzen"] == 4
    assert r["answer_moto"] == 80
    assert r["answer_kanzen"] == 8
    assert r["star_moto"] == 94
    assert r["star_kanzen"] == 4
    assert r["honshitsu_moto"] == 62
    assert r["honshitsu_kanzen"] == 8
    assert r["seikaku_moto"] == 48
    assert r["seikaku_kanzen"] == 3
    assert r["tougou_moto"] == 90
    assert r["tougou_kanzen"] == 9
    assert r["soshitsu_moto"] == 156
    assert r["soshitsu_kanzen"] == 3   # 1+5+6=12→1+2=3


# ── 藤井聡太（2002-07-19）───────────────────────────────────
def test_fujii_sota():
    r = calc_all(2002, 7, 19)
    assert r["kako_moto"] == 19
    assert r["kako_kanzen"] == 1
    assert r["genzai_moto"] == 21
    assert r["genzai_kanzen"] == 3
    assert r["mirai_moto"] == 17
    assert r["mirai_kanzen"] == 8
    assert r["message_moto"] == 57
    assert r["message_kanzen"] == 3
    assert r["answer_moto"] == 60
    assert r["answer_kanzen"] == 6
    assert r["star_moto"] == 77
    assert r["star_kanzen"] == 5
    assert r["honshitsu_moto"] == 40
    assert r["honshitsu_kanzen"] == 4
    assert r["seikaku_moto"] == 38
    assert r["seikaku_kanzen"] == 11   # 3+8=11 → マスターナンバー
    assert r["tougou_moto"] == 74
    assert r["tougou_kanzen"] == 11    # 7+4=11 → マスターナンバー


# ── イーロン・マスク（1971-06-28）─────────────────────────
def test_elon_musk():
    r = calc_all(1971, 6, 28)
    assert r["kako_moto"] == 28
    assert r["kako_kanzen"] == 1
    assert r["genzai_moto"] == 34
    assert r["genzai_kanzen"] == 7
    assert r["mirai_moto"] == 16
    assert r["mirai_kanzen"] == 7
    assert r["message_moto"] == 78
    assert r["message_kanzen"] == 6
    assert r["answer_moto"] == 84
    assert r["answer_kanzen"] == 3
    assert r["star_moto"] == 100
    assert r["star_kanzen"] == 1


# ── 29日生まれ（過去数が 29→11 になるケース）───────────────
def test_kako_29_becomes_11():
    r = calc_all(2000, 1, 29)
    assert r["kako_moto"] == 29
    assert r["kako_kanzen"] == 11   # 2+9=11 → マスターナンバー


# ── 素質が 369 に収束する確認 ────────────────────────────
def test_soshitsu_369_law():
    r = calc_all(1990, 9, 25)
    assert r["soshitsu_kanzen"] in {3, 6, 9}

    r2 = calc_all(1964, 4, 28)
    assert r2["soshitsu_kanzen"] in {3, 6, 9}

    r3 = calc_all(2002, 7, 19)
    assert r3["soshitsu_kanzen"] in {3, 6, 9}
