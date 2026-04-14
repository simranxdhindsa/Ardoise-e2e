import json, urllib.request, urllib.error, os

BASE_URL = "https://core.ardoirse.com"

# ── Load .env ─────────────────────────────────────────────────────────────────
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
TOKEN = None
ORG_UUID = None
with open(_env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith('BEARER_TOKEN='):
            TOKEN = line.split('=', 1)[1].strip()
        elif line.startswith('ORG_UUID='):
            ORG_UUID = line.split('=', 1)[1].strip()

if not TOKEN or TOKEN == 'paste_your_token_here':
    raise SystemExit("ERROR: Set BEARER_TOKEN in .env file.")
if TOKEN.lower().startswith('bearer '):
    TOKEN = TOKEN[7:].strip()
if not ORG_UUID:
    raise SystemExit("ERROR: Set ORG_UUID in .env file.")

print(f"Token loaded  : {TOKEN[:20]}...")
print(f"Org UUID      : {ORG_UUID}\n")

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'authorization': f'Bearer {TOKEN}',
    'origin': 'https://mission-control.ardoirse.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def fetch_all_pages(base_url):
    """Paginate through all pages and return combined list."""
    all_items = []
    page = 0
    while True:
        url = f"{base_url}&page={page}" if '?' in base_url else f"{base_url}?page={page}"
        data = fetch_json(url)
        items = data.get('data', [])
        meta  = data.get('meta', {})
        if not items:
            break
        all_items.extend(items)
        total_pages = meta.get('pages', 1)
        print(f"  Page {page+1}/{total_pages}: {len(items)} items")
        if page + 1 >= total_pages:
            break
        page += 1
    return all_items

# ── Ask action ────────────────────────────────────────────────────────────────
print("What would you like to do?")
print("  1. Add audio models to org")
print("  2. Remove audio models from org")
print()
action = input("Enter 1 or 2: ").strip()
if action not in ('1', '2'):
    raise SystemExit("Invalid choice. Enter 1 or 2.")

# ── Helper: parse selection string like "1, 4-7, 9" ─────────────────────────
def parse_selection(s, max_idx):
    selected = set()
    for part in s.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-', 1)
            selected.update(range(int(a), int(b) + 1))
        elif part.isdigit():
            selected.add(int(part))
    return [i for i in sorted(selected) if 1 <= i <= max_idx]

# ── ADD ───────────────────────────────────────────────────────────────────────
if action == '1':
    print("\nWhich models to add?")
    print("  1. Only models with '0 ' prefix (ones we configured)")
    print("  2. All models from catalog")
    print("  3. Pick manually from list")
    print()
    choice = input("Enter 1, 2 or 3: ").strip()
    if choice not in ('1', '2', '3'):
        raise SystemExit("Invalid choice.")

    print("\nFetching catalog audio models...")
    catalog = fetch_all_pages(f"{BASE_URL}/a/audio-model?size=100&query=")
    print(f"Total catalog models: {len(catalog)}")

    if choice == '1':
        models = [m for m in catalog if m.get('name', '').startswith('0 ')]
        print(f"Models with '0 ' prefix: {len(models)}")
    elif choice == '2':
        models = catalog
        print(f"All models selected: {len(models)}")
    else:
        # Print numbered list
        print()
        for i, m in enumerate(catalog, 1):
            print(f"  {i:>3}. {m['name']}")
        print()
        raw = input("Enter numbers/ranges to add (e.g. 1, 4-7, 9): ").strip()
        indices = parse_selection(raw, len(catalog))
        models = [catalog[i - 1] for i in indices]
        print(f"\nSelected {len(models)} models:")
        for m in models:
            print(f"  - {m['name']}")

    if not models:
        raise SystemExit("No models found to add.")

    print(f"\nAbout to add {len(models)} models to org {ORG_UUID}.")
    confirm = input("Type 'yes' to confirm: ").strip().lower()
    if confirm != 'yes':
        raise SystemExit("Aborted.")

    added = 0
    failed = 0
    add_headers = {**HEADERS, 'content-type': 'application/json'}
    for m in models:
        url = f"{BASE_URL}/a/org/{ORG_UUID}/audio-model"
        body = json.dumps({"audio_model_id": m['uuid']}).encode()
        req = urllib.request.Request(url, data=body, headers=add_headers, method='POST')
        try:
            with urllib.request.urlopen(req) as resp:
                print(f"  ADDED:  {m['name']}")
                added += 1
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            print(f"  FAILED: {m['name']} -> HTTP {e.code}: {err_body[:80]}")
            failed += 1

    print(f"\nDone. Added: {added}, Failed: {failed}")

# ── REMOVE ────────────────────────────────────────────────────────────────────
elif action == '2':
    print("\nWhich models to remove?")
    print("  1. Only models with '0 ' prefix")
    print("  2. All models currently in org")
    print()
    choice = input("Enter 1 or 2: ").strip()
    if choice not in ('1', '2'):
        raise SystemExit("Invalid choice.")

    print("\nFetching org audio models...")
    org_models = fetch_all_pages(f"{BASE_URL}/a/org/{ORG_UUID}/audio-model?size=100&query=")
    print(f"Total models in org: {len(org_models)}")

    # org response: { uuid: <link_uuid>, audio_model: { uuid, name, ... } }
    def model_name(m): return m.get('audio_model', {}).get('name', m.get('name', ''))

    if choice == '1':
        models = [m for m in org_models if model_name(m).startswith('0 ')]
        print(f"Models with '0 ' prefix: {len(models)}")
    else:
        models = org_models

    if not models:
        raise SystemExit("No models found to remove.")

    print(f"\nModels to remove ({len(models)}):")
    for m in models:
        print(f"  - {model_name(m)} (link uuid: {m['uuid']})")

    print(f"\nAbout to remove {len(models)} models from org {ORG_UUID}.")
    confirm = input("Type 'yes' to confirm: ").strip().lower()
    if confirm != 'yes':
        raise SystemExit("Aborted.")

    removed = 0
    failed = 0
    for m in models:
        # DELETE uses the org-model link uuid
        url = f"{BASE_URL}/a/org/{ORG_UUID}/audio-model/{m['uuid']}"
        req = urllib.request.Request(url, headers=HEADERS, method='DELETE')
        try:
            with urllib.request.urlopen(req) as resp:
                print(f"  REMOVED: {model_name(m)}")
                removed += 1
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            print(f"  FAILED:  {model_name(m)} -> HTTP {e.code}: {err_body[:80]}")
            failed += 1

    print(f"\nDone. Removed: {removed}, Failed: {failed}")
