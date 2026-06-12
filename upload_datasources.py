#!/usr/bin/env python3
"""推送到 GitHub - 数据源插件系统"""
import os, base64, json, requests

REPO = "lofy0115/chuangyebang"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "ghp_mmWGrdHsVvGNwIpr2eKmpHuwyJqH2ceKmp")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

def get_sha(path):
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{path}", headers=HEADERS)
    return r.json().get("sha") if r.status_code == 200 else None

def upload(path, content):
    data = base64.b64encode(content.encode()).decode()
    payload = {"message": f"Update {path}", "content": data}
    sha = get_sha(path)
    if sha: payload["sha"] = sha
    r = requests.put(f"https://api.github.com/repos/{REPO}/contents/{path}", headers=HEADERS, json=payload)
    print(f"  {'✅' if r.status_code in (200,201) else '❌'} {path} ({r.status_code})")
    return r

files = {
    "backend/app/datasources/__init__.py": open("backend/app/datasources/__init__.py").read(),
    "backend/app/datasources/base_datasource.py": open("backend/app/datasources/base_datasource.py").read(),
    "backend/app/datasources/weibo_datasource.py": open("backend/app/datasources/weibo_datasource.py").read(),
    "backend/app/datasources/international_datasource.py": open("backend/app/datasources/international_datasource.py").read(),
    "backend/app/datasources/datasource_manager.py": open("backend/app/datasources/datasource_manager.py").read(),
    "backend/app/api/workflow_routes.py": open("backend/app/api/workflow_routes.py").read(),
}

for path, content in files.items():
    upload(path, content)

print("\n触发 APK 构建...")
r = requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/flutter-build.yml/dispatches",
    headers=HEADERS, json={"ref": "main"})
print(f"  {'✅' if r.status_code == 204 else '❌'} 触发构建 ({r.status_code})")