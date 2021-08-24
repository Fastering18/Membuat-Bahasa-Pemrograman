# Membuat-Bahasa-Pemrograman ![travisci test](https://api.travis-ci.org/Fastering18/Membuat-Bahasa-Pemrograman.svg?branch=main)  
Buat kreasi bahasa pemrograman sendiri dengan python!  

Sebelum memulai, download terlebih dahulu dibawah ini

**Download Python versi 3.x**    
- [python.org](https://www.python.org/downloads/)  
  
**Download Nuitka 0.6.x** (untuk generate build file dari python)  
- [Nuitka github](https://github.com/Nuitka/Nuitka) 
- Atau bisa juga dengan `pip install nuitka`  
  
<hr>  

# DEFINISI  
## Tokenizer  
Tokenisasi adalah proses mengganti data dengan simbol identifikasi unik yang menyimpan semua informasi penting tentang data tanpa mengorbankan keamanannya.    
Token yang dihasilkan dapat di gunakan untuk mengidentifikasi tipe data, dll.  

## Lexer  
Lexer hanya mengubah string yang tidak berarti menjadi daftar datar hal-hal seperti "literal angka", "literal string", "pengidentifikasi", atau "operator", dan dapat melakukan hal-hal seperti mengenali pengidentifikasi dan menghilangkan spasi.    
Lexer dapat **mengidentifikasi** operator yang akan digunakan, mendeklarasikan variabel, dll.  

## Parser  
Parser mengambil data masukan (sering kali teks) dan membangun struktur data, seringkali semacam AST (Abstract Syntax Tree), pohon sintaks abstrak atau struktur hierarki lainnya, memberikan representasi struktural dari masukan sambil memeriksa sintaks yang benar.  
Parser dapat membuat pohon AST dan mengidentifikasi sintaks sebelum benar-benar di esekusi.  

## Interpreter  
Interpreter adalah program komputer yang secara langsung menjalankan instruksi yang ditulis dalam bahasa pemrograman atau scripting, tanpa mengharuskannya sebelumnya telah dikompilasi ke dalam program bahasa mesin.  
Interpreter dapat menjalankan intruksi tanpa harus menjadi _machine code_, interpreter dapat menghasilkan operasi matematika, _bitwise operator_, dll.  
  
# Menjalankan script  
setelah build file binary (.exe), lakukan command:  
```./gblk.exe [lokasi file]```  

Jalankan dengan Python jika tidak terdapat binary file:  
```python gblk.py [lokasi file]```  

Untuk menjalankan test ([Makefile](http://gnuwin32.sourceforge.net/packages/make.htm)):  
```make test```  


# Basic syntax  
```gblk
tulis("halo dunia") -- output halo dunia ke stdout

jika benar maka
   tulis("benar == true dan salah == false") -- boolean dasar
tutup -- menutup if statement

lokal str = "selamat pagi"
tulis("Panjang string: " + panjang(str))
tulis((str * 3) + "\nuntuk ketiga kalinya")

lokal iterasi = 10
saat iterasi > 1 maka
   tulis(iterasi)
   lokal iterasi = iterasi - 1
tutup


tulis("program selesai")
```   
## Tipe data  
- Angka  -> tipe data number, angka 0-9
- String  -> tipe data string
- Boolean  -> tipe data boolean (benar|salah)  
- Array  -> tipe data array, ["indeks0", 1]
## Built-in fungsi  
- tulis(semua)  -> menulis ke stdout  
- panjang(string|array)  -> menghitung panjang data  
- tunggu(angka?)  -> menghentikan sementara thread selama waktu yang ditentukan (detik)  
- tipe(semua)  -> mendapatkan nama tipe data  
- substring(string, angkaAwal, angkaAkhir?)  -> memangkas string dari start ke akhir  
- masukkan(array, semua)  -> memasukkan isi kedalam array (indeks terakhir)  
- jalankan(lokasi_file)  -> mengesekusi file yang sudah ditentukan  
## Built-in keyword  
- jika `<kondisi>` maka `<ekspr>` tutup  -> ekuivalen dengan if statement  
- saat `<kondisi>` maka `<ekspr>` tutup  -> ekuivalen dengan loop while statement  
- untuk `<nama variabel>` = `<angka awal>` ke `<angka tujuan>` langkah `<koefisien>` maka `<ekspr>` tutup  -> ekuivalen dengan loop for statement  

**Project migrated to node.js, please refer to**  
> https://github.com/Fastering18/node-gblok
