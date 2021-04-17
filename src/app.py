from flask import Flask, render_template, request, redirect
app = Flask(__name__)

messages=[]

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

@app.route('/send', methods=['POST'])
def send():
    msg = request.form['message']
    if msg:
        messages.append(['sent', request.form['message']])
        messages.append(['received', request.form['message'][::-1]])
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True,threaded=True)