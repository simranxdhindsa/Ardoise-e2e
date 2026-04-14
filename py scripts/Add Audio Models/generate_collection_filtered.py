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
all_items = data['data']['items']
print(f"Fetched {len(all_items)} audio models total")

# ── Language filter ───────────────────────────────────────────────────────────
# Include: English, Spanish, French, Japanese, German, Dutch, Italian
# + Indian languages: Hindi, Bengali, Gujarati, Marathi, Tamil, Telugu,
#                     Kannada, Malayalam, Punjabi, Odia, Assamese, Urdu
ALLOWED_LANG_PREFIXES = {
    'en',           # English
    'es',           # Spanish
    'fr',           # French
    'ja',           # Japanese
    'de',           # German
    'nl',           # Dutch (grouped with German)
    'it',           # Italian
    'hi',           # Hindi
    'pa',           # Punjabi
}

items = [i for i in all_items if i.get('language', '').split('-')[0].lower() in ALLOWED_LANG_PREFIXES]
# ── Cap non-English/Indian languages to 2M+2F or 3M+3F ──────────────────────
# Languages that get capped (not en, hi, pa — those keep all voices)
CAP_LANG_PREFIXES = {'es', 'fr', 'ja', 'de', 'nl', 'it', 'en'}

from collections import defaultdict

# Group capped items by language prefix + gender, pick top N deterministically
def apply_voice_cap(items):
    # Separate items that are NOT capped
    uncapped = [i for i in items if i.get('language','').split('-')[0].lower() not in CAP_LANG_PREFIXES]

    # Group capped items by lang prefix
    capped_groups = defaultdict(lambda: {'male': [], 'female': []})
    for i in items:
        prefix = i.get('language','').split('-')[0].lower()
        gender = i.get('gender','').lower()
        if prefix in CAP_LANG_PREFIXES and gender in ('male', 'female'):
            capped_groups[prefix][gender].append(i)

    selected = []
    for prefix, g in capped_groups.items():
        # English: always 6M+6F; others: 3M+3F if 5+ available, else 2M+2F
        if prefix == 'en':
            pick = 6
        else:
            pick = 3 if max(len(g['male']), len(g['female'])) >= 5 else 2
        # Sort deterministically by voice name so results are consistent
        selected.extend(sorted(g['male'],   key=lambda x: x['voice'])[:pick])
        selected.extend(sorted(g['female'], key=lambda x: x['voice'])[:pick])

    return uncapped + selected

items = apply_voice_cap(items)
print(f"Filtered to {len(items)} models (languages: English, Spanish, French, Japanese, German/Dutch, Italian, Hindi, Punjabi — capped non-EN/Indian to 2-3 per gender)")

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
    return vname.split()[0]  # first word only, e.g. "Aarti" from "Aarti"

# ── Message templates by language group ──────────────────────────────────────
# Indian languages (hi, bn, gu, mr, ta, te, kn, ml, pa, or, as, ur) → English
# All others → native language of that group

