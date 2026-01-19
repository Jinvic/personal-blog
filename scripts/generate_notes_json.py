import yaml
import json
import os

os.makedirs('.github/sync-data', exist_ok=True)

with open('sync-list.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

notes = config.get('notes', [])
print(f'共 {len(notes)} 篇笔记')

with open('.github/sync-data/notes.json', 'w', encoding='utf-8') as f:
    json.dump(notes, f, ensure_ascii=False, indent=2)