import time
import json
import sys
import os
from flask import (
    Flask,
    send_from_directory,
    render_template,
    session,
    redirect,
    request,
)
from flask_babel import Babel
from flask_babel import gettext as _

###############################################################################

app = Flask(__name__, static_url_path="/assets", static_folder="assets")

# try:
#    config = toml.loads(open("config.toml").read())
# except Exception as e:
#    print(
#        "You should create a config.toml with the appropriate key/values, cf config.toml.example"
#    )
#    sys.exit(1)

if app.config.get("DEBUG"):
    app.config["TEMPLATES_AUTO_RELOAD"] = True

AVAILABLE_LANGUAGES = ["en"] + os.listdir("translations")


@app.template_filter("locale")
def get_locale(*args, **kwargs):
    # try to guess the language from the user accept
    # The best match wins.
    return request.accept_languages.best_match(AVAILABLE_LANGUAGES) or "en"


babel = Babel(app, locale_selector=get_locale)


@app.template_filter("days_ago")
def days_ago(timestamp):
    return int((time.time() - timestamp) / (60 * 60 * 24))

@app.context_processor
def utils():
    return {
        "locale": get_locale()
    }

###############################################################################


@app.route("/favicon.ico")
def favicon():
    return send_from_directory("assets", "favicon.png")


def get_dashboard_data():
    path = ".cache/dashboard.json"
    mtime = os.path.getmtime(path)
    if get_dashboard_data.mtime != mtime:
        get_dashboard_data.mtime = mtime
        dashboard_data = json.load(open(path))
        get_dashboard_data.cache = dashboard_data

    return get_dashboard_data.cache

get_dashboard_data.mtime = None
get_dashboard_data()

@app.route("/")
def index():
    return render_template(
        "index.html", data=get_dashboard_data()
    )


@app.route("/charts")
def charts():

    dashboard_data = get_dashboard_data()
    level_summary = {}
    for i in range(0,9):
        level_summary[i] = len([infos for infos in dashboard_data.values() if infos.get("ci_results", {}).get("main").get("level") == i])
    level_summary["unknown"] = len([infos for infos in dashboard_data.values() if infos.get("ci_results", {}).get("main").get("level") in [None, "?"]])

    return render_template(
        "charts.html",
        level_summary=level_summary,
        history=json.loads(open(".cache/history.json").read()),
        news_per_date=json.loads(open(".cache/news.json").read())
    )