TEMPLATES = {

    # ── English (& Indian languages) ─────────────────────────────────────────
    "en": {
        "intro": [
            "Hi there! I am {prefix}, your dedicated AI learning guide. I will walk you through every topic with clarity and patience, making sure you never feel lost.\nDo not hesitate to revisit any section, I am always here to help you succeed.",
            "Hello! My name is {prefix}, and I will be your AI companion throughout this course. Expect clear explanations, helpful examples, and a steady pace tailored just for you.\nLet us build your understanding together, one step at a time.",
            "Welcome! I am {prefix}, your AI instructor for this journey. I will break down complex ideas into simple, digestible pieces so you can learn with confidence.\nFeel free to go at your own pace, I will be right here whenever you need me.",
            "Hey, I am {prefix}! Think of me as your personal AI tutor, patient, focused, and always ready to help. We will tackle each concept together, and I will make sure nothing gets left behind.\nReady when you are!",
            "Greetings! I am {prefix}, your AI learning assistant. I am here to guide you step by step, explain things clearly, and help you build real understanding.\nLet us make this learning experience smooth and rewarding.",
            "Hi! I am {prefix}, and I am thrilled to be your guide through this course. Every lesson has been designed to build on the last, so you always feel supported.\nJust follow my lead and we will get through this together.",
            "Hello and welcome! I am {prefix}. Whether you are a complete beginner or brushing up on your skills, I will make sure every concept lands clearly.\nLet us take this one step at a time.",
            "Hey there! I am {prefix}, your AI learning companion. I will keep things simple, engaging, and easy to follow throughout this entire journey.\nWhenever you are ready, we will get started.",
            "Good to meet you! I am {prefix}, your personal AI guide for this course. My job is to make sure learning feels approachable, not overwhelming.\nLet us work through this together at a pace that suits you.",
            "Hi, I am {prefix}! I am here to turn complex topics into clear, manageable lessons. You can count on me to keep things focused and easy to understand.\nLet us dive in whenever you feel ready.",
            "Welcome to the course! I am {prefix}, your AI learning assistant. I will be with you at every step, explaining ideas clearly and helping you stay on track.\nFeel free to start whenever you are comfortable.",
            "Hello! I am {prefix}, and I am excited to guide you through this learning experience. We will move at a comfortable pace so every concept truly sticks.\nLet us begin this journey together.",
            "Hi there! I am {prefix}. I have been designed to make your learning experience as smooth and effective as possible. No rushing, no confusion, just clear guidance.\nReady to begin?",
            "Greetings! I am {prefix}, your AI tutor. I will break each topic into digestible parts and make sure you fully understand before moving on.\nLet us build something great together.",
            "Hey! I am {prefix}, your guide for this course. Learning works best when it feels natural, so I will keep things conversational and clear throughout.\nLet us get started!",
            "Hello! My name is {prefix}. I am here to support your learning journey from start to finish with patience, clarity, and encouragement.\nWhenever you are set, we will begin.",
            "Hi! I am {prefix}, your dedicated course guide. Think of me as a knowledgeable friend who is always ready to explain, revisit, and help you grow.\nLet us make learning enjoyable.",
            "Welcome! I am {prefix}. I will guide you through this course with clear explanations and a steady pace designed to build your confidence.\nThere is no pressure, we go at your speed.",
            "Hi there! My name is {prefix}, and I am your AI instructor. Every lesson I deliver is designed to be clear, practical, and easy to retain.\nLet us start this learning journey right now.",
            "Hello! I am {prefix}, and I am glad you are here. I will make sure every topic we cover feels within reach, no matter your starting point.\nLet us learn together.",
        ],
        "welcome": [
            "Welcome! I am {prefix}, and I am glad you are here. Take a moment to look around and get comfortable with the course layout.\nWhenever you are ready, we will dive right in together.",
            "Hi and welcome! Great to have you with us. I am {prefix}, and I will be here to support you throughout this course.\nThere is no rush, explore at your own pace and let me know when you are set to begin.",
            "Welcome aboard! I am {prefix}. This is your space to learn, grow, and ask questions without hesitation.\nHave a look at what is ahead, and we will get started the moment you feel ready.",
            "Hello and welcome! I am {prefix}, your guide for this course. Everything you need is right here, and I will help you make the most of it.\nFeel free to explore, then we will begin whenever you are comfortable.",
            "Welcome! So glad you joined us. I am {prefix}, and together we are going to have a great learning experience.\nTake your time getting settled, I will be right here when you are ready to start.",
            "Hi, welcome! I am {prefix}. You have made a great choice starting this course, and I am here to make sure you get the most out of it.\nWhenever you are ready, we will kick things off.",
            "Welcome to the course! I am {prefix}. Take a deep breath, look around, and know that you are in good hands.\nWe will start whenever you say so.",
            "Great to have you here! I am {prefix}, and this is the beginning of something really valuable. I will be with you every step of the way.\nFeel free to get settled first.",
            "Hello and welcome! I am {prefix}. I hope you are feeling excited and ready to learn. Everything is set up and waiting for you.\nJust say the word and we will begin.",
            "Welcome! I am {prefix}, and I am looking forward to this journey with you. Take a moment to get familiar with the layout before we dive in.\nNo rush at all.",
            "Hi there and welcome! I am {prefix}. I am here to make sure your experience is smooth, clear, and genuinely useful from day one.\nLet me know when you are ready to start.",
            "Welcome aboard! I am {prefix}, and I am excited to guide you through what lies ahead. There is a lot of great material here, and I will help you navigate it all.\nGet comfortable and we will begin soon.",
            "So glad you are here! I am {prefix}. This course is designed to be helpful and engaging, and I will be your guide throughout.\nTake your time looking around before we start.",
            "Hello, welcome! I am {prefix}, your learning guide. I am here to make sure you never feel lost or overwhelmed.\nWhenever you feel ready, we will get going together.",
            "Welcome! I am {prefix}. You are about to start something great, and I will be by your side through every lesson.\nSettle in and let me know when you are ready.",
            "Hi and welcome! I am {prefix}. I am genuinely excited to be part of your learning journey today.\nTake a moment, get comfortable, and we will begin when you are set.",
            "Welcome! Great to see you here. I am {prefix}, and I will guide you through this course with care and clarity.\nExplore the layout first, then we will dive in together.",
            "Hello and welcome! I am {prefix}. I am here to make your learning experience as productive and enjoyable as possible.\nJust let me know when you are ready to begin.",
            "Welcome! I am {prefix}, your AI guide. You are in the right place, and I will make sure every step forward feels clear and confident.\nWhenever you are ready, we will start.",
            "Hi, welcome! I am {prefix}. I am here to support you from the very first lesson to the very last.\nTake your time getting comfortable, then we will begin together.",
        ],
    },

    # ── Spanish ───────────────────────────────────────────────────────────────
    "es": {
        "intro": [
            "Hola, soy {prefix}, tu guía de aprendizaje con inteligencia artificial. Te acompañaré en cada tema con claridad y paciencia.\nNo dudes en revisar cualquier sección, siempre estaré aquí para ayudarte.",
            "Hola, me llamo {prefix} y seré tu compañero de aprendizaje durante este curso. Explicaciones claras, ejemplos útiles y un ritmo adaptado a ti.\nConstruyamos el conocimiento juntos, paso a paso.",
            "Bienvenido. Soy {prefix}, tu instructor de inteligencia artificial para este recorrido. Convertiré ideas complejas en lecciones simples y comprensibles.\nVe a tu propio ritmo, aquí estaré cuando me necesites.",
            "Hola, soy {prefix}! Piénsame como tu tutor personal: paciente, enfocado y siempre listo para ayudarte.\nAfrontaremos cada concepto juntos. ¡Cuando quieras, empezamos!",
            "Saludos, soy {prefix}, tu asistente de aprendizaje con IA. Estoy aquí para guiarte paso a paso y ayudarte a construir un entendimiento real.\nHagamos de esta experiencia algo fluido y enriquecedor.",
            "Hola, soy {prefix}. He sido diseñado para hacer tu experiencia de aprendizaje lo más eficaz posible. Sin prisas, sin confusiones, solo orientación clara.\n¿Listo para comenzar?",
            "Hola, me llamo {prefix}. Estoy aquí para convertir temas complejos en lecciones claras y manejables. Puedes contar conmigo en todo momento.\nEmpecemos cuando estés listo.",
            "Bienvenido al curso. Soy {prefix}, tu asistente de aprendizaje con IA. Estaré contigo en cada paso, explicando conceptos y ayudándote a avanzar.\nComienza cuando te sientas cómodo.",
            "Hola, soy {prefix}, y estoy emocionado de guiarte en esta experiencia de aprendizaje. Avanzaremos a un ritmo cómodo para que todo quede bien claro.\nComencemos este camino juntos.",
            "Hola, soy {prefix}. Me han diseñado para que tu aprendizaje sea fluido y efectivo. Sin prisas, sin confusión, solo orientación clara.\n¿Preparado para empezar?",
            "Hola, soy {prefix}, tu guía para este curso. El aprendizaje funciona mejor cuando se siente natural, así que mantendré todo conversacional y claro.\n¡Vamos a comenzar!",
            "Hola, me llamo {prefix}. Estoy aquí para apoyar tu proceso de aprendizaje de principio a fin, con paciencia, claridad y motivación.\nCuando estés listo, empezamos.",
            "Hola, soy {prefix}, tu guía dedicado. Piénsame como un amigo bien informado, siempre dispuesto a explicar, repasar y ayudarte a crecer.\nHagamos del aprendizaje algo agradable.",
            "Hola, soy {prefix}. Te guiaré con explicaciones claras y un ritmo diseñado para construir tu confianza.\nSin presión, vamos a tu velocidad.",
            "Hola, me llamo {prefix} y soy tu instructor de IA. Cada lección que imparto está diseñada para ser clara, práctica y fácil de retener.\nComencemos este proceso de aprendizaje ahora mismo.",
            "Hola, soy {prefix} y me alegra que estés aquí. Me aseguraré de que cada tema que cubramos sea accesible, sin importar tu punto de partida.\nAprendamos juntos.",
            "Hola, soy {prefix}. Cada lección avanza sobre la anterior para que siempre te sientas acompañado.\nSolo sígueme y lo lograremos juntos.",
            "Hola, soy {prefix}. Ya seas principiante o estés repasando, me aseguraré de que cada concepto quede bien claro.\nVayamos paso a paso.",
            "Mucho gusto, soy {prefix}, tu guía personal de IA para este curso. Mi trabajo es hacer que el aprendizaje sea accesible, no abrumador.\nTrabajemos a un ritmo que te convenga.",
            "Hola, soy {prefix}. Estoy aquí para transformar temas complejos en lecciones claras y manejables. Puedes contar conmigo.\nComencemos cuando quieras.",
        ],
        "welcome": [
            "Bienvenido. Soy {prefix} y me alegra tenerte aquí. Tómate un momento para explorar el contenido del curso.\nCuando estés listo, empezamos juntos.",
            "Hola y bienvenido. Es un placer tenerte con nosotros. Soy {prefix} y estaré aquí para apoyarte durante todo el curso.\nNo hay prisa, explora a tu ritmo y dime cuándo empezamos.",
            "Bienvenido a bordo. Soy {prefix}. Este es tu espacio para aprender, crecer y hacer preguntas sin dudarlo.\nEcha un vistazo a lo que viene y empezaremos cuando estés listo.",
            "Hola y bienvenido. Soy {prefix}, tu guía para este curso. Todo lo que necesitas está aquí y te ayudaré a aprovecharlo al máximo.\nExplora y empezamos cuando estés cómodo.",
            "Bienvenido. Qué alegría que te hayas unido. Soy {prefix} y juntos vamos a tener una gran experiencia de aprendizaje.\nTómate tu tiempo para instalarte, aquí estaré cuando quieras empezar.",
            "Hola, bienvenido. Soy {prefix}. Hiciste una excelente elección al comenzar este curso y estoy aquí para que aproveches cada parte.\nCuando estés listo, arrancamos.",
            "Bienvenido al curso. Soy {prefix}. Respira, mira a tu alrededor y sabe que estás en buenas manos.\nEmpezamos cuando tú lo digas.",
            "Qué bueno tenerte aquí. Soy {prefix} y este es el comienzo de algo muy valioso. Estaré contigo en cada paso.\nTómate un momento para instalarte primero.",
            "Hola y bienvenido. Soy {prefix}. Espero que estés emocionado y listo para aprender. Todo está preparado y esperándote.\nSolo di la palabra y empezamos.",
            "Bienvenido. Soy {prefix} y espero con entusiasmo este recorrido contigo. Familiarízate con el contenido antes de que nos lancemos.\nSin ninguna prisa.",
            "Hola y bienvenido. Soy {prefix}. Estoy aquí para asegurarme de que tu experiencia sea fluida, clara y realmente útil desde el primer día.\nDime cuándo estás listo para comenzar.",
            "Bienvenido a bordo. Soy {prefix} y estoy emocionado de guiarte por lo que viene. Hay mucho material valioso aquí y te ayudaré a navegarlo todo.\nInstálate y empezamos pronto.",
            "Qué alegría que estés aquí. Soy {prefix}. Este curso está diseñado para ser útil y atractivo, y seré tu guía en todo momento.\nTómate tu tiempo antes de que comencemos.",
            "Hola, bienvenido. Soy {prefix}, tu guía de aprendizaje. Estoy aquí para asegurarme de que nunca te sientas perdido ni abrumado.\nCuando estés listo, empezamos juntos.",
            "Bienvenido. Soy {prefix}. Estás a punto de comenzar algo grandioso y estaré a tu lado en cada lección.\nInstálate y dime cuándo estás listo.",
            "Hola y bienvenido. Soy {prefix}. Me emociona genuinamente ser parte de tu camino de aprendizaje hoy.\nTómate un momento, ponte cómodo y empezamos cuando estés listo.",
            "Bienvenido. Qué bueno verte aquí. Soy {prefix} y te guiaré con cuidado y claridad durante todo el curso.\nExplora primero y luego nos lanzamos juntos.",
            "Hola y bienvenido. Soy {prefix}. Estoy aquí para hacer tu experiencia de aprendizaje lo más productiva y agradable posible.\nDime cuándo estás listo para empezar.",
            "Bienvenido. Soy {prefix}, tu guía de IA. Estás en el lugar correcto y me aseguraré de que cada avance sea claro y seguro.\nCuando estés listo, empezamos.",
            "Hola, bienvenido. Soy {prefix}. Estoy aquí para apoyarte desde la primera lección hasta la última.\nTómate tu tiempo para ponerte cómodo y luego empezamos juntos.",
        ],
    },

    # ── French ────────────────────────────────────────────────────────────────
    "fr": {
        "intro": [
            "Bonjour, je suis {prefix}, votre guide d'apprentissage IA. Je vous accompagnerai sur chaque sujet avec clarté et patience.\nN'hésitez pas à revoir une section, je suis toujours là pour vous aider.",
            "Bonjour, je m'appelle {prefix} et je serai votre compagnon d'apprentissage tout au long de ce cours. Des explications claires, des exemples utiles, à votre rythme.\nConstruisons ensemble votre compréhension, étape par étape.",
            "Bienvenue. Je suis {prefix}, votre instructeur IA pour ce parcours. Je transformerai les idées complexes en leçons simples et accessibles.\nAvancez à votre propre rythme, je serai là quand vous aurez besoin de moi.",
            "Bonjour, je suis {prefix} ! Considérez-moi comme votre tuteur personnel : patient, concentré et toujours prêt à vous aider.\nNous aborderons chaque concept ensemble. Prêt quand vous l'êtes !",
            "Bonjour, je suis {prefix}, votre assistant d'apprentissage IA. Je suis ici pour vous guider pas à pas et vous aider à développer une vraie compréhension.\nRendons cette expérience fluide et enrichissante.",
            "Bonjour, je suis {prefix}. J'ai été conçu pour rendre votre apprentissage aussi efficace que possible. Sans précipitation, sans confusion, juste des conseils clairs.\nPrêt à commencer ?",
            "Bonjour, je m'appelle {prefix}. Je suis là pour transformer des sujets complexes en leçons claires et gérables. Vous pouvez compter sur moi.\nCommençons quand vous êtes prêt.",
            "Bienvenue dans ce cours. Je suis {prefix}, votre assistant d'apprentissage IA. Je serai avec vous à chaque étape, en expliquant les concepts et en vous aidant à progresser.\nCommencez quand vous vous sentez à l'aise.",
            "Bonjour, je suis {prefix}, et je suis ravi de vous guider dans cette expérience d'apprentissage. Nous avancerons à un rythme confortable pour que tout soit bien assimilé.\nCommençons ce chemin ensemble.",
            "Bonjour, je suis {prefix}. J'ai été conçu pour que votre apprentissage soit fluide et efficace. Sans précipitation, sans confusion, juste des conseils clairs.\nPrêt à commencer ?",
            "Bonjour, je suis {prefix}, votre guide pour ce cours. L'apprentissage fonctionne mieux quand il semble naturel, alors je garderai tout conversationnel et clair.\nAllons-y !",
            "Bonjour, je m'appelle {prefix}. Je suis là pour soutenir votre parcours d'apprentissage du début à la fin, avec patience, clarté et encouragement.\nQuand vous serez prêt, nous commencerons.",
            "Bonjour, je suis {prefix}, votre guide dévoué. Considérez-moi comme un ami bien informé, toujours prêt à expliquer, à réviser et à vous aider à progresser.\nRendons l'apprentissage agréable.",
            "Bonjour, je suis {prefix}. Je vous guiderai avec des explications claires et un rythme conçu pour renforcer votre confiance.\nSans pression, nous avançons à votre vitesse.",
            "Bonjour, je m'appelle {prefix} et je suis votre instructeur IA. Chaque leçon que je dispense est conçue pour être claire, pratique et facile à retenir.\nCommençons ce parcours d'apprentissage maintenant.",
            "Bonjour, je suis {prefix} et je suis heureux que vous soyez là. Je veillerai à ce que chaque sujet abordé soit accessible, quel que soit votre point de départ.\nApprenons ensemble.",
            "Bonjour, je suis {prefix}. Chaque leçon s'appuie sur la précédente pour que vous vous sentiez toujours accompagné.\nSuivez-moi et nous y arriverons ensemble.",
            "Bonjour, je suis {prefix}. Que vous soyez débutant ou en révision, je veillerai à ce que chaque concept soit bien compris.\nAvançons pas à pas.",
            "Enchanté, je suis {prefix}, votre guide IA personnel pour ce cours. Mon rôle est de rendre l'apprentissage accessible, pas écrasant.\nTravaillons à un rythme qui vous convient.",
            "Bonjour, je suis {prefix}. Je suis là pour transformer des sujets complexes en leçons claires et gérables. Vous pouvez compter sur moi.\nCommençons quand vous voulez.",
        ],
        "welcome": [
            "Bienvenue. Je suis {prefix} et je suis heureux de vous accueillir. Prenez un moment pour explorer le contenu du cours.\nQuand vous êtes prêt, nous plongerons ensemble.",
            "Bonjour et bienvenue. Ravi de vous avoir parmi nous. Je suis {prefix} et je serai là pour vous soutenir tout au long de ce cours.\nPrenez votre temps, explorez à votre rythme et dites-moi quand vous êtes prêt.",
            "Bienvenue à bord. Je suis {prefix}. C'est votre espace pour apprendre, progresser et poser des questions sans hésitation.\nJetez un œil à ce qui vous attend et nous commencerons quand vous vous sentirez prêt.",
            "Bonjour et bienvenue. Je suis {prefix}, votre guide pour ce cours. Tout ce dont vous avez besoin est ici et je vous aiderai à en tirer le meilleur parti.\nExplorez et nous commencerons quand vous serez à l'aise.",
            "Bienvenue. Que vous soyez là. Je suis {prefix} et ensemble nous allons vivre une belle expérience d'apprentissage.\nPrenez le temps de vous installer, je serai là quand vous voudrez commencer.",
            "Bonjour, bienvenue. Je suis {prefix}. Vous avez fait un excellent choix en commençant ce cours et je suis là pour que vous en profitiez pleinement.\nQuand vous êtes prêt, on démarre.",
            "Bienvenue dans ce cours. Je suis {prefix}. Respirez, regardez autour de vous et sachez que vous êtes en de bonnes mains.\nNous commençons quand vous le dites.",
            "Ravi de vous accueillir. Je suis {prefix} et c'est le début de quelque chose de très précieux. Je serai avec vous à chaque étape.\nPrenez un moment pour vous installer d'abord.",
            "Bonjour et bienvenue. Je suis {prefix}. J'espère que vous êtes enthousiaste et prêt à apprendre. Tout est préparé et vous attend.\nDites le mot et nous commençons.",
            "Bienvenue. Je suis {prefix} et j'ai hâte de parcourir ce chemin avec vous. Familiarisez-vous avec le contenu avant de plonger.\nSans aucune précipitation.",
            "Bonjour et bienvenue. Je suis {prefix}. Je suis là pour m'assurer que votre expérience soit fluide, claire et vraiment utile dès le premier jour.\nDites-moi quand vous êtes prêt à commencer.",
            "Bienvenue à bord. Je suis {prefix} et je suis enthousiaste à l'idée de vous guider dans ce qui vous attend. Il y a beaucoup de contenu de valeur ici.\nInstallez-vous et nous commencerons bientôt.",
            "Ravi que vous soyez là. Je suis {prefix}. Ce cours est conçu pour être utile et engageant, et je serai votre guide tout au long.\nPrenez votre temps avant que nous commencions.",
            "Bonjour, bienvenue. Je suis {prefix}, votre guide d'apprentissage. Je suis là pour m'assurer que vous ne vous sentiez jamais perdu ni dépassé.\nQuand vous êtes prêt, nous commençons ensemble.",
            "Bienvenue. Je suis {prefix}. Vous êtes sur le point de commencer quelque chose de formidable et je serai à vos côtés à chaque leçon.\nInstallez-vous et dites-moi quand vous êtes prêt.",
            "Bonjour et bienvenue. Je suis {prefix}. Je suis vraiment ravi de faire partie de votre parcours d'apprentissage aujourd'hui.\nPrenez un moment, installez-vous confortablement et nous commençons quand vous êtes prêt.",
            "Bienvenue. Heureux de vous voir ici. Je suis {prefix} et je vous guiderai avec soin et clarté tout au long du cours.\nExplorez d'abord, puis nous plongerons ensemble.",
            "Bonjour et bienvenue. Je suis {prefix}. Je suis là pour rendre votre expérience d'apprentissage aussi productive et agréable que possible.\nDites-moi quand vous êtes prêt à commencer.",
            "Bienvenue. Je suis {prefix}, votre guide IA. Vous êtes au bon endroit et je veillerai à ce que chaque avancée soit claire et assurée.\nQuand vous êtes prêt, nous commençons.",
            "Bonjour, bienvenue. Je suis {prefix}. Je suis là pour vous accompagner de la première leçon à la dernière.\nPrenez votre temps pour vous installer, puis nous commençons ensemble.",
        ],
    },

    # ── Japanese ──────────────────────────────────────────────────────────────
    "ja": {
        "intro": [
            "こんにちは、{prefix}です。AIの学習ガイドとして、明確さと丁寧さをもってすべてのトピックを案内します。\nいつでもセクションを見直してください。いつでもサポートします。",
            "はじめまして、{prefix}といいます。このコースを通じてAIの学習パートナーとしてご一緒します。明確な説明と役立つ例を、あなたのペースでお届けします。\n一歩一歩、一緒に理解を深めましょう。",
            "ようこそ。私は{prefix}、このコースのAIインストラクターです。複雑なアイデアをシンプルで理解しやすいレッスンに変えます。\n自分のペースで進めてください。必要なときはいつでもここにいます。",
            "こんにちは、{prefix}です！私を個人AIチューターと思ってください。忍耐強く、集中力があり、いつでもお役に立てます。\n一緒にすべてのコンセプトに取り組みましょう。準備ができたらどうぞ！",
            "ご挨拶申し上げます。私は{prefix}、AIの学習アシスタントです。ステップバイステップでガイドし、真の理解を構築できるよう支援します。\nスムーズで充実した学習体験にしましょう。",
            "こんにちは、{prefix}です。学習体験をできるだけスムーズで効果的にするよう設計されています。急がず、混乱なく、明確なガイダンスだけです。\n始める準備はいいですか？",
            "はじめまして、{prefix}です。複雑なテーマをわかりやすい明確なレッスンに変えるためにここにいます。\n準備ができたら始めましょう。",
            "ようこそ。私は{prefix}、AIの学習アシスタントです。すべてのステップでご一緒し、コンセプトを説明し、前進をサポートします。\n快適に感じたら始めてください。",
            "こんにちは、私は{prefix}です。このコースをガイドすることにわくわくしています。すべてがしっかり定着するよう快適なペースで進めます。\n一緒にこの旅を始めましょう。",
            "こんにちは、{prefix}です。学習をスムーズで効果的にするよう設計されています。急がず、明確なガイダンスだけです。\n始める準備はいいですか？",
            "こんにちは、このコースのガイド{prefix}です。学習は自然に感じるときが一番うまくいきます。だからすべてを会話的にわかりやすく保ちます。\n始めましょう！",
            "はじめまして、{prefix}です。最初から最後まで、忍耐、明確さ、励ましをもって学習の旅をサポートします。\n準備ができたら始めましょう。",
            "こんにちは、{prefix}です。知識豊富な友人として、いつでも説明し、復習し、成長を助けることができます。\n学習を楽しいものにしましょう。",
            "こんにちは、{prefix}です。明確な説明と自信を積み上げるためのペースでガイドします。\nプレッシャーなし、あなたのスピードで進めます。",
            "はじめまして、{prefix}、AIインストラクターです。提供するすべてのレッスンは、明確でわかりやすく、記憶に残るよう設計されています。\n今すぐこの学習の旅を始めましょう。",
            "こんにちは、{prefix}です。ここにいてくれて嬉しいです。どこから始めても、すべてのトピックに手が届くよう確認します。\n一緒に学びましょう。",
            "こんにちは、{prefix}です。各レッスンは前のレッスンに基づいているため、常にサポートされていると感じられます。\nついてきてください、一緒に乗り越えましょう。",
            "こんにちは、{prefix}です。初心者でも復習中でも、すべてのコンセプトが明確に届くよう確認します。\n一歩一歩進みましょう。",
            "はじめまして、{prefix}、このコースの個人AIガイドです。学習を圧倒的でなく、アクセスしやすいものにするのが私の仕事です。\nあなたに合ったペースで一緒に取り組みましょう。",
            "こんにちは、{prefix}です。複雑なテーマを明確で管理しやすいレッスンに変えるためにここにいます。\n始める準備ができたらどうぞ。",
        ],
        "welcome": [
            "ようこそ。{prefix}です。ここにいてくれて嬉しいです。少しコースのレイアウトを確認してください。\n準備ができたら一緒に始めましょう。",
            "こんにちは、ようこそ。ご参加いただき嬉しいです。私は{prefix}、このコース全体でサポートします。\n急がず、自分のペースで探索してください。",
            "ようこそ。私は{prefix}です。ここは学び、成長し、遠慮なく質問できる場所です。\n先に何があるかを見て、準備ができたら始めましょう。",
            "こんにちは、ようこそ。{prefix}です。すべて必要なものがここにあります。最大限に活用できるよう手伝います。\n探索して、快適になったら始めましょう。",
            "ようこそ。ご参加いただき嬉しいです。{prefix}です。一緒に素晴らしい学習体験になるでしょう。\n落ち着く時間を取ってください。始める準備ができたらここにいます。",
            "こんにちは、ようこそ。{prefix}です。このコースを始めた素晴らしい選択に感謝します。\n準備ができたら始めましょう。",
            "ようこそ。{prefix}です。深呼吸して、周りを見回して、良い手に委ねていることを知ってください。\nあなたが言ったときに始めます。",
            "ご参加いただき嬉しいです。{prefix}です。これはとても価値のある何かの始まりです。すべてのステップで一緒にいます。\nまず落ち着いてください。",
            "こんにちは、ようこそ。{prefix}です。学ぶ準備ができているといいですね。すべて準備できています。\n一言いってくれれば始めます。",
            "ようこそ。{prefix}です。この旅を楽しみにしています。飛び込む前にレイアウトに慣れてください。\n急がなくて大丈夫です。",
            "こんにちは、ようこそ。{prefix}です。初日からスムーズで明確な体験を確保するためにここにいます。\n始める準備ができたら教えてください。",
            "ようこそ。{prefix}です。これから先にある素晴らしい内容をガイドするのが楽しみです。\n落ち着いてください、すぐに始めましょう。",
            "ここにいてくれて嬉しいです。{prefix}です。このコースは役立つように設計されています。ずっとガイドします。\n始める前に時間を取ってください。",
            "こんにちは、ようこそ。{prefix}、学習ガイドです。迷ったり圧倒されたりしないよう確認します。\n準備ができたら一緒に始めましょう。",
            "ようこそ。{prefix}です。素晴らしいことを始めようとしています。すべてのレッスンで隣にいます。\n落ち着いて、準備ができたら教えてください。",
            "こんにちは、ようこそ。{prefix}です。今日あなたの学習の旅に参加できることを本当に嬉しく思います。\n少し時間を取って、快適になって、準備ができたら始めましょう。",
            "ようこそ。ここにいてくれて嬉しいです。{prefix}です。注意深さと明確さをもってコース全体でガイドします。\nまず探索して、一緒に飛び込みましょう。",
            "こんにちは、ようこそ。{prefix}です。学習体験をできるだけ生産的で楽しいものにするためにここにいます。\n始める準備ができたら教えてください。",
            "ようこそ。{prefix}、AIガイドです。正しい場所にいます。すべての前進が明確で自信に満ちていることを確認します。\n準備ができたら始めましょう。",
            "こんにちは、ようこそ。{prefix}です。最初のレッスンから最後のレッスンまでサポートするためにここにいます。\n落ち着く時間を取って、一緒に始めましょう。",
        ],
    },

    # ── German / Dutch ────────────────────────────────────────────────────────
    "de": {
        "intro": [
            "Hallo, ich bin {prefix}, dein KI-Lernbegleiter. Ich führe dich mit Klarheit und Geduld durch jedes Thema.\nZögere nicht, einen Abschnitt zu wiederholen – ich bin immer für dich da.",
            "Hallo, mein Name ist {prefix} und ich werde dein Lernbegleiter in diesem Kurs sein. Klare Erklärungen, nützliche Beispiele und dein eigenes Tempo.\nLass uns gemeinsam Schritt für Schritt dein Wissen aufbauen.",
            "Willkommen. Ich bin {prefix}, dein KI-Instruktor für diese Reise. Ich verwandle komplexe Ideen in einfache, verständliche Lektionen.\nGeh in deinem eigenen Tempo vor – ich bin da, wenn du mich brauchst.",
            "Hi, ich bin {prefix}! Stell dir mich als deinen persönlichen KI-Tutor vor: geduldig, fokussiert und immer bereit zu helfen.\nWir gehen jeden Begriff gemeinsam an. Los geht's, wenn du bereit bist!",
            "Guten Tag, ich bin {prefix}, dein KI-Lernassistent. Ich bin hier, um dich Schritt für Schritt zu führen und echtes Verständnis aufzubauen.\nLass uns diese Lernerfahrung reibungslos und lohnend machen.",
            "Hallo, ich bin {prefix}. Ich wurde entwickelt, um dein Lernen so effektiv wie möglich zu gestalten. Kein Stress, keine Verwirrung, nur klare Anleitung.\nBereit anzufangen?",
            "Hallo, ich heiße {prefix}. Ich bin hier, um komplexe Themen in klare, überschaubare Lektionen zu verwandeln. Du kannst dich auf mich verlassen.\nFangen wir an, wenn du bereit bist.",
            "Willkommen im Kurs. Ich bin {prefix}, dein KI-Lernassistent. Ich bin bei jedem Schritt dabei und erkläre Konzepte und helfe dir voranzukommen.\nFang an, wenn du dich wohl fühlst.",
            "Hallo, ich bin {prefix}, und ich freue mich darauf, dich durch diese Lernerfahrung zu führen. Wir gehen in einem angenehmen Tempo vor, damit alles gut sitzt.\nLass uns diese Reise gemeinsam beginnen.",
            "Hallo, ich bin {prefix}. Ich wurde entwickelt, um dein Lernen reibungslos und effektiv zu gestalten. Kein Stress, nur klare Anleitung.\nBereit anzufangen?",
            "Hallo, ich bin {prefix}, dein Guide für diesen Kurs. Lernen funktioniert am besten, wenn es sich natürlich anfühlt, also halte ich alles verständlich und klar.\nLos geht's!",
            "Hallo, ich heiße {prefix}. Ich bin hier, um deine Lernreise von Anfang bis Ende mit Geduld, Klarheit und Motivation zu begleiten.\nWenn du bereit bist, fangen wir an.",
            "Hallo, ich bin {prefix}, dein engagierter Guide. Stell dir mich als einen gut informierten Freund vor, der immer bereit ist zu erklären, zu wiederholen und dir beim Wachsen zu helfen.\nLass uns Lernen angenehm machen.",
            "Hallo, ich bin {prefix}. Ich führe dich mit klaren Erklärungen und einem Tempo, das dein Vertrauen aufbaut.\nKein Druck, wir gehen in deinem Tempo.",
            "Hallo, mein Name ist {prefix} und ich bin dein KI-Instruktor. Jede Lektion, die ich vermittle, ist klar, praxisnah und leicht zu behalten.\nLass uns jetzt mit dieser Lernreise beginnen.",
            "Hallo, ich bin {prefix} und freue mich, dass du hier bist. Ich stelle sicher, dass jedes Thema zugänglich ist, egal wo du anfängst.\nLass uns gemeinsam lernen.",
            "Hallo, ich bin {prefix}. Jede Lektion baut auf der vorherigen auf, sodass du dich immer unterstützt fühlst.\nFolg mir einfach und wir schaffen das gemeinsam.",
            "Hallo, ich bin {prefix}. Ob Anfänger oder zur Auffrischung – ich sorge dafür, dass jedes Konzept klar ankommt.\nGehen wir es Schritt für Schritt an.",
            "Guten Tag, ich bin {prefix}, dein persönlicher KI-Guide für diesen Kurs. Meine Aufgabe ist es, Lernen zugänglich, nicht überwältigend zu machen.\nLass uns in einem Tempo arbeiten, das zu dir passt.",
            "Hallo, ich bin {prefix}. Ich bin hier, um komplexe Themen in klare, überschaubare Lektionen zu verwandeln. Du kannst auf mich zählen.\nFangen wir an, wenn du möchtest.",
        ],
        "welcome": [
            "Willkommen. Ich bin {prefix} und freue mich, dass du hier bist. Nimm dir einen Moment, um den Kursaufbau kennenzulernen.\nWenn du bereit bist, tauchen wir gemeinsam ein.",
            "Hallo und willkommen. Schön, dass du dabei bist. Ich bin {prefix} und begleite dich durch den gesamten Kurs.\nKein Stress – erkunde in deinem Tempo und sag mir, wann du loslegen möchtest.",
            "Willkommen an Bord. Ich bin {prefix}. Dies ist dein Raum zum Lernen, Wachsen und Fragen ohne Zögern.\nSchau dir an, was vor dir liegt, und wir starten, wenn du bereit bist.",
            "Hallo und willkommen. Ich bin {prefix}, dein Guide für diesen Kurs. Alles, was du brauchst, ist hier, und ich helfe dir, das Beste daraus zu machen.\nSchau dich um und fang an, wenn du dich wohl fühlst.",
            "Willkommen. Schön, dass du dabei bist. Ich bin {prefix} und gemeinsam werden wir eine tolle Lernerfahrung haben.\nNimm dir Zeit zum Eingewöhnen – ich bin da, wenn du starten möchtest.",
            "Hallo, willkommen. Ich bin {prefix}. Du hast eine gute Wahl getroffen und ich bin hier, damit du alles mitnimmst.\nWenn du bereit bist, legen wir los.",
            "Willkommen im Kurs. Ich bin {prefix}. Atme durch, schau dich um und wisse, dass du in guten Händen bist.\nWir starten, wenn du es sagst.",
            "Schön, dass du hier bist. Ich bin {prefix} und dies ist der Beginn von etwas sehr Wertvollem. Ich bin bei jedem Schritt dabei.\nNimm dir erst einen Moment zum Eingewöhnen.",
            "Hallo und willkommen. Ich bin {prefix}. Ich hoffe, du bist begeistert und bereit zu lernen. Alles ist vorbereitet und wartet auf dich.\nSag ein Wort und wir beginnen.",
            "Willkommen. Ich bin {prefix} und freue mich auf diese Reise mit dir. Mach dich mit dem Aufbau vertraut, bevor wir einsteigen.\nKein Zeitdruck.",
            "Hallo und willkommen. Ich bin {prefix}. Ich bin hier, um sicherzustellen, dass deine Erfahrung von Tag eins an reibungslos und klar ist.\nSag mir, wann du bereit bist.",
            "Willkommen an Bord. Ich bin {prefix} und freue mich, dich durch das Kommende zu führen. Es gibt viel wertvolles Material hier.\nMach es dir bequem und wir starten bald.",
            "Schön, dass du hier bist. Ich bin {prefix}. Dieser Kurs ist darauf ausgelegt, nützlich und interessant zu sein, und ich bin dein Guide.\nNimm dir Zeit, bevor wir beginnen.",
            "Hallo, willkommen. Ich bin {prefix}, dein Lernbegleiter. Ich bin hier, um sicherzustellen, dass du dich nie verloren oder überfordert fühlst.\nWenn du bereit bist, starten wir gemeinsam.",
            "Willkommen. Ich bin {prefix}. Du stehst kurz davor, etwas Großartiges zu beginnen, und ich bin bei jeder Lektion an deiner Seite.\nMach es dir bequem und sag mir, wann du bereit bist.",
            "Hallo und willkommen. Ich bin {prefix}. Ich freue mich wirklich, heute Teil deiner Lernreise zu sein.\nNimm dir einen Moment, mach es dir bequem und wir beginnen, wenn du bereit bist.",
            "Willkommen. Schön, dich hier zu sehen. Ich bin {prefix} und begleite dich mit Sorgfalt und Klarheit durch den Kurs.\nSchau dich erst um, dann tauchen wir gemeinsam ein.",
            "Hallo und willkommen. Ich bin {prefix}. Ich bin hier, um deine Lernerfahrung so produktiv und angenehm wie möglich zu machen.\nSag mir, wann du bereit bist.",
            "Willkommen. Ich bin {prefix}, dein KI-Guide. Du bist am richtigen Ort und ich sorge dafür, dass jeder Schritt klar und sicher ist.\nWenn du bereit bist, starten wir.",
            "Hallo, willkommen. Ich bin {prefix}. Ich bin hier, um dich von der ersten bis zur letzten Lektion zu begleiten.\nNimm dir Zeit zum Eingewöhnen und dann starten wir gemeinsam.",
        ],
    },

    # ── Italian ───────────────────────────────────────────────────────────────
    "it": {
        "intro": [
            "Ciao, sono {prefix}, la tua guida di apprendimento IA. Ti accompagnerò in ogni argomento con chiarezza e pazienza.\nNon esitare a rivedere qualsiasi sezione, sono sempre qui per aiutarti.",
            "Ciao, mi chiamo {prefix} e sarò il tuo compagno di apprendimento durante questo corso. Spiegazioni chiare, esempi utili e un ritmo su misura per te.\nCostruiamo insieme la tua comprensione, passo dopo passo.",
            "Benvenuto. Sono {prefix}, il tuo istruttore IA per questo percorso. Trasformerò idee complesse in lezioni semplici e comprensibili.\nVai al tuo ritmo, sarò qui quando avrai bisogno di me.",
            "Ciao, sono {prefix}! Pensami come il tuo tutor personale: paziente, concentrato e sempre pronto ad aiutarti.\nAffronteremo ogni concetto insieme. Quando sei pronto, iniziamo!",
            "Salve, sono {prefix}, il tuo assistente di apprendimento IA. Sono qui per guidarti passo dopo passo e aiutarti a costruire una vera comprensione.\nRendiamo questa esperienza fluida e gratificante.",
            "Ciao, sono {prefix}. Sono stato progettato per rendere la tua esperienza di apprendimento il più efficace possibile. Nessuna fretta, nessuna confusione, solo una guida chiara.\nPronto a iniziare?",
            "Ciao, mi chiamo {prefix}. Sono qui per trasformare argomenti complessi in lezioni chiare e gestibili. Puoi contare su di me.\nCominciamo quando sei pronto.",
            "Benvenuto nel corso. Sono {prefix}, il tuo assistente di apprendimento IA. Sarò con te ad ogni passo, spiegando concetti e aiutandoti ad avanzare.\nInizia quando ti senti a tuo agio.",
            "Ciao, sono {prefix}, e sono entusiasta di guidarti in questa esperienza di apprendimento. Andremo ad un ritmo confortevole per assicurarci che tutto sia ben assimilato.\nIniziamo questo percorso insieme.",
            "Ciao, sono {prefix}. Sono stato progettato affinché il tuo apprendimento sia fluido ed efficace. Nessuna fretta, solo una guida chiara.\nPronto a iniziare?",
            "Ciao, sono {prefix}, la tua guida per questo corso. L'apprendimento funziona meglio quando sembra naturale, quindi manterrò tutto comprensibile e chiaro.\nAndiamo!",
            "Ciao, mi chiamo {prefix}. Sono qui per supportare il tuo percorso di apprendimento dall'inizio alla fine con pazienza, chiarezza e incoraggiamento.\nQuando sei pronto, cominciamo.",
            "Ciao, sono {prefix}, la tua guida dedicata. Pensami come un amico ben informato, sempre pronto a spiegare, ripassare e aiutarti a crescere.\nRendiamo l'apprendimento piacevole.",
            "Ciao, sono {prefix}. Ti guiderò con spiegazioni chiare e un ritmo progettato per costruire la tua fiducia.\nNessuna pressione, andiamo al tuo ritmo.",
            "Ciao, mi chiamo {prefix} e sono il tuo istruttore IA. Ogni lezione che offro è progettata per essere chiara, pratica e facile da ricordare.\nIniziamo ora questo percorso di apprendimento.",
            "Ciao, sono {prefix} e sono contento che tu sia qui. Mi assicurerò che ogni argomento sia accessibile, indipendentemente dal tuo punto di partenza.\nImpariamo insieme.",
            "Ciao, sono {prefix}. Ogni lezione si basa sulla precedente per farti sentire sempre supportato.\nSeguimi e ce la faremo insieme.",
            "Ciao, sono {prefix}. Che tu sia un principiante o stia rinfrescando le tue conoscenze, mi assicurerò che ogni concetto arrivi chiaramente.\nProcediamo passo dopo passo.",
            "Buongiorno, sono {prefix}, la tua guida IA personale per questo corso. Il mio compito è rendere l'apprendimento accessibile, non opprimente.\nLavoriamo ad un ritmo che si adatti a te.",
            "Ciao, sono {prefix}. Sono qui per trasformare argomenti complessi in lezioni chiare e gestibili. Puoi contare su di me.\nCominciamo quando vuoi.",
        ],
        "welcome": [
            "Benvenuto. Sono {prefix} e sono contento che tu sia qui. Prenditi un momento per esplorare il contenuto del corso.\nQuando sei pronto, ci tuffiamo insieme.",
            "Ciao e benvenuto. Che piacere averti con noi. Sono {prefix} e sarò qui per supportarti durante tutto il corso.\nNessuna fretta, esplora al tuo ritmo e dimmi quando sei pronto.",
            "Benvenuto a bordo. Sono {prefix}. Questo è il tuo spazio per imparare, crescere e fare domande senza esitazione.\nDai un'occhiata a ciò che ti aspetta e inizieremo quando ti sentirai pronto.",
            "Ciao e benvenuto. Sono {prefix}, la tua guida per questo corso. Tutto ciò di cui hai bisogno è qui e ti aiuterò a sfruttarlo al massimo.\nEsplora e iniziamo quando sei a tuo agio.",
            "Benvenuto. Che bello che tu sia qui. Sono {prefix} e insieme avremo una grande esperienza di apprendimento.\nPrenditi il tempo per sistemarti, sarò qui quando vorrai iniziare.",
            "Ciao, benvenuto. Sono {prefix}. Hai fatto una scelta eccellente iniziando questo corso e sono qui perché tu possa trarne il massimo.\nQuando sei pronto, cominciamo.",
            "Benvenuto nel corso. Sono {prefix}. Respira, guarda intorno a te e sappi che sei in buone mani.\nIniziamo quando lo dici tu.",
            "Che piacere averti qui. Sono {prefix} e questo è l'inizio di qualcosa di molto prezioso. Sarò con te ad ogni passo.\nPrenditi un momento per sistemarti prima.",
            "Ciao e benvenuto. Sono {prefix}. Spero che tu sia entusiasta e pronto ad imparare. Tutto è pronto e ti aspetta.\nDi' solo una parola e iniziamo.",
            "Benvenuto. Sono {prefix} e non vedo l'ora di percorrere questo cammino con te. Familiarizzati con il contenuto prima di immergerti.\nNessuna fretta.",
            "Ciao e benvenuto. Sono {prefix}. Sono qui per assicurarmi che la tua esperienza sia fluida, chiara e davvero utile fin dal primo giorno.\nDimmi quando sei pronto per iniziare.",
            "Benvenuto a bordo. Sono {prefix} e sono entusiasta di guidarti in ciò che ti aspetta. C'è molto materiale di valore qui.\nSistémati e inizieremo presto.",
            "Che bello che tu sia qui. Sono {prefix}. Questo corso è progettato per essere utile e coinvolgente e sarò la tua guida per tutto il tempo.\nPrenditi il tempo prima che iniziamo.",
            "Ciao, benvenuto. Sono {prefix}, la tua guida di apprendimento. Sono qui per assicurarmi che tu non ti senta mai perso o sopraffatto.\nQuando sei pronto, iniziamo insieme.",
            "Benvenuto. Sono {prefix}. Stai per iniziare qualcosa di grandioso e sarò al tuo fianco ad ogni lezione.\nSistémati e dimmi quando sei pronto.",
            "Ciao e benvenuto. Sono {prefix}. Sono davvero felice di far parte del tuo percorso di apprendimento oggi.\nPrenditi un momento, mettiti a tuo agio e iniziamo quando sei pronto.",
            "Benvenuto. Che bello vederti qui. Sono {prefix} e ti guiderò con cura e chiarezza durante tutto il corso.\nEsplora prima, poi ci tuffiamo insieme.",
            "Ciao e benvenuto. Sono {prefix}. Sono qui per rendere la tua esperienza di apprendimento il più produttiva e piacevole possibile.\nDimmi quando sei pronto per iniziare.",
            "Benvenuto. Sono {prefix}, la tua guida IA. Sei nel posto giusto e mi assicurerò che ogni passo avanti sia chiaro e sicuro.\nQuando sei pronto, iniziamo.",
            "Ciao, benvenuto. Sono {prefix}. Sono qui per supportarti dalla prima all'ultima lezione.\nPrenditi il tempo per sistemarti, poi iniziamo insieme.",
        ],
    },
}

