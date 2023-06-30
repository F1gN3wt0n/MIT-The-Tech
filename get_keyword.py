from flask import Flask, request, render_template

app = Flask(__name__, template_folder='')

@app.route('/', methods = ["GET", "POST"])
def initial():
    return render_template("index.html")
def get_keyword():
    return render_template("index.html")

if __name__ == "__main__":
        app.run(debug=True)
