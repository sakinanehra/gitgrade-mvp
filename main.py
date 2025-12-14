from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()


def analyze_repo(repo_url):
    parts = repo_url.replace("https://github.com/", "").split("/")
    owner, repo = parts[0], parts[1]

    base = f"https://api.github.com/repos/{owner}/{repo}"

    contents = requests.get(f"{base}/contents").json()
    commits = requests.get(f"{base}/commits").json()
    languages = requests.get(f"{base}/languages").json()

    folders = [i["name"] for i in contents if i["type"] == "dir"]
    files = [i["name"] for i in contents if i["type"] == "file"]

    return {
        "readme": any("readme" in f.lower() for f in files),
        "tests": any("test" in f.lower() for f in folders),
        "src": "src" in folders,
        "commits": len(commits) if isinstance(commits, list) else 0,
        "languages": list(languages.keys())
    }


def score_repo(a):
    score = 0
    score += 15 if a["readme"] else 0
    score += 15 if a["tests"] else 0
    score += 10 if a["src"] else 0
    score += 15 if a["commits"] > 20 else 10 if a["commits"] > 5 else 0
    score += min(len(a["languages"]) * 5, 15)

    level = "Advanced" if score >= 80 else "Intermediate" if score >= 50 else "Beginner"
    return score, level


def roadmap(a):
    steps = []
    if not a["readme"]:
        steps.append(
            "Add a README with project overview and setup instructions")
    if not a["tests"]:
        steps.append("Write unit tests for core features")
    if not a["src"]:
        steps.append("Organize code into a src folder")
    if a["commits"] < 10:
        steps.append("Commit code regularly with meaningful messages")
    steps.append("Add CI/CD using GitHub Actions")
    return steps


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <body style="font-family: Arial; padding: 40px">
        <h2>GitGrade – GitHub Repository Analyzer</h2>
        <form action="/analyze">
            <input name="repo" size="50" placeholder="GitHub Repo URL" required/>
            <button type="submit">Analyze</button>
        </form>
    </body>
    </html>
    """


@app.get("/analyze", response_class=HTMLResponse)
def analyze(repo: str):
    a = analyze_repo(repo)
    score, level = score_repo(a)
    steps = roadmap(a)

    return f"""
    <html>
    <body style="font-family: Arial; padding: 40px">
        <h2>Analysis Result</h2>
        <p><b>Score:</b> {score}/100 ({level})</p>
        <p><b>Summary:</b> Clean structure but missing some best practices.</p>
        <h3>Personalized Roadmap</h3>
        <ul>
            {''.join(f"<li>{s}</li>" for s in steps)}
        </ul>
        <a href="/">Analyze another repo</a>
    </body>
    </html>
    """


import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
