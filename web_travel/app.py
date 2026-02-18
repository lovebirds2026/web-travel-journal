from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'It XXworks!\nLovebirds® 2026 Dev domain\n\nPython 3.13'

if __name__ == '__main__':
    app.run(debug=True) # export this to env var


