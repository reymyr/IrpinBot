import re

keywords = ["Kuis", "Ujian", "Tucil", "Tubes", "Praktikum"]
months = {'januari': '1', 'februari':'2', 'maret':'3', 'april':'4','mei':'5','juni':'6','juli':'7','agustus':'8', 'september':'9',
            'oktober':'10','november':'11','desember':'12'}

# convert bulan format %d %B %y menjadi %d/%m/%y --> masih dalam bentuk string
def convertDateFormat(text):
    attr = text.split(' ')
    return '/'.join((attr[0],months[attr[1].lower()],attr[2]))

# Mengembalikan tanggal dalam text dengan format dd/mm/yyyy
def getDates(text):
    return re.findall(r"((?:0?[1-9]|[12][\d]|3[01])\/(?:0?[1-9]|1[12])\/(?:\d{4}))", text)

# Mengembalikan tanggal dalam text dengan format dd %B yyyy
def getDatesAlternate(text):
    return re.findall(r"((?:0?[1-9]|[12][\d]|3[01])\s(?:[Jj]anuari|[Ff]ebruari|[Mm]aret|[Aa]pril|[Mm]ei|[Jj]u[nl]i|[Aa]gustus|[Ss]eptember|[Oo]ktober|[Nn]ovember|[Dd]esember)\s(?:\d{4}))", text)

# Mengembalikan topik tugas dalam text
def getTopic(text):
    temporaryTuple = re.findall(r"(\b[A-Za-z]{2}\d{4}\b(.|\b)*\bpada\b)", text) #masih mengandung kode matkul dan kata "pada"
    if (len(temporaryTuple) == 0):
        return getTopic2(text)
    temporaryText = temporaryTuple[0][0].split()
    rm = temporaryText[:-1]
    listToStr = ' '.join([elmt for elmt in rm])
    checkerTopic = listToStr.split(' ')
    if len(checkerTopic) <= 1:
        return getTopic2(text)
    finalSentences = listToStr.split(' ', 1)[1]
    listToStr = ''.join([elmt for elmt in finalSentences])
    return listToStr

def getTopic2(text):
    wordsToStrip = []
    wordsToStrip += getDates(text) + getDatesAlternate(text) + getKodeMatkul(text) + keywords
    t = text
    for word in wordsToStrip:
        t = re.sub(word, "", t, flags=re.IGNORECASE)

    match = re.search(r"topik(nya)?\b", t, re.IGNORECASE)
    if match:
        t = t.split(match.group(), 1)[-1].strip()
        if len(t) != 0:
            return t

    return []

# Mengembalikan kode matkul dalam text dengan format AAYYYY, A adalah huruf dan Y adalah angka
def getKodeMatkul(text):
    kode = re.findall(r"\b[A-Za-z]{2}\d{4}\b", text)
    return [k.upper() for k in kode]
# Mengembalikan no id task dalam text
def getIdTask(text):
    return re.findall(r"\b(\d{1}|\d{2}|\d{3})\b", text)

# Memeriksa apakah kata dalam keywords ada dalam text
# all = True -> semua kata dalam keywords
# all = False -> minimal salah satu kata dalam keywords
def textContains(text, keywords, all=False):
    if all:
        for key in keywords:
            if boyerMoore(text, key) == -1:
                return False
        return True
    else:
        for key in keywords:
            if boyerMoore(text, key) != -1:
                return True
        return False

# Mengembalikan index awal kemunculan pattern atau -1 jika tidak ditemukan
def boyerMoore(text, pattern):
    # Ubah ke lowercase agar tidak case sensitive
    textLower = text.lower()
    patternLower = pattern.lower()

    # Cari index kemunculan terakhir alfabet di pattern
    lastOccurence = getLastOccurence(textLower, patternLower)

    # Hitung panjang teks dan pattern
    lenT = len(textLower)
    lenP = len(patternLower)

    # Panjang pattern lebih besar dari panjang teks (Tidak ditemukan kecocokan)
    if lenP > lenT:
        return -1

    # Set pencarian awal dari indeks paling akhir pattern
    i = lenP - 1
    j = lenP - 1

    # Looping sepanjang teks
    while (i < lenT):
        # Jika karakter pada pattern dan teks sama
        if (textLower[i] == patternLower[j]):
            # Jika kesamaan ditemukan pada indeks pertama
            # Pattern ditemukan pada teks
            if (j == 0):
                return i
            # Jika tidak, periksa karakter selanjutnya
            else:
                i -= 1
                j -= 1
        # Karakter pada pattern dan teks berbeda
        else:
            # Ambil indeks kemunculan terakhir
            lastCharIdx = lastOccurence[textLower[i]]

            # Hitung nilai i baru
            i += lenP
            # Jika indeks kemunculan terakhir lebih kecil dari indeks ketidakcocokan
            if lastCharIdx < j:
                i -= lastCharIdx + 1
            # Jika indeks kemunculan terakhir lebih besar dari indeks ketidakcocokan
            elif lastCharIdx > j:
                i -= j
            # Jika indeks kemunculan = -1, nilai i baru = (i + panjang pattern)
            
            # Ulangi pencarian pada indeks terakhir pattern
            j = lenP - 1
    
    # Tidak ditemukan kecocokan
    return -1

# Mengembalikan dictionary last occurence dari semua karakter di text pada pattern
def getLastOccurence(text, pattern):
    # Set dictionary awal -1 dengan key setiap karakter pada teks
    lastOcc = dict.fromkeys(text, -1)

    # Looping untuk mencari indeks kemunculan terakhir
    for i in range(len(pattern)):
        lastOcc[pattern[i]] = i 

    return lastOcc