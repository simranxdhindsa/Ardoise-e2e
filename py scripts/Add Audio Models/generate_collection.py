import json, hashlib, urllib.request, os

BASE_URL = "https://core.ardoirse.com"

# ── Load token from .env ──────────────────────────────────────────────────────
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
AUTH_TOKEN = None
with open(_env_path) as _f:
    for _line in _f:
        _line = _line.strip()
        if _line.startswith('BEARER_TOKEN='):
            AUTH_TOKEN = _line.split('=', 1)[1].strip()
            break

if not AUTH_TOKEN or AUTH_TOKEN == 'paste_your_token_here':
    raise SystemExit("ERROR: Set BEARER_TOKEN in .env file before running.")

# Strip "Bearer " prefix if accidentally included in .env
if AUTH_TOKEN.lower().startswith('bearer '):
    AUTH_TOKEN = AUTH_TOKEN[7:].strip()

print(f"Token loaded from .env ({AUTH_TOKEN[:20]}...)")

req = urllib.request.Request(
    'https://core.ardoirse.com/a/audio-model/testing/benchmark/combos?session_id=default',
    headers={
        'authorization': f'Bearer {AUTH_TOKEN}',
        'accept': 'application/json',
        'origin': 'https://mission-control.ardoirse.com',
    }
)
with urllib.request.urlopen(req) as resp:
    raw = resp.read().decode()

data = json.loads(raw)
items = data['data']['items']
print(f"Fetched {len(items)} audio models")

# Categories with reasoning:
# warm_friendly  -> voices that sound conversational, casual (even distribution by hash)
# professional   -> neutral, clear voices
# energetic      -> upbeat, expressive voices
# calm_soothing  -> soft, gentle voices
CATEGORIES = [
    {"uuid": "ecbf655f-1df2-441d-83d0-22169866f14e", "key": "Warm & friendly"},
    {"uuid": "cde83438-bb06-4954-a0f6-461fd52e27e0", "key": "Professional"},
    {"uuid": "a4960ab0-2c0a-47cd-9478-5f8e9e632d13", "key": "Energetic"},
    {"uuid": "a9a11d2d-2544-4228-a1dd-5a46806ca984", "key": "Calm & soothing"},
]

def assign_category(item):
    seed = int(hashlib.md5((item.get('name', '') + item.get('voice', '')).encode()).hexdigest(), 16) % 4
    return CATEGORIES[seed]

