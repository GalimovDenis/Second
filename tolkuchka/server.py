from flask import render_template

import config

connex_app = config.connexian_app

connex_app.add_api("tolkuchka/openapi.yaml")


@connex_app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    connex_app.run(host="0.0.0.0", port=8080, debug=True)
