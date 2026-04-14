import json, urllib.request, urllib.error

BASE_URL = "https://core.ardoirse.com"

# ── Load token from .env ──────────────────────────────────────────────────────
import os
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
TOKEN = None
with open(_env_path) as f:
    for line in f:
        if line.startswith('BEARER_TOKEN='):
            TOKEN = line.split('=', 1)[1].strip()
            break
if not TOKEN or TOKEN == 'paste_your_token_here':
    raise SystemExit("ERROR: Set BEARER_TOKEN in .env file before running.")
if TOKEN.lower().startswith('bearer '):
    TOKEN = TOKEN[7:].strip()

print(f"Token loaded ({TOKEN[:20]}...)\n")

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'authorization': f'Bearer {TOKEN}',
    'origin': 'https://mission-control.ardoirse.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
}

# ── Fetch all pages until no more results ─────────────────────────────────────
def fetch_all_models():
    all_models = []
    page = 0
    while True:
        url = f"{BASE_URL}/a/audio-model?size=100&query=&page={page}"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        items = data.get('data', [])
        meta  = data.get('meta', {})
        if not items:
            break
        all_models.extend(items)
        total_pages = meta.get('pages', 1)
        print(f"  Fetched page {page+1}/{total_pages}: {len(items)} models")
        if page + 1 >= total_pages:
            break
        page += 1
    return all_models

print("Fetching all audio models...")
all_models = fetch_all_models()
print(f"Total fetched: {len(all_models)}\n")

# ── Filter models whose name starts with "0 " ─────────────────────────────────
to_delete = [m for m in all_models if m.get('name', '').startswith('0 ')]
print(f"Models with '0 ' prefix in name: {len(to_delete)}")
for m in to_delete:
    print(f"  - [{m['uuid']}] {m['name']}")

if not to_delete:
    print("\nNothing to delete.")
    raise SystemExit(0)

# ── Confirm before deleting ───────────────────────────────────────────────────
print(f"\nAbout to delete {len(to_delete)} models. Type 'yes' to confirm: ", end='')
confirm = input().strip().lower()
if confirm != 'yes':
    print("Aborted.")
    raise SystemExit(0)

# ── Delete each model ─────────────────────────────────────────────────────────
deleted = 0
failed = 0
for m in to_delete:
    uuid = m['uuid']
    name = m['name']
    url = f"{BASE_URL}/a/audio-model/{uuid}"
    req = urllib.request.Request(url, method='DELETE', headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"  DELETED: {name} ({uuid})")
            deleted += 1
    except urllib.error.HTTPError as e:
        print(f"  FAILED:  {name} ({uuid}) -> HTTP {e.code}")
        failed += 1

print(f"\nDone. Deleted: {deleted}, Failed: {failed}")