LANGUAGE_MAP = {
    "af-ZA": "AF (Afrikaans-South Africa)",
    "am-ET": "AM (Amharic-Ethiopia)",
    "ar-AE": "AR (Arabic-United Arab Emirates)",
    "ar-BH": "AR (Arabic-Bahrain)",
    "ar-DZ": "AR (Arabic-Algeria)",
    "ar-EG": "AR (Arabic-Egypt)",
    "ar-IQ": "AR (Arabic-Iraq)",
    "ar-JO": "AR (Arabic-Jordan)",
    "ar-KW": "AR (Arabic-Kuwait)",
    "ar-LB": "AR (Arabic-Lebanon)",
    "ar-LY": "AR (Arabic-Libya)",
    "ar-MA": "AR (Arabic-Morocco)",
    "ar-OM": "AR (Arabic-Oman)",
    "ar-QA": "AR (Arabic-Qatar)",
    "ar-SA": "AR (Arabic-Saudi Arabia)",
    "ar-SY": "AR (Arabic-Syria)",
    "ar-TN": "AR (Arabic-Tunisia)",
    "ar-YE": "AR (Arabic-Yemen)",
    "as-IN": "AS (Assamese-India)",
    "az-AZ": "AZ (Azerbaijani-Azerbaijan)",
    "bg-BG": "BG (Bulgarian-Bulgaria)",
    "bn-BD": "BN (Bengali-Bangladesh)",
    "bn-IN": "BN (Bengali-India)",
    "bs-BA": "BS (Bosnian-Bosnia and Herzegovina)",
    "ca-ES": "CA (Catalan-Spain)",
    "cs-CZ": "CS (Czech-Czech Republic)",
    "cy-GB": "CY (Welsh-United Kingdom)",
    "da-DK": "DA (Danish-Denmark)",
    "de-AT": "DE (German-Austria)",
    "de-CH": "DE (German-Switzerland)",
    "de-DE": "DE (German-Germany)",
    "el-GR": "EL (Greek-Greece)",
    "en":    "EN (English)",
    "en-AU": "EN (English-Australia)",
    "en-CA": "EN (English-Canada)",
    "en-GB": "EN (English-United Kingdom)",
    "en-HK": "EN (English-Hong Kong)",
    "en-IE": "EN (English-Ireland)",
    "en-IN": "EN (English-India)",
    "en-KE": "EN (English-Kenya)",
    "en-NG": "EN (English-Nigeria)",
    "en-NZ": "EN (English-New Zealand)",
    "en-PH": "EN (English-Philippines)",
    "en-SG": "EN (English-Singapore)",
    "en-TZ": "EN (English-Tanzania)",
    "en-US": "EN (English-United States)",
    "en-ZA": "EN (English-South Africa)",
    "es-AR": "ES (Spanish-Argentina)",
    "es-BO": "ES (Spanish-Bolivia)",
    "es-CL": "ES (Spanish-Chile)",
    "es-CO": "ES (Spanish-Colombia)",
    "es-CR": "ES (Spanish-Costa Rica)",
    "es-CU": "ES (Spanish-Cuba)",
    "es-DO": "ES (Spanish-Dominican Republic)",
    "es-EC": "ES (Spanish-Ecuador)",
    "es-ES": "ES (Spanish-Spain)",
    "es-GQ": "ES (Spanish-Equatorial Guinea)",
    "es-GT": "ES (Spanish-Guatemala)",
    "es-HN": "ES (Spanish-Honduras)",
    "es-MX": "ES (Spanish-Mexico)",
    "es-NI": "ES (Spanish-Nicaragua)",
    "es-PA": "ES (Spanish-Panama)",
    "es-PE": "ES (Spanish-Peru)",
    "es-PR": "ES (Spanish-Puerto Rico)",
    "es-PY": "ES (Spanish-Paraguay)",
    "es-SV": "ES (Spanish-El Salvador)",
    "es-US": "ES (Spanish-United States)",
    "es-UY": "ES (Spanish-Uruguay)",
    "es-VE": "ES (Spanish-Venezuela)",
    "et-EE": "ET (Estonian-Estonia)",
    "eu-ES": "EU (Basque-Spain)",
    "fa-IR": "FA (Persian-Iran)",
    "fi-FI": "FI (Finnish-Finland)",
    "fil-PH": "FIL (Filipino-Philippines)",
    "fr":    "FR (French)",
    "fr-BE": "FR (French-Belgium)",
    "fr-CA": "FR (French-Canada)",
    "fr-CH": "FR (French-Switzerland)",
    "fr-FR": "FR (French-France)",
    "ga-IE": "GA (Irish-Ireland)",
    "gl-ES": "GL (Galician-Spain)",
    "gu-IN": "GU (Gujarati-India)",
    "he-IL": "HE (Hebrew-Israel)",
    "hi-IN": "HI (Hindi-India)",
    "hr-HR": "HR (Croatian-Croatia)",
    "hu-HU": "HU (Hungarian-Hungary)",
    "hy-AM": "HY (Armenian-Armenia)",
    "id-ID": "ID (Indonesian-Indonesia)",
    "is-IS": "IS (Icelandic-Iceland)",
    "it-IT": "IT (Italian-Italy)",
    "iu-Cans-CA": "IU (Inuktitut Syllabics-Canada)",
    "iu-Latn-CA": "IU (Inuktitut Latin-Canada)",
    "ja":    "JA (Japanese)",
    "ja-JP": "JA (Japanese-Japan)",
    "jv-ID": "JV (Javanese-Indonesia)",
    "ka-GE": "KA (Georgian-Georgia)",
    "kk-KZ": "KK (Kazakh-Kazakhstan)",
    "km-KH": "KM (Khmer-Cambodia)",
    "kn-IN": "KN (Kannada-India)",
    "ko-KR": "KO (Korean-South Korea)",
    "lo-LA": "LO (Lao-Laos)",
    "lt-LT": "LT (Lithuanian-Lithuania)",
    "lv-LV": "LV (Latvian-Latvia)",
    "mk-MK": "MK (Macedonian-North Macedonia)",
    "ml-IN": "ML (Malayalam-India)",
    "mn-MN": "MN (Mongolian-Mongolia)",
    "mr-IN": "MR (Marathi-India)",
    "ms-MY": "MS (Malay-Malaysia)",
    "mt-MT": "MT (Maltese-Malta)",
    "my-MM": "MY (Burmese-Myanmar)",
    "nb-NO": "NB (Norwegian Bokmal-Norway)",
    "ne-NP": "NE (Nepali-Nepal)",
    "nl-BE": "NL (Dutch-Belgium)",
    "nl-NL": "NL (Dutch-Netherlands)",
    "or-IN": "OR (Odia-India)",
    "pa-IN": "PA (Punjabi-India)",
    "pl-PL": "PL (Polish-Poland)",
    "ps-AF": "PS (Pashto-Afghanistan)",
    "pt-BR": "PT (Portuguese-Brazil)",
    "pt-PT": "PT (Portuguese-Portugal)",
    "ro-RO": "RO (Romanian-Romania)",
    "ru-RU": "RU (Russian-Russia)",
    "si-LK": "SI (Sinhala-Sri Lanka)",
    "sk-SK": "SK (Slovak-Slovakia)",
    "sl-SI": "SL (Slovenian-Slovenia)",
    "so-SO": "SO (Somali-Somalia)",
    "sq-AL": "SQ (Albanian-Albania)",
    "sr-Latn-RS": "SR (Serbian Latin-Serbia)",
    "sr-RS": "SR (Serbian-Serbia)",
    "su-ID": "SU (Sundanese-Indonesia)",
    "sv-SE": "SV (Swedish-Sweden)",
    "sw-KE": "SW (Swahili-Kenya)",
    "sw-TZ": "SW (Swahili-Tanzania)",
    "ta-IN": "TA (Tamil-India)",
    "ta-LK": "TA (Tamil-Sri Lanka)",
    "ta-MY": "TA (Tamil-Malaysia)",
    "ta-SG": "TA (Tamil-Singapore)",
    "te-IN": "TE (Telugu-India)",
    "th-TH": "TH (Thai-Thailand)",
    "tr-TR": "TR (Turkish-Turkey)",
    "uk-UA": "UK (Ukrainian-Ukraine)",
    "ur-IN": "UR (Urdu-India)",
    "ur-PK": "UR (Urdu-Pakistan)",
    "uz-UZ": "UZ (Uzbek-Uzbekistan)",
    "vi-VN": "VI (Vietnamese-Vietnam)",
    "wuu-CN": "WUU (Wu Chinese-China)",
    "yue-CN": "YUE (Cantonese-China)",
    "zh-CN": "ZH (Chinese-China)",
    "zh-CN-henan":   "ZH (Chinese-China Henan)",
    "zh-CN-liaoning": "ZH (Chinese-China Liaoning)",
    "zh-CN-shaanxi": "ZH (Chinese-China Shaanxi)",
    "zh-CN-shandong": "ZH (Chinese-China Shandong)",
    "zh-CN-sichuan": "ZH (Chinese-China Sichuan)",
    "zh-HK": "ZH (Chinese-Hong Kong)",
    "zh-TW": "ZH (Chinese-Taiwan)",
    "zu-ZA": "ZU (Zulu-South Africa)",
}

