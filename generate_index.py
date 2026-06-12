import requests
import os

# 個人配下は対象から外すのでコメント化
# ORG = "hanihatena35-prog" # 個人ユーザー
ORG_NAME = "FEEL-TECH-TEST" # 組織ユーザー

# GitHub Actionsの場合はトークンを環境変数から取得（未設定でも動作する）
TOKEN = os.environ.get("ORG_TOKEN", "")
# Debug追加
print(f"トークン取得: {'あり' if TOKEN else 'なし'}")

HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

# 個人配下のリポジトリは対象から外すのでコメント化
# 個人配下のリポジトリを取得
# url = f"https://api.github.com/users/{ORG}/repos"  #Github API使用
# res = requests.get(url, headers=HEADERS)
# repos = res.json()

# Organization配下のリポジトリを取得
org_url = f"https://api.github.com/orgs/{ORG_NAME}/repos?type=all"  #Github API使用
org_res = requests.get(org_url, headers=HEADERS)
org_repos = org_res.json()

# デバック
print(f"Org API status: {org_res.status_code}")
# 個人配下のリポジトリは対象から外すのでコメント化
# print(f"=== 個人リポジトリ数: {len(repos)} ===")
# for r in repos:
#    print(f"  -  {r['name']} (Private: {r['private']})")

print(f"=== Organizationリポジトリ数: {len(org_repos)} ===")
for r in org_repos:
    print(f"  -  {r['name']} (Private: {r['private']})")

# リポジトリを結合
# repos = repos + org_repos
repos = org_repos  # 個人配下は対象から外すので組織配下のみ使用

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
pages_cards = ""    # Pages用のカードHTMLを格納する変数
releases_cards = ""   # Releases用のカードHTMLを格納する変数

for repo in repos:
    name = repo["name"]
    description = repo["description"] or ""
    owner = repo["owner"]["login"]  # オーナー名をAPIレスポンスから取得

    #　公開repoのみ対象
    #　ひとまずPublicも対象にするので下記をコメント化
    # if repo["private"]:
    #     continue

    #　表示対象を絞る（任意：prefix)
    if not (name.startswith("project-doc") or name.startswith("Organization_")):
       continue

    # pages_url = f"https://{owner}.github.io/{name}/" #Pages URL　ownerに修正

    #　Releases APIで最新リリースを取得
    releases_api = f"https://api.github.com/repos/{owner}/{name}/releases"  #ownerに修正
    rel_res = requests.get(releases_api, headers=HEADERS)

    # デバッグ
    print(f"Releases API [{name}] status: {rel_res.status_code}")
    print(f"Releases response: {rel_res.json()}")
    
    releases = rel_res.json()

    #　リリースがある場合だけボタンを追加
    releases_btn = ""
    if isinstance(releases, list) and len(releases) > 0:
        release_url = releases[0]["html_url"] # 最新リリースのURL
        release_tag = releases[0].get("tag_name", "latest") # 最新リリースのタグ名
        releases_btn = f'<a href="{release_url}" class="btn" target="_blank" rel="noopener">最新リリース ({release_tag})</a>'
    
    #　PagesのAPIで有効/無効を確認
    pages_api = f"https://api.github.com/repos/{owner}/{name}/pages"
    pages_res = requests.get(pages_api, headers=HEADERS)
    pages_btn = ""
    if pages_res.status_code == 200:
        pages_url = f"https://{owner}.github.io/{name}/" # APIからURLを取得、なければ従来のURL
        pages_btn = f'<a href="{pages_url}" class="btn" target="_blank" rel="noopener">ダウンロードページへ</a>'

    card = f"""
    <div class="card">
        <h2>📂{name}</h2>
        <p>{description}</p>
        {pages_btn}
        {releases_btn}
    </div>
    """

    # Releaseがあるカードは下、ないカードは上に振り分け
    if releases_btn:
        releases_cards += card
    else:
        pages_cards += card

# Pages用を先に、Release用を後にまとめて出力
html += pages_cards
html += releases_cards
html += "</div></body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)