import Utama as interpreter
from pathlib import Path
from datetime import date
import sys

tanggal = date.today().strftime("%B %d, %Y")

print(
f"""
Gblk 0.0.6 (https://github.com/Fastering18/Membuat-Bahasa-Pemrograman, {tanggal}) di {sys.platform}
"""
)
if len(sys.argv) > 1:
    namafile = sys.argv[1]
    filetujuan = Path(namafile)
    if filetujuan.is_file():
        try:
            isifile = open(namafile, encoding="utf8").read()
            hasil, error = interpreter.esekusi(namafile, isifile)

            if error: 
                print(error.jadiString())
                sys.exit(1)
            elif hasil: 
                if len(hasil.isi) == 1:
                    print(repr(hasil.isi[0]))
                else:
                    print(repr(hasil))
        except UnicodeDecodeError:
            print("Enkoding file harus berupa valid UTF-8")
    else:
        print("file tidak ditemukan")

sys.exit(0)

# python gblk.py