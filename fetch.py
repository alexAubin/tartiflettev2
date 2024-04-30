import requests
import json
from github import Github

g = Github(open("../apps/apps/.github_token").read().strip())

popularity_stars = requests.get("https://apps.yunohost.org/popularity.json").json()
catalog = requests.get("https://app.yunohost.org/default/v3/apps.json").json()
main_ci_apps_results = requests.get("https://ci-apps.yunohost.org/ci/api/results").json()
nextdebian_ci_apps_results = requests.get("https://ci-apps-bookworm.yunohost.org/ci/api/results").json()


def get_github_infos(github_orga_and_repo):

    repo = g.get_repo(github_orga_and_repo)
    infos = {}

    pulls = [p for p in repo.get_pulls()]

    infos["nb_prs"] = len(pulls)
    infos["nb_issues"] = repo.open_issues_count - infos["nb_prs"]

    testings = [p for p in pulls if p.head.ref == "testing"]
    testing = testings[0] if testings else None
    ci_auto_updates = [p for p in pulls if p.head.ref.startswith("ci-auto-update")]
    ci_auto_update = sorted(ci_auto_updates, key=lambda p: p.created_at, reverse=True)[0] if ci_auto_updates else None

    for p in ([testing] if testing else []) + ([ci_auto_update] if ci_auto_update else []):

        if p.head.label != "YunoHost-Apps:testing" and not (p.user.login == "yunohost-bot" and p.head.ref.startswith("ci-auto-update-")):
            continue

        infos["testing" if p.head.ref == "testing" else "ci-auto-update"] = {
            "branch": p.head.ref,
            "url": p.html_url,
            "timestamp_created": int(p.created_at.timestamp()),
            "timestamp_updated": int(p.updated_at.timestamp()),
            "statuses": [
                {"state": s.state, "context": s.context, "url": s.target_url, "timestamp": int(s.updated_at.timestamp())}
                for s in repo.get_commit(p.head.sha).get_combined_status().statuses
            ]
        }

    return infos

consolidated_infos = {}
for app, infos in catalog["apps"].items():

    if infos["state"] != "working":
        continue

    print(app)

    consolidated_infos[app] = {
        "public_level": infos["level"],
        "url": infos["git"]["url"],
        "timestamp_latest_commit": infos["lastUpdate"],
        "maintainers": infos["manifest"]["maintainers"],
        "antifeatures": infos["antifeatures"],
        "packaging_format": infos["manifest"]["packaging_format"],
        "popularity_stars": popularity_stars.get(app, 0),
        "ci_results": {
            "main": {
                "level": main_ci_apps_results[app]["level"],
                "timestamp": main_ci_apps_results[app]["timestamp"]
            } if app in main_ci_apps_results else None,
            "nextdebian": {
                "level": nextdebian_ci_apps_results[app]["level"],
                "timestamp": nextdebian_ci_apps_results[app]["timestamp"]
            } if app in nextdebian_ci_apps_results else None
        }
    }

    if infos["git"]["url"].lower().startswith("https://github.com/"):
        consolidated_infos[app].update(get_github_infos(infos["git"]["url"].lower().replace("https://github.com/", "")))

open("data.json", "w").write(json.dumps(consolidated_infos))