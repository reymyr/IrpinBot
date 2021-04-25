import string
from stringMatching import *
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

keywords = ["Kuis", "Ujian", "Tucil", "Tubes", "Praktikum"]
helpWords = ["bisa", "kemampuan", "fitur", "help", "bantuan", "tolong"]
updateWords = ["diubah","diundur","dimajukan"]

class Task(db.Model):
    id_task = db.Column(db.Integer, primary_key = True)
    tanggal = db.Column(db.Date, default=datetime.date.today)
    kode = db.Column(db.String(10))
    jenis = db.Column(db.String(10))
    topik = db.Column(db.String(100))

class Keyword(db.Model):
    id_keyword = db.Column(db.Integer, primary_key = True)
    jenis = db.Column(db.String(10))


messages=[]

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

@app.route('/send', methods=['POST'])
def send():
    msg = request.form['message']
    if msg:
        reply = processMessage(msg)
        messages.append(['sent', request.form['message']])
        messages.append(['received', reply])
    return redirect("/")


def processMessage(text):
    print(keywords)
    # If ada 4 komponen, add task

    if len(getKodeMatkul(text)) == 0:
        if (textContains(text,helpWords)):
            return getHelp(text)
        elif (textContains(text,updateWords)):
            return updateTasksDeadline(text)
        return getTasks(text)
    elif len(getKodeMatkul(text)[0]) != 0:
        return getTasksDeadline(text)

def getTasks(text):
    seluruh = ["sejauh ini", "sampai sekarang", "semuanya", "sampe sekarang", "semua"]
    between = [["antara", "sampai"], ["antara", "dan"], ["dari", "sampai"]]
    nWeek = ["minggu ke depan", "minggu dari sekarang"]
    nDays = ["hari ke depan", "hari dari sekarang"]
    hariIni = ["hari ini"]
    today = datetime.date.today()
    start = None
    end = None
    jenis = None
    timeValid = False
    keyValid = False
    all = False

    if textContains(text, seluruh):
        all = True
        timeValid = True
    elif any(textContains(text, keys, all=True) for keys in between):
        print("hai")
        dates = getDates(text)
        if len(dates) == 2:
            start = min(datetime.datetime.strptime(dates[0], "%d/%m/%Y").date(), datetime.datetime.strptime(dates[1], "%d/%m/%Y").date())
            end = max(datetime.datetime.strptime(dates[0], "%d/%m/%Y").date(), datetime.datetime.strptime(dates[1], "%d/%m/%Y").date())
            timeValid = True
    elif textContains(text, nWeek):
        match = re.search(r"\b\d+ minggu", text, re.IGNORECASE)
        if match:
            start = today
            end = start + datetime.timedelta(weeks=int(match.group().split(" ")[0]))
            timeValid = True
    elif textContains(text, nDays):
        match = re.search(r"\b\d+ hari", text, re.IGNORECASE)
        if match:
            start = today
            end = start + datetime.timedelta(days=int(match.group().split(" ")[0]))
            timeValid = True
    elif textContains(text, hariIni):
        start = today
        end = today
        timeValid = True
    
    for key in keywords:
        jenis = key
        if textContains(text, [key]):
            keyValid = True
            break
    
    if not keyValid:
        keyValid = textContains(text, ["Deadline"])
        jenis = "Deadline"

    if keyValid and timeValid:
        tasks = None
        print(jenis, start, end)
        if all:
            if jenis == "Deadline":
                tasks = Task.query.all()
            else:
                tasks = Task.query.filter(Task.jenis == jenis).all()
        else:
            if jenis == "Deadline":
                tasks = Task.query.filter((Task.tanggal >= start) & (Task.tanggal <= end)).all()
            else:
                tasks = Task.query.filter((Task.jenis == jenis) & (Task.tanggal >= start) & (Task.tanggal <= end)).all()

        if len(tasks) == 0:
            reply = "Tidak ada"
        else:
            reply = '[Daftar Deadline]<br>'
            for i in range(len(tasks)):
                task = tasks[i]
                reply += str(i+1) + ". (ID: " + str(task.id_task) + ") " + task.tanggal.strftime("%d/%m/%Y") + " - " + task.kode + " - " + task.jenis + " - " + task.topik + '<br>'
        return reply
    else:
        return "ga valid bro"

def getTasksDeadline(text):
    kodeMatkul = getKodeMatkul(text)
    today = datetime.date.today()
    jenis = None
    keyValid = False

    for key in keywords:
        if((key == "Tubes") or (key == "Tucil")):
            jenis = key
            if textContains(text, [key]):
                keyValid = True
                break
    
    if (keyValid):
        tasks = None
        #print(jenis, today)
        tasks = Task.query.filter((Task.jenis == jenis) & (Task.tanggal >= today) & (Task.kode == kodeMatkul[0])).all()

        if len(tasks) == 0:
            reply = "Tidak ada"
        else:
            reply = '[Deadline ' + jenis + ' ' + kodeMatkul[0] + ']<br>'
            for i in range(len(tasks)):
                task = tasks[i]
                reply += str(i+1) + ". " + task.tanggal.strftime("%d/%m/%Y") + " - " + task.jenis + " - " + task.topik + '<br>'
        return reply
    else:
        return "ga valid bro"

def updateTasksDeadline(text):
    kataKunci = ["diubah","diundur","dimajukan"]
    date = None
    keyValid = False
    id = None

    for key in kataKunci:
        if textContains(text,[key]):
            keyValid = True
            break
    
    if keyValid:
        tasks = None
        id = getIdTask(text)
        date = getDates(text)

        if (len(id) == 0):
            return "ga valid bro"
        if (len(date) == 0):
            return "ga valid bro"
        # print(date[0])

        tasks = Task.query.filter((Task.id_task == int(id[0]))).all()

        if (len(tasks)) == 0:
            reply = "Task yang dimaksud tidak dikenali mimin:("
        else:
            dateFormat = datetime.datetime.strptime(date[0],"%d/%m/%Y").date()
            Task.query.filter((Task.id_task == int(id[0]))).update({Task.tanggal: dateFormat})
            db.session.commit()
            reply = "Deadline task " + id[0] + " " + key + " menjadi " + date[0]
        return reply
    else:
        return "ga valid bro"

def getHelp(text):
    fitur = ["Menambahkan task baru", "Melihat daftar task", "Melihat deadline task tertentu", "Memperbaharui task tertentu", "Menandai task yang sudah dikerjakan"]

    reply = None
    if textContains(text, helpWords):
        reply = '[Fitur]<br>'
        for i in range(len(fitur)):
            reply += str(i+1) + ". " + fitur[i] + '<br>'
        
        reply += '<br>'
        reply += '[Kata Penting]<br>'
        for i in range(len(keywords)):
            reply += str(i+1) + ". " + keywords[i] + '<br>'
        return reply
    else:
        return "ga valid bro"

if __name__ == "__main__":
    app.run(debug=True,threaded=True)