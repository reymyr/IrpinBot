import string
from stringMatching import *
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vudbnpdnxobjpa:3898a90b83f4b374ec08fc1fedb87f7bb1787696f8722ea5a52ad4cd05e7c0be@ec2-52-45-73-150.compute-1.amazonaws.com:5432/dcvg700sjjstrh'
db = SQLAlchemy(app)

keywords = ["Kuis", "Ujian", "Tucil", "Tubes", "Praktikum"]
helpWords = ["bisa", "kemampuan", "fitur", "help", "bantuan", "tolong"]
updateWords = ["diubah","diundur","dimajukan"]
doneWords = ["selesai", "beres", "udah"]

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
    #first of all, check apakah ada kekeliruan di text
    listText = text.split(' ')
    errorMsg, foundError = recommendWord(listText)
    if foundError:
        return errorMsg


    # If ada 4 komponen, add task
    if (len(getDates(text)) > 0 or len(getDatesAlternate(text)) > 0) and len(getKodeMatkul(text)) > 0 and len(getTopic(text)) > 0:
        return addTasks(text)

    if len(getKodeMatkul(text)) == 0:
        if (textContains(text,updateWords)):
            return updateTasksDeadline(text)
        elif (textContains(text,doneWords)):
            return removeTask(text)
        elif (textContains(text,helpWords)):
            return getHelp(text)
        return getTasks(text)
    elif len(getKodeMatkul(text)[0]) != 0:
        return getTasksDeadline(text)

def addTasks(text):
    keyValid = False

    tanggal = None
    if len(getDates(text)) > 0:
        tanggal = getDates(text) #masih dalam list inget han
    else: #pasti dari alternate date
        tanggal = getDatesAlternate(text)
        tanggal[0] = convertDateFormat(tanggal[0])

    kode = getKodeMatkul(text)

    key = None
    for key in keywords:
        if textContains(text,[key]):
            keyValid = True
            break

    topik = getTopic(text)

    #----------UPDATE DATABASE----------#
    if keyValid:
        foundEmptyId = False
        idTask = 0
        while not foundEmptyId:
            tasks = Task.query.filter((Task.id_task == idTask)).all()
            if len(tasks) == 0:
                newRecord = Task(id_task = idTask, 
                                tanggal = datetime.datetime.strptime(tanggal[0],"%d/%m/%Y").date(),
                                kode = kode[0],
                                jenis = key,
                                topik = topik)
                db.session.add(newRecord)
                db.session.commit()
                foundEmptyId = True
            else:
                idTask+=1
        reply = '[TASK BERHASIL DICATAT]<br>'
        reply += "(ID: " + str(idTask) + ") " + tanggal[0] + " - " + kode[0] + " - " + key + " - " + topik
        return reply
    else:
        return "ga valid bro #from addTasks"


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
        # date = getDates(text)
        if len(getDates(text)) > 0:
            date = getDates(text) #masih dalam list inget han
        else: #pasti dari alternate date
            date = getDatesAlternate(text)
            date[0] = convertDateFormat(date[0])

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

def removeTask(text):
    idTask = getIdTask(text)
    reply = None

    if len(idTask) != 0:
        tasks = Task.query.filter((Task.id_task == idTask[0])).all()
        if len(tasks) != 0:
            task = tasks[0]
            reply = '[Task dengan ID ' + idTask[0] + ' (' + task.jenis + ' ' + task.kode + ' ' + task.topik + ') ditandai selesai]'
            Task.query.filter((Task.id_task == idTask[0])).delete()
            db.session.commit()
            return reply                
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

# mereturn berapa perubahan yang harus dilakukan untuk dari word1 menjadi word2
def levenshtein(word1, word2):
    word1 = str(word1).lower()
    word2 = str(word2).lower()
    matrix = [[0 for j in range (len(word2)+1)] for i in range (len(word1)+1)]
    for i in range (len(word1)+1):
        matrix[i][0] = i
    for j in range (len(word2)+1):
        matrix[0][j] = j
    
    for i in range(1, len(word1)+1):
        for j in range(1, len(word2)+1):
            if (word1[i-1] == word2[j-1]):
                matrix[i][j] = min(matrix[i-1][j]+1, matrix[i][j-1]+1, matrix[i-1][j-1])
            else: #kalo word[i] != word2[j]
                matrix[i][j] = min(matrix[i-1][j]+1, matrix[i][j-1]+1, matrix[i-1][j-1]+1)

    return matrix[len(word1)][len(word2)]
# -------------------------------------------------------------------------------- #

# kalo foundError = true, terdapat minimal satu kesalahan pada text
# foundError = false, text udah bener atau memang ga valid aja
def recommendWord(listWord):
    i = 0
    foundError = False
    for word in listWord:
        j = 0
        for key in keywords:
            if (len(word)-levenshtein(word,key))/len(word) >= 0.75 and (len(word)-levenshtein(word,key))/len(word) < 1:
                # word = key
                listWord[i] = "<b><i>"+keywords[j]+"</i></b>"
                foundError = True
                break
            j+=1
        j = 0
        for key in helpWords:
            if (len(word)-levenshtein(word,key))/len(word) >= 0.75 and (len(word)-levenshtein(word,key))/len(word) < 1:
                # word = key
                listWord[i] = "<b><i>"+helpWords[j]+"</i></b>"
                foundError = True
                break
            j+=1
        j = 0
        for key in doneWords:
            if (len(word)-levenshtein(word,key))/len(word) >= 0.75 and (len(word)-levenshtein(word,key))/len(word) < 1:
                # word = key
                listWord[i] = "<b><i>"+doneWords[j]+"</i></b>"
                foundError = True
                break
            j+=1
        j = 0
        for key in updateWords:
            if (len(word)-levenshtein(word,key))/len(word) >= 0.75 and (len(word)-levenshtein(word,key))/len(word) < 1:
                # word = key
                listWord[i] = "<b><i>"+updateWords[j]+"</i></b>"
                foundError = True
                break
            j+=1
        i+=1

    reply = "Mungkin maksud kamu:<br>"
    reply += ' '.join([elmt for elmt in listWord])
    return reply, foundError


if __name__ == "__main__":
    app.run(debug=True,threaded=True)