def format_language(lang_code):
    return LANGUAGE_MAP.get(lang_code, lang_code.upper())

def get_source(provider):
    return {"azure": "AZURE", "elevenlabs": "ELEVENLABS", "openai": "OPENAI", "gemini": "GEMINI"}.get(
        provider.lower(), provider.upper()
    )

def build_name(item):
    source = item.get('provider', '').capitalize()
    vname = item.get('name', '').strip()
    if item.get('provider') == 'elevenlabs' and ' - ' in vname:
        vname = vname.split(' - ')[0].strip()
    gender = item.get('gender', '').capitalize()
    return f"0 {source}-{vname}-{gender}"

def get_voice_first_name(item):
    vname = item.get('name', '').strip()
    if item.get('provider') == 'elevenlabs' and ' - ' in vname:
        vname = vname.split(' - ')[0].strip()
    return vname.split()[0]

MALE_PREFIXES = ["Takumi", "Ramesh"]
FEMALE_PREFIXES = ["Blue", "Manga", "Pixar", "Quibli"]

INTRO_TEMPLATES = [
    "Hi there! I am {prefix}, your dedicated AI learning guide. I will walk you through every topic with clarity and patience, making sure you never feel lost.\nDo not hesitate to revisit any section, I am always here to help you succeed.",
    "Hello! My name is {prefix}, and I will be your AI companion throughout this course. Expect clear explanations, helpful examples, and a steady pace tailored just for you.\nLet us build your understanding together, one step at a time.",
    "Welcome! I am {prefix}, your AI instructor for this journey. I will break down complex ideas into simple, digestible pieces so you can learn with confidence.\nFeel free to go at your own pace, I will be right here whenever you need me.",
    "Hey, I am {prefix}! Think of me as your personal AI tutor, patient, focused, and always ready to help. We will tackle each concept together, and I will make sure nothing gets left behind.\nReady when you are!",
    "Greetings! I am {prefix}, your AI learning assistant. I am here to guide you step by step, explain things clearly, and help you build real understanding.\nLet us make this learning experience smooth and rewarding.",
]

