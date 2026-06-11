import requests
import os

ORG = "hanihatena35-prog" # ユーザー名かOrgazination

# GitHub Actionsの場合はトークンを環境変数から取得（未設定でも動作する）
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

url = f"https://api.github.com/users/{ORG}/repos"  #Github API使用

res = requests.get(url, headers=HEADERS)
repos = res.json()

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

h1{
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

for repo in repos:
    name = repo["name"]
    description = repo["description"] or ""

    #　公開repoのみ対象
    #　ひとまずPublicも対象にするので下記をコメント化
    # if repo["private"]:
    #     continue

    #　表示対象を絞る（任意：prefix)
    if not (name.startswith("project-") or name.startswith("Organization_")):
       continue

    pages_ur1 = f"https://{ORG}.github.io/{name}/" #Pages URL

    #　Releases APIで最新リリースを取得
    releases_api = f"https://api.github.com/repos/{ORG}/{name}/releases"
    rel_res = requests.get(releases_api, headers=HEADERS)
    releases = rel_res.json()

    #　リリースがある場合だけボタンを追加
    releases_btn = ""
    if isinstance(releases, list) and len(releases) > 0:
        release_url = releases[0]["html_url"] # 最新リリースのURL
        release_tag = releases[0].get("tag_name", "latest") # 最新リリースのタグ名
        releases_btn = f'<a href="{release_url}" class="btn" target="_blank" rel="noopener">最新リリース ({release_tag})</a>'

    html += f"""
    <div class="card">
        <h2>📂{name}</h2>
        <p>{description}</p>
        <a href="{pages_ur1}" class="btn" target="_blank" rel="noopener">ダウンロードページへ</a>
        {releases_btn}
    </div>
    """

html += "</div></body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)