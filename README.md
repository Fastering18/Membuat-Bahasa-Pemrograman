# Membuat-Bahasa-Pemrograman
Buat kreasi bahasa pemrograman sendiri dengan python!  

Sebelum memulai, download terlebih dahulu dibawah ini

- **Download Python versi 3.x**    
- [python.org](https://www.python.org/downloads/)  
  
- **Download Nuitka 0.6.x** (untuk generate build file dari python)  
- [Nuitka github](https://github.com/Nuitka/Nuitka) 
- Atau bisa juga dengan `pip install nuitka`  
<br>
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

