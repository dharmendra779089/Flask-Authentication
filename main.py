from app import app, db, User

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    is_debug = os.environ.get("FLASK_DEBUG", "True").lower() in ["true", "1"]
    app.run(host="0.0.0.0", port=port, debug=is_debug)
