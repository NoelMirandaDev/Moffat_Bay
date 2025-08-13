from flask import Flask

app = Flask(__name__)

@app.route("/")
def landing():
    return "<h1>Welcome to Moffat Bay Lodge</h1>"

if __name__ == "__main__":
    app.run(debug=True)