WELCOME_TEMPLATES = [
    "Welcome! I am {prefix}, and I am glad you are here. Take a moment to look around and get comfortable with the course layout.\nWhenever you are ready, we will dive right in together.",
    "Hi and welcome! Great to have you with us. I am {prefix}, and I will be here to support you throughout this course.\nThere is no rush, explore at your own pace and let me know when you are set to begin.",
    "Welcome aboard! I am {prefix}. This is your space to learn, grow, and ask questions without hesitation.\nHave a look at what is ahead, and we will get started the moment you feel ready.",
    "Hello and welcome! I am {prefix}, your guide for this course. Everything you need is right here, and I will help you make the most of it.\nFeel free to explore, then we will begin whenever you are comfortable.",
    "Welcome! So glad you joined us. I am {prefix}, and together we are going to have a great learning experience.\nTake your time getting settled, I will be right here when you are ready to start.",
]

def make_headers():
    return [
        {"key": "accept",        "value": "application/json, text/plain, */*"},
        {"key": "content-type",  "value": "application/json"},
        {"key": "authorization", "value": f"Bearer {AUTH_TOKEN}"},
        {"key": "origin",        "value": "https://mission-control.ardoirse.com"},
        {"key": "user-agent",    "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"},
    ]

collection_items = []
male_idx = 0
female_idx = 0

