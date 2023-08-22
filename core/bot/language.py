from typing import Dict,  Any
from os import path, listdir
from json import load


class LocalizationError(Exception):
    ...

class BotLanguage():
    name: str
    strings: Dict[str, str]

    def __init__(self, strings: Dict[str, str], language_name: str):
        self.strings = strings
        self.name = language_name
    
    def string(self, string_id: str, **values: Any) -> str:
        string = self.strings.get(string_id)
        if string is None:
            raise LocalizationError(f"Localization '{self.name}' doesn't have a '{string_id}' string")
        for key, value in values.items():
            string = string.replace(f"%{key}%", str(value))
        return string

def load_languages(languages_dir: str) -> Dict[str, BotLanguage]:
    languages = dict()
    for entry in listdir(languages_dir):
        entry_path = path.join(languages_dir, entry)
        if not path.isfile(entry_path) or not entry.endswith(".json"):
            continue
        with open(entry_path, "r", encoding="utf-8") as f:
            strings = load(f)
            language_name = strings.pop("LOCALIZATION_NAME")
            languages[language_name] = BotLanguage(strings, language_name)
    return languages