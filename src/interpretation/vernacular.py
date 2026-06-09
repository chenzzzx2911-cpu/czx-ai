"""64卦深度白话解读模块"""
import json, os

_DATA = None

def _load():
    global _DATA
    if _DATA is None:
        path = os.path.join(os.path.dirname(__file__), 'vernacular_data.json')
        with open(path, encoding='utf-8') as f:
            _DATA = json.load(f)
    return _DATA

def get_vernacular(binary: str) -> dict:
    data = _load()
    if binary in data:
        return data[binary]
    return {"summary":"此卦暂无深度解读，请参考原文。","vernacular_gua_ci":"","essence":"","life_advice":{"事业":"","感情":"","健康":"","财运":""},"keywords":[],"life_lesson":"","suggested_book":"","modern_example":""}
