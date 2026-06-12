#!/usr/bin/env python3
"""Upload all key files to GitHub using Contents API"""
import base64, json, urllib.request, urllib.error, os, sys

TOKEN = 'ghp_mm…eKmp'
REPO = 'lofy0115/chuangyebang'
headers = {'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'}

def upload_file(path, message=None):
    if message is None:
        message = f'Update {path}'
    content = open(path, 'rb').read()
    encoded = base64.b64encode(content).decode('utf-8')

    # Get current SHA if exists
    req = urllib.request.Request(
        f'https://api.github.com/repos/{REPO}/contents/{path}',
        headers=headers
    )
    sha = None
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        current = json.loads(resp.read())
        sha = current['sha']
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f'FAIL (get): {path} - {e.code}')
            return False
    except Exception as e:
        print(f'WARN: {path} - {e}')

    payload = {'message': message, 'content': encoded}
    if sha:
        payload['sha'] = sha

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f'https://api.github.com/repos/{REPO}/contents/{path}',
        data=data,
        headers=headers,
        method='PUT'
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        print(f'OK: {path}')
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        print(f'FAIL: {path} - HTTP {e.code}: {body}')
        return False

# Backend files
backend_files = [
    'backend/app/main.py',
    'backend/app/api/workflow_routes.py',
    'backend/app/services/ai_analysis_service.py',
    'backend/app/services/profit_model_service.py',
    'backend/app/services/roadmap_service.py',
    'backend/requirements.txt',
]

# Frontend files
frontend_files = [
    'frontend/index.html',
    'frontend/standalone.html',
    'frontend/manifest.json',
    'frontend/sw.js',
    'frontend/web/index.html',
    'frontend/web/manifest.json',
]

# Workflow
workflow_files = [
    '.github/workflows/flutter-build.yml',
]

all_files = backend_files + frontend_files + workflow_files

print('Uploading files to GitHub...')
for f in all_files:
    if os.path.exists(f):
        upload_file(f, f'Update {f}')
    else:
        print(f'SKIP (not found): {f}')

print('\nDone!')