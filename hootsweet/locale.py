import pytz

ACCEPTED_LANGUAGES = [
    "en",
    "ja",
    "fr",
    "it",
    "es",
    "de",
    "pt_BR",
    "pl",
    "id",
    "zh_CN",
    "zh_HK",
    "zh_TW",
    "nl",
    "ko",
    "ar",
    "ru",
    "th",
    "tr",
]


def is_valid_language(language: str):
    return language in ACCEPTED_LANGUAGES


def is_valid_timezone(timezone: str):
    return timezone in pytz.all_timezones
