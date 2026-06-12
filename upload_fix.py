import base64, json, urllib.request, urllib.error

TOKEN = '<TOKEN_PLACEHOLDER>'
REPO = 'lofy0115/chuangyebang'

path = '.github/workflows/flutter-build.yml'
content = open(path, 'rb').read()
encoded = base64.b64encode(content).decode('utf-8')

req = urllib.request.Request(
    f'https://api.github.com/repos/{REPO}/contents/{path}',
    headers={'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
)
resp = urllib.request.urlopen(req, timeout=10)
current = json.loads(resp.read())
sha = current['sha']

payload = {
    'message': 'Add android licenses acceptance',
    'content': encoded,
    'sha': sha
}
data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(
    f'https://api.github.com/repos/{REPO}/contents/{path}',
    data=data,
    headers={'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json'},
    method='PUT'
)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    result = json.loads(resp.read())
    print('OK:', result['commit']['sha'][:8])
except urllib.error.HTTPError as e:
    print('FAIL:', e.code, e.read().decode()[:300])