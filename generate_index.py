import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

ORG_NAME = "FEEL-TECH-TEST"  # 組織ユーザー

# GitHub Actionsの場合はトークンを環境変数から取得
TOKEN = os.environ.get("ORG_TOKEN", "")
print(f"トークン取得: {'あり' if TOKEN else 'なし'}")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.mercy-preview+json"  # topics取得に必要
} if TOKEN else {
    "Accept": "application/vnd.github.mercy-preview+json"
}

# --------------------------------
# Organization repo取得（ページング対応）
# --------------------------------
repos = []
page = 1

while True:
    url = f"https://api.github.com/orgs/{ORG_NAME}/repos?type=all&per_page=100&page={page}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print(f"Error fetching repos (page={page}): {res.status_code} {res.text}")
        break

    data = res.json()
    if not data:
        break  # 取得するリポジトリがなくなったら終了

    repos.extend(data)
    print(f"  page {page}: {len(data)} 件取得（累計 {len(repos)} 件）")
    page += 1

print(f"=== Organizationリポジトリ総数: {len(repos)} ===")

# --------------------------------
# prefixフィルタ（APIを叩く前に絞り込む）
# --------------------------------
filtered_repos = [
    r for r in repos
    if r["name"].startswith("project-doc") or r["name"].startswith("Organization_")
]
print(f"=== prefixフィルタ後: {len(filtered_repos)} 件 ===")

# --------------------------------
# 各リポジトリの詳細情報を並列取得
# --------------------------------
def fetch_repo_detail(repo):
    """
    topics / releases / pages を並列取得してカード情報を返す。
    フィルタ条件を満たさない場合は None を返す。
    """
    name  = repo["name"]
    owner = repo["owner"]["login"]

    # topics を個別APIで確実に取得
    #    /orgs/.../repos の一覧APIはtopicsを返さない場合があるため個別取得が確実
    topics_res = requests.get(
        f"https://api.github.com/repos/{owner}/{name}/topics",
        headers=HEADERS
    )
    if topics_res.status_code == 200:
        topics = topics_res.json().get("names", [])
    else:
        topics = []

    # topicフィルタ（"project-doc" トピックがなければスキップ）
    if "project-doc" not in topics:
        return None

    description = repo.get("description") or ""

    # Releases APIで最新リリースを取得
    rel_res = requests.get(
        f"https://api.github.com/repos/{owner}/{name}/releases",
        headers=HEADERS
    )
    releases_btn = ""
    if rel_res.status_code == 200:
        releases = rel_res.json()
        if isinstance(releases, list) and len(releases) > 0:
            release_url = releases[0]["html_url"]
            release_tag = releases[0].get("tag_name", "latest")
            releases_btn = (
                f'<a href="{release_url}" class="btn" target="_blank" rel="noopener">'
                f'最新リリース ({release_tag})</a>'
            )

    # PagesのAPIで有効/無効を確認
    pages_res = requests.get(
        f"https://api.github.com/repos/{owner}/{name}/pages",
        headers=HEADERS
    )
    pages_btn = ""
    if pages_res.status_code == 200:
        pages_url = f"https://{owner}.github.io/{name}/"
        pages_btn = (
            f'<a href="{pages_url}" class="btn" target="_blank" rel="noopener">'
            f'ダウンロードページへ</a>'
        )

    # pagesがあればpages優先、なければreleases
    if pages_btn:
        display_btn = pages_btn
    elif releases_btn:
        display_btn = releases_btn
    else:
        display_btn = ""

    card = f"""
    <div class="card">
        <h2>📂{name}</h2>
        <p>{description}</p>
        {display_btn}
    </div>
    """

    # Releaseのみ（pagesなし）→ releases_cards、それ以外 → pages_cards
    bucket = "releases" if (releases_btn and not pages_btn) else "pages"

    return {"bucket": bucket, "card": card}


# 並列実行（最大10スレッド：GitHub APIのレート制限を考慮）
pages_cards   = ""
releases_cards = ""

print(f"=== 詳細情報を並列取得中（対象: {len(filtered_repos)} 件）===")
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(fetch_repo_detail, repo): repo for repo in filtered_repos}
    for future in as_completed(futures):
        result = future.result()
        if result is None:
            continue
        if result["bucket"] == "releases":
            releases_cards += result["card"]
        else:
            pages_cards += result["card"]

# --------------------------------
# HTML生成
# --------------------------------
html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>ダウンロードポータル</title>

<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
    background-color: #f5f6f8;
    margin: 0;
    padding: 20px;
}

h1 {
    text-align: center;
}

.container {
    max-width: 800px;
    margin: auto;
}

.card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
}

.card h2 {
    margin: 0;
}

.card p {
    color: #666;
    margin: 5px 0 10px 0;
}

.btn {
    display: inline-block;
    padding: 8px 14px;
    background: #0366d6;
    color: white;
    text-decoration: none;
    border-radius: 8px;
}

.btn:hover {
    background: #024c9a;
}
</style>

</head>
<body>
<h1>ダウンロードポータル</h1>
<div class="container">
"""

# Pages用を先に、Release用を後にまとめて出力
html += pages_cards
html += releases_cards
html += "</div></body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("=== index.html を生成しました ===")
html += "</div></body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
