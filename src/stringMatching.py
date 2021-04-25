import re

# Mengembalikan tanggal dalam text dengan format dd/mm/yyyy
def getDates(text):
    return re.findall(r"((?:0?[1-9]|[12][\d]|3[01])\/(?:0?[1-9]|1[12])\/(?:\d{4}))", text)

# Mengembalikan kode matkul dalam text dengan format AAYYYY, A adalah huruf kapital dan Y adalah angka
def getKodeMatkul(text):
    return re.findall(r"\b[A-Z]{2}\d{4}\b", text)

# Mengembalikan no id task dalam text
def getIdTask(text):
    return re.findall(r"\b(\d{1}|\d{2}|\d{3})\b", text)

# Memeriksa apakah kata dalam keywords ada dalam text
# all = True -> semua kata dalam keywords
# all = False -> salah satu kata dalam keywords
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