for item in items:
    gender = item.get('gender', 'female').lower()
    provider = item.get('provider', '')
    source = get_source(provider)
    model = item.get('model', 'N/A') or 'N/A'
    voice = item.get('voice', '')
    language = format_language(item.get('language', ''))
    name = build_name(item)
    category = assign_category(item)

    if gender == 'male':
        male_idx += 1
    else:
        female_idx += 1

    voice_name = get_voice_first_name(item)
    seed_val = int(hashlib.md5((name + voice + 'msg').encode()).hexdigest(), 16)
    intro_msg   = INTRO_TEMPLATES[seed_val % len(INTRO_TEMPLATES)].format(prefix=voice_name)
    welcome_msg = WELCOME_TEMPLATES[(seed_val // 7) % len(WELCOME_TEMPLATES)].format(prefix=voice_name)

    create_body = {
        "source": source,
        "model": model,
        "language": language,
        "voice": voice,
        "gender": gender.capitalize(),
        "name": name,
        "description": f"I am {voice_name}, a {source.capitalize()} {language} voice with a {category['key']} tone.",
        "category_uuid": category["uuid"],
    }

    create_req = {
        "name": f"1. Create - {name}",
        "event": [{
            "listen": "test",
            "script": {
                "exec": [
                    "var jsonData = pm.response.json();",
                    "if (jsonData && jsonData.data && jsonData.data.uuid) {",
                    "    pm.collectionVariables.set('current_audio_model_uuid', jsonData.data.uuid);",
                    "    console.log('Created audio model UUID:', jsonData.data.uuid);",
                    "}"
                ],
                "type": "text/javascript"
            }
        }],
        "request": {
            "method": "POST",
            "header": make_headers(),
            "body": {
                "mode": "raw",
                "raw": json.dumps(create_body),
                "options": {"raw": {"language": "json"}}
            },
            "url": {
                "raw": f"{BASE_URL}/a/audio-model",
                "protocol": "https",
                "host": ["core", "ardoirse", "com"],
                "path": ["a", "audio-model"]
            }
        }
    }

    intro_req = {
        "name": f"2. Intro Message - {name}",
        "request": {
            "method": "PUT",
            "header": make_headers(),
            "body": {
                "mode": "raw",
                "raw": json.dumps({"message_type": "introduction", "message": intro_msg}),
                "options": {"raw": {"language": "json"}}
            },
            "url": {
                "raw": f"{BASE_URL}/a/audio-model/{{{{current_audio_model_uuid}}}}/message",
                "protocol": "https",
                "host": ["core", "ardoirse", "com"],
                "path": ["a", "audio-model", "{{current_audio_model_uuid}}", "message"]
            }
        }
    }

    welcome_req = {
        "name": f"3. Welcome Message - {name}",
        "request": {
            "method": "PUT",
            "header": make_headers(),
            "body": {
                "mode": "raw",
                "raw": json.dumps({"message_type": "welcome", "message": welcome_msg}),
                "options": {"raw": {"language": "json"}}
            },
            "url": {
                "raw": f"{BASE_URL}/a/audio-model/{{{{current_audio_model_uuid}}}}/message",
                "protocol": "https",
                "host": ["core", "ardoirse", "com"],
                "path": ["a", "audio-model", "{{current_audio_model_uuid}}", "message"]
            }
        }
    }

    activate_req = {
        "name": f"4. Activate - {name}",
        "request": {
            "method": "PATCH",
            "header": make_headers(),
            "body": {
                "mode": "raw",
                "raw": json.dumps({"toggle": True}),
                "options": {"raw": {"language": "json"}}
            },
            "url": {
                "raw": f"{BASE_URL}/a/audio-model/{{{{current_audio_model_uuid}}}}/active",
                "protocol": "https",
                "host": ["core", "ardoirse", "com"],
                "path": ["a", "audio-model", "{{current_audio_model_uuid}}", "active"]
            }
        }
    }

    collection_items.append({"name": name, "item": [create_req, intro_req, welcome_req, activate_req]})

collection = {
    "info": {
        "name": "Audio Models - Bulk Create",
        "_postman_id": "audio-models-bulk-001",
        "description": f"Auto-generated: {len(items)} audio models, 4 requests each ({len(items) * 4} total). Flow per model: 1) Create, 2) Intro message, 3) Welcome message, 4) Activate.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "variable": [
        {"key": "current_audio_model_uuid", "value": "", "type": "string"},
    ],
    "item": collection_items
}

out = "c:/dhindsa/01 temp_JSON Collection Postman/audio_models_bulk_create.postman_collection.json"
with open(out, 'w', encoding='utf-8') as f:
    json.dump(collection, f, indent=2, ensure_ascii=False)

print(f"Done! {len(items)} folders x 4 requests = {len(items) * 4} total requests")
print(f"File: {out}")
