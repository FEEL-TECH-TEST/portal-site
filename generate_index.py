import requests

ORG = "hanihatena35-prog" # ユーザー名かOrgazination

url = f"https://api.github.com/users/{ORG}/repos"  #Github API使用

res = requests.get(url)
repos = res.json()

html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>ダウンロードポータル</title>
</head>
<body>
<h1>ダウンロードポータル</h1>
<ul>
"""

for repo in repos:
    name = repo["name"]

    #　公開repoのみ対象
    #　ひとまずPublicも対象にするので下記をコメント化
    # if repo["private"]:
    #     continue

    #　表示対象を絞る（任意：prefix)
    if not name.startswith("project-"):
       continue

    pages_ur1 = f"https://{ORG}.github.io/{name}/" #Pages URL

    html += f'<li><a href="{pages_ur1}" target="_blank">📂{name}</a></li>\n'

html += "</ul></body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)