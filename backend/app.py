import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from models import db
from routes import api


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///collections.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.environ.get(
        "UPLOAD_FOLDER", os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    )
    app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB upload limit

    CORS(app)  # allow the React dev server to call the API
    db.init_app(app)
    app.register_blueprint(api, url_prefix="/api")

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    with app.app_context():
        db.create_all()
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