# Indian language codes → use English templates
INDIAN_LANG_PREFIXES = {'hi', 'pa'}

def get_templates(lang_code):
    prefix = lang_code.split('-')[0].lower()
    if prefix in INDIAN_LANG_PREFIXES:
        return TEMPLATES['en']
    if prefix in ('de', 'nl'):
        return TEMPLATES['de']
    return TEMPLATES.get(prefix, TEMPLATES['en'])

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
    lang_code = item.get('language', 'en')
    tmpl = get_templates(lang_code)
    seed_val = int(hashlib.md5((name + voice + 'msg').encode()).hexdigest(), 16)
    intro_msg   = tmpl['intro'][seed_val % len(tmpl['intro'])].format(prefix=voice_name)
    welcome_msg = tmpl['welcome'][(seed_val // 7) % len(tmpl['welcome'])].format(prefix=voice_name)

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
        "name": "Audio Models - Bulk Create (Filtered)",
        "_postman_id": "audio-models-bulk-filtered-001",
        "description": f"Auto-generated (filtered): {len(items)} audio models, 4 requests each ({len(items) * 4} total). Languages: English, Spanish, French, Japanese, German/Dutch, Italian, Hindi, Punjabi. Flow per model: 1) Create, 2) Intro message, 3) Welcome message, 4) Activate.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "variable": [
        {"key": "current_audio_model_uuid", "value": "", "type": "string"},
    ],
    "item": collection_items
}

out = "c:/dhindsa/01 temp_JSON Collection Postman/audio_models_bulk_create_filtered.postman_collection.json"
with open(out, 'w', encoding='utf-8') as f:
    json.dump(collection, f, indent=2, ensure_ascii=False)

print(f"Done! {len(items)} filtered folders x 4 requests = {len(items) * 4} total requests")
print(f"File: {out}")
