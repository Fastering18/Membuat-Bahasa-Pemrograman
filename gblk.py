import Utama as interpreter
from pathlib import Path
import sys

def jalankan(namafile):
    try:
        isifile = open(namafile, encoding="utf8").read()
        hasil, error = interpreter.esekusi(namafile, isifile)

        if error: 
            print(error.jadiString())
            sys.exit(1)
    except UnicodeDecodeError:
        print("Enkoding file harus berupa valid UTF-8")

if len(sys.argv) > 1:
    namafile = sys.argv[1]
    if Path(namafile).is_file():
        jalankan(namafile)
    elif Path(namafile + ".gblk").is_file():
        jalankan(namafile + ".gblk")
    else:
        print("file tidak ditemukan")

# jika berjalan tanpa error
sys.exit(0)

# python gblk.py <namafile> 
