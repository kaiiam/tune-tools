from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create_chord_chart", methods=["POST", "GET"])
def create_chord_chart():
    if request.method == "POST":
        key = request.form.get('keybox')
        user_input = request.form["usr_txt"]
        cmd = f"python3 ../src/tune-tools.py -i '{str(user_input)}' -w -m 'create_chord_chart' -k '{key}' -n"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        stder = p.stderr.read()
        out, err = p.communicate()
        if not stder:
            result_list = out.split('\n')
            return render_template("create_chord_chart.html", content=result_list)
        else:
            result_list = stder.split('\n')
            return render_template("create_chord_chart.html", content=result_list)
    else:
        return render_template("post_create_chord_chart.html")


@app.route("/suggest_scales", methods=["POST", "GET"])
def suggest_scales():
    if request.method == "POST":
        key = request.form.get('keybox')
        user_input = request.form["usr_txt"]
        cmd = f"python3 ../src/tune-tools.py -i '{str(user_input)}' -w -m 'suggest_scales' -k '{key}' "
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        stder = p.stderr.read()
        out, err = p.communicate()
        if not stder:
            result_list = out.split('\n')
            return render_template("suggest_scales.html", content=result_list)
        else:
            result_list = stder.split('\n')
            return render_template("suggest_scales.html", content=result_list)
    else:
        return render_template("post_suggest_scales.html")


@app.route("/chord_fingerboard", methods=["POST", "GET"])
def chord_fingerboard():
    if request.method == "POST":
        instrument = request.form.get('instruments')
        key = request.form.get('keybox')
        user_input = request.form["usr_txt"]
        cmd = f"python3 ../src/tune-tools.py -i '{str(user_input)}' -w -m 'print_chord_fingerboard' -ins '{instrument}' -k '{key}' -n"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        stder = p.stderr.read()
        out, err = p.communicate()
        if not stder:
            result_list = out.split('\n')
            return render_template("chord_fingerboard.html", content=result_list)
        else:
            result_list = stder.split('\n')
            return render_template("chord_fingerboard.html", content=result_list)
    else:
        return render_template("post_chord_fingerboard.html")


@app.route("/scale_fingerboard", methods=["POST", "GET"])
def scale_fingerboard():
    if request.method == "POST":
        instrument = request.form.get('instruments')
        key = request.form.get('keybox')
        user_input = request.form["usr_txt"]
        cmd = f"python3 ../src/tune-tools.py -i '{str(user_input)}' -w -m 'print_scale_fingerboard' -ins '{instrument}' -k '{key}' "
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        stder = p.stderr.read()
        out, err = p.communicate()
        if not stder:
            result_list = out.split('\n')
            return render_template("scale_fingerboard.html", content=result_list)
        else:
            result_list = stder.split('\n')
            return render_template("scale_fingerboard.html", content=result_list)
    else:
        return render_template("post_scale_fingerboard.html")


if __name__ == "__main__":
    app.run(debug=False)