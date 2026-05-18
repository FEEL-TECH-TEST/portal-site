import requests

ORG = "hanihatena35-prog"
REPOS = ["project-docs1", "project-docs2", "project-docs3"]

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

for repo in REPOS:
    pages_ur1 = f"https://{ORG}.github.io/{repo}/"
    html += f'<li><a href="{pages_ur1}">{repo}</a></li>\n'

html += """
</ul>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)