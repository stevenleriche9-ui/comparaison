import re 
import unicodedata

ALIAS = {
    "gb": "go", "tb": "to",
    "frigo": "refrigerateur", "fridge": "refrigerateur",
    "clim": "climatiseur", "ventilo": "ventilateur",
    "blender": "mixeur", "kettle": "bouilloire", "electric": "electrique",
    "monitor": "ecran", "mouse": "souris", "printer": "imprimante",
    "wireless": "sans fil", "microwave": "micro ondes", "dd": "disque dur",
}

PHRASES = {
    "air conditioner": "climatiseur",
    "steam iron": "fer a repasser",
}

BRUIT = {"a", "pc", "portable", "laptop", "core", "ultra",
         "expansion", "ssd", "sur", "pied", "4k", "ac1200",
         "disque", "dur", "externe"}

def normaliser(nom):
    t = nom.lower()
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = t.replace('"', " pouces ")
    t = re.sub(r"(\d),(\d)", r"\1.\2", t)
    t = re.sub(r"(\d(?:\.\d+)?)\s*hp\b", r"\1 cv", t)
    t = re.sub(r"(\d)([a-z])", r"\1 \2", t)

    for phrase, remplacement in PHRASES.items():
        t = t.replace(phrase, remplacement)
    t = re.sub(r"[^a-z0-9.]+", " ", t)
    mots = []
    for mot in t.split():
        mots.extend(ALIAS.get(mot, mot).split())
    return {m for m in mots if m not in BRUIT}