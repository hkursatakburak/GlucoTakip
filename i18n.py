import json
import os
from typing import Dict, Any
from fastapi import Request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(BASE_DIR, "locales")

def load_translations(lang: str) -> Dict[str, Any]:
    file_path = os.path.join(LOCALES_DIR, f"{lang}.json")
    if not os.path.exists(file_path):
        # Fallback to Turkish
        file_path = os.path.join(LOCALES_DIR, "tr.json")
        if not os.path.exists(file_path):
            print(f"ERROR: Translation file not found at {file_path}")
            return {}
            
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR loading translation file {file_path}: {e}")
        return {}

# Global translations cache
translations_cache: Dict[str, Dict[str, Any]] = {}

def get_translations(lang: str) -> Dict[str, Any]:
    if lang not in translations_cache:
        translations_cache[lang] = load_translations(lang)
        # Verify fallback logic
        if not translations_cache[lang] and lang != "tr":
            translations_cache[lang] = load_translations("tr")
    return translations_cache[lang]

def get_language(request: Request) -> str:
    # 1. Check HTTP-only cookie first
    lang = request.cookies.get("language")
    if lang in ["tr", "en"]:
        return lang
    
    # Defaults to tr
    return "tr"

def get_translation(key: str, lang: str = "tr", **kwargs) -> str:
    """
    Get translation by dotted key (e.g. 'nav.dashboard').
    Optionally, format the string with kwargs.
    """
    trans = get_translations(lang)
    keys = key.split('.')
    
    val = trans
    for k in keys:
        if isinstance(val, dict) and k in val:
            val = val[k]
        else:
            return key # fallback to key itself
            
    if isinstance(val, str) and kwargs:
        try:
            return val.format(**kwargs)
        except KeyError:
            pass # Ignore missing kwargs
            
    return str(val) if val is not None else key

import jinja2

@jinja2.pass_context
def translate_context(context, key: str, **kwargs) -> str:
    request = context.get("request")
    lang = "tr"
    if request:
        lang = get_language(request)
    return get_translation(key, lang=lang, **kwargs)

def setup_templates(templates):
    """
    Adds the `_` function to the Jinja2 env globals using pass_context,
    so we don't need to pass `_` on every render.
    """
    templates.env.globals["_"] = translate_context
