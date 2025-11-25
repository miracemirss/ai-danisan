# app/core/utils.py

import re
import unicodedata

def slugify(value: str) -> str:
    """
    Metni URL dostu 'slug' formatına çevirir.
    Örnek: "AI Danışan Başlıyor" -> "ai-danisan-basliyor"
    """
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-")