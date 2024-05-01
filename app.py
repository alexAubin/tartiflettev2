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

###############################################################################


@app.template_filter("days_ago")
def days_ago(timestamp):
    return int((time.time() - timestamp) / (60 * 60 * 24))


###############################################################################


@app.route("/favicon.ico")
def favicon():
    return send_from_directory("assets", "favicon.png")


@app.route("/")
def index():
    return render_template(
        "index.html", data=json.loads(open(".cache/dashboard.json").read())
    )
