from util.panaherror import *
from pathlib import Path
import string, time

# Utama
Digit = "0123456789"
Huruf = string.ascii_letters
Huruf_Digit = Huruf + Digit

# ERROR
class Error:
	def __init__(self, posisi_awal, posisi_akhir, nama, detail):
		self.posisi_awal = posisi_awal
		self.posisi_akhir = posisi_akhir
		self.nama_error = nama
		self.details = detail

	def jadiString(self):
		string_error = f"{self.nama_error}: {self.details}"
		string_error += (
			f"\nFile {self.posisi_awal.namafile}, baris {self.posisi_awal.baris + 1}"
		)
		string_error += "\n\n" + panaherror(
			self.posisi_awal.fileteks, self.posisi_awal, self.posisi_akhir
		)
		return string_error


class KarakterSalah(Error):
	def __init__(self, posisi_awal, posisi_akhir, detail):
		super().__init__(posisi_awal, posisi_akhir, "Kesalahan Karakter", detail)


class KarakterYangDibutuhkan(Error):
	def __init__(self, posisi_awal, posisi_akhir, detail):
		super().__init__(posisi_awal, posisi_akhir, "Dibutuhkan Karakter", detail)


class SintaksSalah(Error):
	def __init__(self, posisi_awal, posisi_akhir, detail=""):
		super().__init__(posisi_awal, posisi_akhir, "Kesalahan Syntax", detail)


class RTError(Error):
	def __init__(self, posisi_awal, posisi_akhir, detail, konteks):
		super().__init__(posisi_awal, posisi_akhir, "Runtime Error", detail)
		self.konteks = konteks

	def jadiString(self):
		hasil_error = self.buat_traceback()
		hasil_error += f"{self.nama_error}: {self.details}"
		hasil_error += "\n\n" + panaherror(
			self.posisi_awal.fileteks, self.posisi_awal, self.posisi_akhir
		)
		return hasil_error

	def buat_traceback(self):
		hasil = ""
		# pos = self.posisi_awal
		konteks = self.konteks

		while konteks:
			hasil = (
				f"  File {self.posisi_awal.namafile}, baris {str(self.posisi_awal.baris + 1)}, di {konteks.display_nama}\n"
				+ hasil
			)
			pos = konteks.posisi_urutan_induk
			konteks = konteks.induk

		return "Traceback (panggilan terakhir):\n" + hasil


# POSISI
class Posisi:
	def __init__(self, indeks, baris, kolom, namafile, fileteks):
		self.indeks = indeks
		self.baris = baris
		self.kolom = kolom
		self.namafile = namafile
		self.fileteks = fileteks

	def maju(self, karakterSkrg=None):
		self.indeks += 1
		self.kolom += 1

		if karakterSkrg == "\n":
			self.baris += 1
			self.kolom = 0

		return self

	def salin(self):
		return Posisi(self.indeks, self.baris, self.kolom, self.namafile, self.fileteks)


# TOKEN
TokenInteger = "INT"
TokenFloat = "FLOAT"
TokenString = "STRING"
TokenIdentifier = "IDENTIFIER"
TokenKeyword = "KEYWORD"
TokenTambah = "TAMBAH"
TokenKurang = "KURANG"
TokenKali = "KALI"
TokenBagi = "BAGI"
TokenPangkat = "PANGKAT"
TokenModulo = "MODULUS"
TokenParentesisKiri = "PKiri"
TokenParentesisKanan = "PKanan"
TokenKotakKiri = "KKiri"
TokenKotakKanan = "KKanan"
TokenSama = "EQ"
TokenSamaSama = "SAMASAMA"
TokenTidakSama = "GKSAMA"
TokenKurangDari = "KURANGDARI"
TokenLebihDari = "LEBIHDARI"
TokenKurangAtauSama = "SAMAKURANG"
TokenLebihAtauSama = "LEBIHKURANG"
TokenKoma = "KOMA"
TokenPanah = "PANAH"
TokenLineBaru = "NEWLINE"
TokenEOF = "EOF"

Konstruktor = [
	"lokal",      # lokal anjay = "anjay"
	"dan",        # <kondisi1> dan <kondisi2>
	"atau",       # <kondisi1> atau <kondisi2>
	"bukan",      # not true == false
	"jika",       # jika [kondisi] maka
	"maka",       # then [expr]
	"jikatidak",  # else [expr]
	"kalau",      # elseif [kondisi] [expr]
	"untuk",      # untuk i = 0 ke 5
	"ke",         # untuk indeks = 0 ke 10
	"langkah",    # untuk indeks = 8 ke -5 langkah -1
	"fungsi",     # function
	"saat",       # while
	"tutup",      # end (menutup blok statement)
	"kembali",      # return
	"lanjutkan",  # continue
	"berhenti"    # break
]


class Token:
	def __init__(self, tipe_, value=None, posisi_awal=None, posisi_akhir=None):
		self.tipe = tipe_
		self.value = value

		if posisi_awal:
			self.posisi_awal = posisi_awal.salin()
			self.posisi_akhir = posisi_awal.salin()
			self.posisi_akhir.maju()
		if posisi_akhir:
			self.posisi_akhir = posisi_akhir.salin()

	def sama_dengan(self, tipe_, value):
		return self.tipe == tipe_ and self.value == value

	def __repr__(self):
		if self.value:
			return f"{self.tipe}:{self.value}"
		return f"{self.tipe}"


# Lexer


class Lexer:
	def __init__(self, nama_file, teks):
		self.teks = teks
		self.posisi = Posisi(-1, 0, -1, nama_file, teks)
		self.namafile = nama_file
		self.karakterSkrg = None
		self.maju()

	def maju(self):
		self.posisi.maju(self.karakterSkrg)
		self.karakterSkrg = (
			self.teks[self.posisi.indeks]
			if self.posisi.indeks < len(self.teks)
			else None
		)

	def buatToken(self):
		tokens = []

		while self.karakterSkrg != None:
			if self.karakterSkrg in " \t":
				self.maju()
			elif self.karakterSkrg in ";\n":
				tokens.append(Token(TokenLineBaru, posisi_awal=self.posisi))
				self.maju()
			elif self.karakterSkrg in Digit:
				tokens.append(self._buatAngka())
			elif self.karakterSkrg in Huruf:
				tokens.append(self._daftarlokal())
			elif self.karakterSkrg == '"':
				tokens.append(self._buatString())
			elif self.karakterSkrg == "+":
				tokens.append(Token(TokenTambah, posisi_awal=self.posisi))
				self.maju()
			elif self.karakterSkrg == "-":
				tokenMungkin = self.buat_minus_atau_panah_atau_komentar()
				if isinstance(tokenMungkin, Token): tokens.append(tokenMungkin)
			elif self.karakterSkrg == "*":
				tokens.append(Token(TokenKali, posisi_awal=self.posisi))
				self.maju()
			elif self.karakterSkrg == "/":
				tokens.append(Token(TokenBagi, posisi_awal=self.posisi))
				self.maju()
			elif self.karakterSkrg == "^":
				tokens.append(Token(TokenPangkat, posisi_awal=self.posisi))
				self.maju()
			elif self.karakterSkrg == "%":
				tokens.append(Token(TokenModulo, posisi_awal=self.posisi))
				self.maju()
			elif self.karakterSkrg == "(":
				tokens.append(Token(TokenParentesisKiri, posisi_awal=self.posisi))
				self.maju()
			elif self.karakterSkrg == ")":
				tokens.append(Token(TokenParentesisKanan, posisi_awal=self.posisi))
				self.maju()
			elif self.karakterSkrg == "[":
				tokens.append(Token(TokenKotakKiri, posisi_awal=self.posisi))
				self.maju()
			elif self.karakterSkrg == "]":
				tokens.append(Token(TokenKotakKanan, posisi_awal=self.posisi))
				self.maju()
			elif self.karakterSkrg == "!":
				token, error = self.buat_tidak_sama()
				if error:
					return [], error
				tokens.append(token)
			elif self.karakterSkrg == "=":
				tokens.append(self.buat_kesamaan())
			elif self.karakterSkrg == ">":
				tokens.append(self.buat_lebih_dari())
			elif self.karakterSkrg == "<":
				tokens.append(self.buat_kurang_dari())
			elif self.karakterSkrg == ",":
				tokens.append(Token(TokenKoma, posisi_awal=self.posisi))
				self.maju()
			else:
				posisi_awal = self.posisi.salin()
				karakter = self.karakterSkrg
				self.maju()
				return [], KarakterSalah(posisi_awal, self.posisi, '"' + karakter + '"')

		tokens.append(Token(TokenEOF, posisi_awal=self.posisi))
		return tokens, None

	def _buatAngka(self):
		angkaString = ""
		jumlah_titik = 0
		ada_e = False
		posisi_awal = self.posisi.salin()

		while self.karakterSkrg != None and self.karakterSkrg in Digit + "." + "e":
			if self.karakterSkrg == "e":
				if ada_e == True:
					break
				ada_e = True
				angkaString += "e"
			elif self.karakterSkrg == ".":
				if jumlah_titik == 1:
					break
				jumlah_titik += 1
				angkaString += "."
			else:
				angkaString += self.karakterSkrg
			self.maju()

		if jumlah_titik == 0 and ada_e == False:
			return Token(TokenInteger, int(angkaString), posisi_awal, self.posisi)
		else:
			return Token(TokenFloat, float(angkaString), posisi_awal, self.posisi)

	def _buatString(self):
		string = ""
		posisi_awal = self.posisi.salin()
		escape_karakter = False
		self.maju()

		daftar_escape_karakter = {"n": "\n", "t": "\t"}

		while self.karakterSkrg != None and (
			self.karakterSkrg != '"' or escape_karakter
		):
			if escape_karakter:
				string += daftar_escape_karakter.get(
					self.karakterSkrg, self.karakterSkrg
				)
			else:
				if self.karakterSkrg == "\\":
					escape_karakter = True
				else:
					string += self.karakterSkrg
			self.maju()
			eescape_karakter = False

		self.maju()
		return Token(TokenString, string, posisi_awal, self.posisi)

	def _daftarlokal(self):
		identitas_string = ""
		posisi_awal = self.posisi.salin()

		while self.karakterSkrg != None and self.karakterSkrg in Huruf_Digit + "_":
			identitas_string += self.karakterSkrg
			self.maju()

		tipe_token = (
			TokenKeyword if identitas_string in Konstruktor else TokenIdentifier
		)
		return Token(tipe_token, identitas_string, posisi_awal, self.posisi)

	def buat_minus_atau_panah_atau_komentar(self):
		tipe_token = TokenKurang
		posisi_awal = self.posisi.salin()
		self.maju()

		if self.karakterSkrg == ">":
			self.maju()
			tipe_token = TokenPanah
		elif self.karakterSkrg == "-":
			self.skip_komentar()
			return

		return Token(tipe_token, posisi_awal=posisi_awal, posisi_akhir=self.posisi)

	def buat_tidak_sama(self):
		posisi_awal = self.posisi.salin()
		self.maju()

		if self.karakterSkrg == "=":
			self.maju()
			return (
				Token(
					TokenTidakSama, posisi_awal=posisi_awal, posisi_akhir=self.posisi
				),
				None,
			)

		self.maju()
		return None, KarakterYangDibutuhkan(
			posisi_awal, self.posisi, "'=' (setelah '!')"
		)

	def buat_kesamaan(self):
		tipe_token = TokenSama
		posisi_awal = self.posisi.salin()
		self.maju()

		if self.karakterSkrg == "=":
			self.maju()
			tipe_token = TokenSamaSama

		return Token(tipe_token, posisi_awal=posisi_awal, posisi_akhir=self.posisi)

	def buat_kurang_dari(self):
		tipe_token = TokenKurangDari
		posisi_awal = self.posisi.salin()
		self.maju()

		if self.karakterSkrg == "=":
			self.maju()
			tipe_token = TokenKurangAtauSama

		return Token(tipe_token, posisi_awal=posisi_awal, posisi_akhir=self.posisi)

	def buat_lebih_dari(self):
		tipe_token = TokenLebihDari
		posisi_awal = self.posisi.salin()
		self.maju()

		if self.karakterSkrg == "=":
			self.maju()
			tipe_token = TokenLebihAtauSama

		return Token(tipe_token, posisi_awal=posisi_awal, posisi_akhir=self.posisi)

	def skip_komentar(self):
		komen_blok = False
		posisi_awal = self.posisi.salin()
		self.maju()

		if self.karakterSkrg == "[":
			komen_blok = True
			self.maju()
			if self.karakterSkrg == "[":
				while self.karakterSkrg != ']' and self.karakterSkrg != None:
					self.maju()
				self.maju()
				if self.karakterSkrg != "]":
					return None, KarakterYangDibutuhkan(
						posisi_awal, self.posisi, "Dibutuhkan ']'"
					)
		else:
			while self.karakterSkrg != '\n' and self.karakterSkrg != None:
				self.maju()

		self.maju()

# NODES


class NodeAngka:
	def __init__(self, token):
		self.token = token
		self.posisi_awal = self.token.posisi_awal
		self.posisi_akhir = self.token.posisi_akhir

	def __repr__(self):
		return f"{self.token}"


class NodeString:
	def __init__(self, token):
		self.token = token
		self.posisi_awal = self.token.posisi_awal
		self.posisi_akhir = self.token.posisi_akhir

	def __repr__(self):
		return f"{self.token}"


class NodeOperasiBinary:
	def __init__(self, node_kiri, operator_token, node_kanan):
		self.node_kiri = node_kiri
		self.operator_token = operator_token
		self.node_kanan = node_kanan

		self.posisi_awal = self.node_kiri.posisi_awal
		self.posisi_akhir = self.node_kanan.posisi_akhir

	def __repr__(self):
		return f"({self.node_kiri}, {self.operator_token}, {self.node_kanan})"


class NodeOperatorMinus:  # Unary operator
	def __init__(self, operator_token, node):
		self.operator_token = operator_token
		self.node = node

		self.posisi_awal = self.operator_token.posisi_awal
		self.posisi_akhir = node.posisi_akhir

	def __repr__(self):
		return f"({self.operator_token}, {self.node})"


class DaftarNode:
	def __init__(self, isi_daftar, posisi_awal, posisi_akhir):
		self.isi_daftar = isi_daftar

		self.posisi_awal = posisi_awal
		self.posisi_akhir = posisi_akhir


class NodeAkseslokal:
	def __init__(self, namalokal_token):
		self.nama_token_lokal = namalokal_token

		self.posisi_awal = self.nama_token_lokal.posisi_awal
		self.posisi_akhir = self.nama_token_lokal.posisi_akhir


class NodeBuatlokal:
	def __init__(self, namalokal_token, isi_node):
		self.nama_token_lokal = namalokal_token
		self.isi_node = isi_node

		self.posisi_awal = self.nama_token_lokal.posisi_awal
		self.posisi_akhir = self.nama_token_lokal.posisi_akhir


class NodeIF:
	def __init__(self, cases, else_case):
		self.cases = cases
		self.else_case = else_case

		self.posisi_awal = self.cases[0][0].posisi_awal
		self.posisi_akhir = (
			self.else_case or self.cases[len(self.cases) - 1]
		)[0].posisi_akhir


class NodeFor:
	def __init__(
		self,
		namalokal_token,
		node_mulai_nilai,
		node_akhir_nilai,
		node_step_nilai,
		isi_node, 
		harus_return_null
	):
		self.namalokal_token = namalokal_token
		self.node_mulai_nilai = node_mulai_nilai
		self.node_akhir_nilai = node_akhir_nilai
		self.node_step_nilai = node_step_nilai
		self.isi_node = isi_node
		self.harus_return_null = harus_return_null

		self.posisi_awal = self.namalokal_token.posisi_awal
		self.posisi_akhir = self.isi_node.posisi_akhir


class NodeWhile:
	def __init__(self, kondisi, isi_node, harus_return_null):
		self.kondisi = kondisi
		self.isi_node = isi_node
		self.harus_return_null = harus_return_null

		self.posisi_awal = self.kondisi.posisi_awal
		self.posisi_akhir = self.isi_node.posisi_akhir

#lokal b = 0; saat b < 15 maka tulis(b); lokal b = b + 1 tutup
class NodeBuatFungsi:
	def __init__(self, namalokal_token, nama_parameter_token, isi_node, harus_return_null):
		self.namalokal_token = namalokal_token
		self.nama_parameter_token = nama_parameter_token
		self.isi_node = isi_node
		self.harus_return_null = harus_return_null

		if self.namalokal_token:
			self.posisi_awal = self.namalokal_token.posisi_awal
		elif len(self.nama_parameter_token) > 0:
			self.posisi_awal = self.nama_parameter_token[0].posisi_awal
		else:
			self.posisi_awal = self.isi_node.posisi_awal

		self.posisi_akhir = self.isi_node.posisi_akhir


class NodePanggil:
	def __init__(self, node_untuk_panggil, node_parameter):
		self.node_untuk_panggil = node_untuk_panggil
		self.node_parameter = node_parameter

		self.posisi_awal = self.node_untuk_panggil.posisi_awal

		if len(self.node_parameter) > 0:
			self.posisi_akhir = self.node_parameter[
				len(self.node_parameter) - 1
			].posisi_akhir
		else:
			self.posisi_akhir = self.node_untuk_panggil.posisi_akhir

class NodeReturn:
	def __init__(self, node_to_return, poisi_awal, poisi_akhir):
		self.node_untuk_return = node_to_return

		self.posisi_awal = poisi_awal
		self.posisi_akhir = poisi_akhir

class NodeLanjutkan:
	def __init__(self, poisi_awal, poisi_akhir):
		self.posisi_awal = poisi_awal
		self.posisi_akhir = poisi_akhir

class NodeBreak:
	def __init__(self, poisi_awal, poisi_akhir):
		self.posisi_awal = poisi_awal
		self.posisi_akhir = poisi_akhir

# HASIL PARSE
class HasilParse:
	def __init__(self):
		self.error = None
		self.node = None
		self.jumlah_kemajuan_terdaftar = 0
		self.jumlah_maju = 0
		self.perhitungan_balik = 0

	def daftar_kemajuan(self):
		self.jumlah_kemajuan_terdaftar = 1
		self.jumlah_maju += 1

	def daftar(self, hasil):
		self.jumlah_kemajuan_terdaftar = hasil.jumlah_maju
		self.jumlah_maju += hasil.jumlah_maju
		if hasil.error:
			self.error = hasil.error
		return hasil.node
	
	def coba_daftar(self, hasil):
		if hasil.error:
			self.perhitungan_balik = hasil.jumlah_maju
			return None
		return self.daftar(hasil)

	def berhasil(self, node):
		self.node = node
		return self

	def gagal(self, error):
		if not self.error or self.jumlah_kemajuan_terdaftar == 0:
			self.error = error
		return self


# PARSER
class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.token_indeks = -1
		self.maju()

	def maju(
		self,
	):
		self.token_indeks += 1
		self.perbarui_tokenSkrg()
		return self.tokenSkrg
	
	def balik(self, jumlah=1):
		self.token_indeks -= jumlah
		self.perbarui_tokenSkrg()
		return self.tokenSkrg

	def perbarui_tokenSkrg(self):
		if self.token_indeks >= 0 and self.token_indeks < len(self.tokens):
			self.tokenSkrg = self.tokens[self.token_indeks]

	def parse(self):
		res = self.statements()
		if not res.error and self.tokenSkrg.tipe != TokenEOF:
			return res.gagal(
				SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					"Harus berupa sintaks '+', '-', '*', '/', '^', '%'",
				)
			)
		return res

	def daftar_expr(self):
		res = HasilParse()
		isi_elemen = []
		posisi_awal = self.tokenSkrg.posisi_awal.salin()

		if self.tokenSkrg.tipe != TokenKotakKiri:
			return res.gagal(
				SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					f"Dibutuhkan '['",
				)
			)

		res.daftar_kemajuan()
		self.maju()

		if self.tokenSkrg.tipe == TokenKotakKanan:
			res.daftar_kemajuan()
			self.maju()
		else:
			isi_elemen.append(res.daftar(self.expr()))
			if res.error:
				return res.gagal(
					SintaksSalah(
						self.tokenSkrg.posisi_awal,
						self.tokenSkrg.posisi_akhir,
						"Dibutuhkan ')', 'lokal', 'jika', 'untuk', 'saat', 'fungsi', int, float, pengenal lokal, '+', '-', '(' atau 'bukan'",
					)
				)

			while self.tokenSkrg.tipe == TokenKoma:
				res.daftar_kemajuan()
				self.maju()

				isi_elemen.append(res.daftar(self.expr()))
				if res.error:
					return res

			if self.tokenSkrg.tipe != TokenKotakKanan:
				return res.gagal(
					SintaksSalah(
						self.tokenSkrg.posisi_awal,
						self.tokenSkrg.posisi_akhir,
						"Dibutuhkan ',' atau ']'",
					)
				)

			res.daftar_kemajuan()
			self.maju()

		return res.berhasil(
			DaftarNode(isi_elemen, posisi_awal, self.tokenSkrg.posisi_akhir.salin())
		)

	def if_expr(self):
		res = HasilParse()
		all_cases = res.daftar(self.if_expr_cases('jika'))
		if res.error: return res
		cases, else_case = all_cases
		return res.berhasil(NodeIF(cases, else_case))

	def if_expr_elseif(self):
		return self.if_expr_cases('kalau')
	
	def if_expr_c(self):
		res = HasilParse()
		else_case = None

		if self.tokenSkrg.sama_dengan(TokenKeyword, 'jikatidak'):
			res.daftar_kemajuan()
			self.maju()

			if self.tokenSkrg.tipe == TokenLineBaru:
				res.daftar_kemajuan()
				self.maju()

				statements = res.daftar(self.statements())
				if res.error: return res
				else_case = (statements, True)

				if self.tokenSkrg.sama_dengan(TokenKeyword, 'tutup'):
					res.daftar_kemajuan()
					self.maju()
				else:
					return res.gagal(SintaksSalah(
					self.tokenSkrg.posisi_awal, self.tokenSkrg.posisi_akhir,
						"Expected 'tutup'"
					))
			else:
				expr = res.daftar(self.statement())
				if res.error: return res
				else_case = (expr, False)

		return res.berhasil(else_case)

	def if_else_atau_elseif(self):
		res = HasilParse()
		cases, else_case = [], None

		if self.tokenSkrg.sama_dengan(TokenKeyword, 'kalau'):
			all_cases = res.daftar(self.if_expr_elseif())
			if res.error: return res
			cases, else_case = all_cases
		else:
			else_case = res.daftar(self.if_expr_c())
			if res.error: return res
	
		return res.berhasil((cases, else_case))

	def if_expr_cases(self, case_keyword):
		res = HasilParse()
		cases = []
		else_case = None

		if not self.tokenSkrg.sama_dengan(TokenKeyword, case_keyword):
			return res.gagal(SintaksSalah(
				self.tokenSkrg.posisi_awal, self.tokenSkrg.posisi_akhir,
				f"Dibutuhkan '{case_keyword}'"
			))

		res.daftar_kemajuan()
		self.maju()

		condition = res.daftar(self.expr())
		if res.error: return res

		if not self.tokenSkrg.sama_dengan(TokenKeyword, 'maka'):
			return res.gagal(SintaksSalah(
				self.tokenSkrg.posisi_awal, self.tokenSkrg.posisi_akhir,
				f"Expected 'maka'"
			))

		res.daftar_kemajuan()
		self.maju()
		if self.tokenSkrg.tipe == TokenLineBaru:
			res.daftar_kemajuan()
			self.maju()

			statements = res.daftar(self.statements())
			if res.error: return res
			cases.append((condition, statements, True))

			if self.tokenSkrg.sama_dengan(TokenKeyword, 'tutup'):
				res.daftar_kemajuan()
				self.maju()
			else:
				all_cases = res.daftar(self.if_else_atau_elseif())
				if res.error: return res
				new_cases, else_case = all_cases
				cases.extend(new_cases)
		else:
			expr = res.daftar(self.statement())
			if res.error: return res
			cases.append((condition, expr, False))

			all_cases = res.daftar(self.if_else_atau_elseif())
			if res.error: return res
			new_cases, else_case = all_cases
			cases.extend(new_cases)

			if self.tokenSkrg.tipe == TokenLineBaru:
				res.daftar_kemajuan()
				self.maju()

			if not self.tokenSkrg.sama_dengan(TokenKeyword, 'tutup'):
				return res.gagal(SintaksSalah(
					self.tokenSkrg.posisi_awal, self.tokenSkrg.posisi_akhir,
					f"Dibutuhkan 'tutup'"
				))

			res.daftar_kemajuan()
			self.maju()

		return res.berhasil((cases, else_case))

	def for_expr(self):
		res = HasilParse()

		if not self.tokenSkrg.sama_dengan(TokenKeyword, "untuk"):  # for
			return res.gagal(
				SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					f"Dibutuhkan 'untuk'",
				)
			)

		res.daftar_kemajuan()
		self.maju()

		if self.tokenSkrg.tipe != TokenIdentifier:
			return res.gagal(
				SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					f"Dibutuhkan lokal pengenal",
				)
			)

		nama_lokal = self.tokenSkrg
		res.daftar_kemajuan()
		self.maju()

		if self.tokenSkrg.tipe != TokenSama:
			return res.gagal(
				SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					f"Dibutuhkan '='",
				)
			)

		res.daftar_kemajuan()
		self.maju()

		isi_awal = res.daftar(self.expr())
		if res.error:
			return res

		if not self.tokenSkrg.sama_dengan(TokenKeyword, "ke"):  # for ... to
			return res.gagal(
				SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					f"Dibutuhkan 'ke'",
				)
			)

		res.daftar_kemajuan()
		self.maju()

		isi_akhir = res.daftar(self.expr())
		if res.error:
			return res

		if self.tokenSkrg.sama_dengan(
			TokenKeyword, "langkah"
		):  # for ... to ... langkah
			res.daftar_kemajuan()
			self.maju()

			isi_step = res.daftar(self.expr())
			if res.error:
				return res
		else:
			isi_step = None

		if not self.tokenSkrg.sama_dengan(
			TokenKeyword, "maka"
		):  # untuk ... ke ... langkah ... maka
			return res.gagal(
				SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					f"Dibutuhkan 'maka'",
				)
			)

		res.daftar_kemajuan()
		self.maju()

		if self.tokenSkrg.tipe == TokenLineBaru:
			res.daftar_kemajuan()
			self.maju()

			isi = res.daftar(self.statements())
			if res.error:
				return res

			if not self.tokenSkrg.sama_dengan(TokenKeyword, 'tutup'):
				return res.gagal(SintaksSalah(
					self.tokenSkrg.posisi_awal, self.tokenSkrg.posisi_akhir,
						"Dibutuhkan 'tutup'"
					))
			
			res.daftar_kemajuan()
			self.maju()

			return res.berhasil(NodeFor(nama_lokal, isi_awal, isi_akhir, isi_step, isi, True))
		
		isi = res.daftar(self.statement())
		if res.error: return res

		return res.berhasil(NodeFor(nama_lokal, isi_awal, isi_akhir, isi_step, isi, False))

	def while_expr(self):
		res = HasilParse()

		if not self.tokenSkrg.sama_dengan(TokenKeyword, "saat"):  # while
			return res.gagal(
				SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					f"Dibutuhkan 'saat'",
				)
			)

		res.daftar_kemajuan()
		self.maju()

		kondisi = res.daftar(self.expr())
		if res.error:
			return res

		if not self.tokenSkrg.sama_dengan(TokenKeyword, "maka"):  # while ... do
			return res.gagal(
				SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					f"Dibutuhkan 'maka'",
				)
			)

		res.daftar_kemajuan()
		self.maju()

		if self.tokenSkrg.tipe == TokenLineBaru:
			res.daftar_kemajuan()
			self.maju()

			isi = res.daftar(self.statements())
			if res.error:
				return res

			if not self.tokenSkrg.sama_dengan(TokenKeyword, 'tutup'):
				return res.gagal(SintaksSalah(
					self.tokenSkrg.posisi_awal, self.tokenSkrg.posisi_akhir,
						"Dibutuhkan 'tutup'"
					))
			
			res.daftar_kemajuan()
			self.maju()

			return res.berhasil(NodeWhile(kondisi, isi, True))

		isi = res.daftar(self.statement())
		if res.error: return res

		return res.berhasil(NodeWhile(kondisi, isi, False))

	def atom(self):
		res = HasilParse()
		tokenskrg = self.tokenSkrg#saat ae < 10 maka lokal ae = ae + 1 tulis(ae);

		if tokenskrg.tipe in (TokenInteger, TokenFloat):
			res.daftar_kemajuan()
			self.maju()
			return res.berhasil(NodeAngka(tokenskrg))

		elif tokenskrg.tipe == TokenString:
			res.daftar_kemajuan()
			self.maju()
			return res.berhasil(NodeString(tokenskrg))

		elif tokenskrg.tipe == TokenIdentifier:
			res.daftar_kemajuan()
			self.maju()
			return res.berhasil(NodeAkseslokal(tokenskrg))

		elif tokenskrg.tipe == TokenParentesisKiri:
			res.daftar_kemajuan()
			self.maju()
			expr = res.daftar(self.expr())
			if res.error:
				return res
			if self.tokenSkrg.tipe == TokenParentesisKanan:
				res.daftar_kemajuan()
				self.maju()
				return res.berhasil(expr)
			else:
				return res.gagal(
					SintaksSalah(
						self.tokenSkrg.posisi_awal,
						self.tokenSkrg.posisi_akhir,
						"Dibutuhkan ')'",
					)
				)
		elif tokenskrg.tipe == TokenKotakKiri:
			daftar_expr = res.daftar(self.daftar_expr())
			if res.error:
				return res
			return res.berhasil(daftar_expr)

		elif tokenskrg.sama_dengan(TokenKeyword, "jika"):
			if_expr = res.daftar(self.if_expr())
			if res.error:
				return res
			return res.berhasil(if_expr)

		elif tokenskrg.sama_dengan(TokenKeyword, "untuk"):
			for_expr = res.daftar(self.for_expr())
			if res.error:
				return res
			return res.berhasil(for_expr)

		elif tokenskrg.sama_dengan(TokenKeyword, "saat"):
			while_expr = res.daftar(self.while_expr())
			if res.error:
				return res
			return res.berhasil(while_expr)

		elif tokenskrg.sama_dengan(TokenKeyword, "fungsi"):
			fungsi = res.daftar(self.buat_fungsi())
			if res.error:
				return res
			return res.berhasil(fungsi)

		return res.gagal(
			SintaksSalah(
				tokenskrg.posisi_awal,
				tokenskrg.posisi_akhir,
				"Harus memiliki int, float, lokal, '+', '-' atau parentesis",
			)
		)

	def power(self):
		return self.binary_operator(self.panggil, (TokenPangkat,), self.faktor)

	def panggil(self):
		res = HasilParse()
		atom = res.daftar(self.atom())
		if res.error:
			return res

		if self.tokenSkrg.tipe == TokenParentesisKiri:
			res.daftar_kemajuan()
			self.maju()
			node_parameter = []

			if self.tokenSkrg.tipe == TokenParentesisKanan:
				res.daftar_kemajuan()
				self.maju()
			else:
				node_parameter.append(res.daftar(self.expr()))
				if res.error:
					return res.gagal(
						SintaksSalah(
							self.tokenSkrg.posisi_awal,
							self.tokenSkrg.posisi_akhir,
							"Dibutuhkan ')', 'lokal', 'jika', 'untuk', 'saat', 'fungsi', int, float, pengenal lokal, '+', '-', '(' atau 'bukan'",
						)
					)

				while self.tokenSkrg.tipe == TokenKoma:
					res.daftar_kemajuan()
					self.maju()

					node_parameter.append(res.daftar(self.expr()))
					if res.error:
						return res

				if self.tokenSkrg.tipe != TokenParentesisKanan:
					return res.gagal(
						SintaksSalah(
							self.tokenSkrg.posisi_awal,
							self.tokenSkrg.posisi_akhir,
							"Dibutuhkan ',' atau ')'",
						)
					)

				res.daftar_kemajuan()
				self.maju()
			return res.berhasil(NodePanggil(atom, node_parameter))
		return res.berhasil(atom)

	def faktor(self):
		res = HasilParse()
		tokenskrg = self.tokenSkrg

		if tokenskrg.tipe in (TokenTambah, TokenKurang):
			res.daftar_kemajuan()
			self.maju()
			faktor = res.daftar(self.faktor())
			if res.error:
				return res
			return res.berhasil(NodeOperatorMinus(tokenskrg, faktor))

		return self.power()

	def term(self):
		return self.binary_operator(self.faktor, (TokenKali, TokenBagi, TokenModulo))

	def arith_expr(self):
		return self.binary_operator(self.term, (TokenTambah, TokenKurang))

	def perbandingan_expr(self):
		res = HasilParse()

		if self.tokenSkrg.sama_dengan(TokenKeyword, "bukan"):
			operator_token = self.tokenSkrg
			res.daftar_kemajuan()
			self.maju()

			node = res.daftar(self.perbandingan_expr())
			if res.error:
				return res
			return res.berhasil(NodeOperatorMinus(operator_token, node))

		node = res.daftar(
			self.binary_operator(
				self.arith_expr,
				(
					TokenSamaSama,
					TokenTidakSama,
					TokenKurangDari,
					TokenLebihDari,
					TokenKurangAtauSama,
					TokenLebihAtauSama,
				),
			)
		)

		if res.error:
			return res.gagal(
				res.error
				or SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					"Harus memiliki int, float, lokal, '+', '-', 'bukan', atau parentesis",
				)
			)

		return res.berhasil(node)
	
	def statements(self):
		res = HasilParse()
		statements = []
		posisi_awal = self.tokenSkrg.posisi_awal.salin()

		while self.tokenSkrg.tipe == TokenLineBaru:
			res.daftar_kemajuan()
			self.maju()

		statement = res.daftar(self.statement())
		if res.error:
			return res
		statements.append(statement)

		statements_lebih = True

		while True:
			jumlah_newline = 0
			while self.tokenSkrg.tipe == TokenLineBaru:
				res.daftar_kemajuan()
				self.maju()
				jumlah_newline += 1
			if jumlah_newline == 0:
				statements_lebih = False	

			if not statements_lebih: break
			statement = res.coba_daftar(self.statement())
			if not statement:
				self.balik(res.perhitungan_balik)
				statements_lebih = False
				continue
			statements.append(statement)
		return res.berhasil(DaftarNode(
			statements,
			posisi_awal,
			self.tokenSkrg.posisi_akhir.salin()
		))
	
	def statement(self):
		res = HasilParse()
		posisi_awal = self.tokenSkrg.posisi_awal.salin()

		if self.tokenSkrg.sama_dengan(TokenKeyword, "kembali"):
			res.daftar_kemajuan()
			self.maju()

			expr = res.coba_daftar(self.expr())
			if not expr:
				self.balik(res.perhitungan_balik)
			return res.berhasil(NodeReturn(expr, posisi_awal, self.tokenSkrg.posisi_awal.salin()))

		if self.tokenSkrg.sama_dengan(TokenKeyword, "lanjutkan"):
			res.daftar_kemajuan()
			self.maju()
			return res.berhasil(NodeLanjutkan(posisi_awal, self.tokenSkrg.posisi_awal.salin()))

		if self.tokenSkrg.sama_dengan(TokenKeyword, "berhenti"):
			res.daftar_kemajuan()
			self.maju()
			return res.berhasil(NodeBreak(posisi_awal, self.tokenSkrg.posisi_awal.salin()))

		expr = res.daftar(self.expr())
		if res.error:
			return res.gagal(
				SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					res.error.details
					or "Harus memiliki lanjutkan, kembali, berhenti, int, float, lokal, '+', '-' atau parentesis",
				)
			)

		return res.berhasil(expr)

	def expr(self):
		res = HasilParse()

		if self.tokenSkrg.sama_dengan(TokenKeyword, "lokal"):
			res.daftar_kemajuan()
			self.maju()

			if self.tokenSkrg.tipe != TokenIdentifier:
				return res.gagal(
					SintaksSalah(
						self.tokenSkrg.posisi_awal,
						self.tokenSkrg.posisi_akhir,
						"Harus memiliki nama lokal",
					)
				)

			nama_lokal = self.tokenSkrg
			res.daftar_kemajuan()
			self.maju()

			if self.tokenSkrg.tipe != TokenSama:
				return res.gagal(
					SintaksSalah(
						self.tokenSkrg.posisi_awal,
						self.tokenSkrg.posisi_akhir,
						"Harus memiliki '=' untuk mendeklarasikan lokal",
					)
				)

			res.daftar_kemajuan()
			self.maju()
			expr = res.daftar(self.expr())
			if res.error:
				return res
			return res.berhasil(NodeBuatlokal(nama_lokal, expr))

		node = res.daftar(
			self.binary_operator(
				self.perbandingan_expr, ((TokenKeyword, "dan"), (TokenKeyword, "atau"))
			)
		)

		if res.error:
			return res.gagal(
				SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					res.error.details
					or "Harus memiliki int, float, lokal, '+', '-' atau parentesis",
				)
			)

		return res.berhasil(node)
		# return self.binary_operator(self.term, (TokenTambah, TokenKurang, TokenPangkat))

	def buat_fungsi(self):
		res = HasilParse()

		if not self.tokenSkrg.sama_dengan(TokenKeyword, "fungsi"):
			return res.gagal(
				SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					"Dibutuhkan 'fungsi'",
				)
			)

		res.daftar_kemajuan()
		self.maju()

		if self.tokenSkrg.tipe == TokenIdentifier:
			token_nama_lokal = self.tokenSkrg
			res.daftar_kemajuan()
			self.maju()
			if self.tokenSkrg.tipe != TokenParentesisKiri:
				return res.gagal(
					SintaksSalah(
						self.tokenSkrg.posisi_awal,
						self.tokenSkrg.posisi_akhir,
						"Dibutuhkan '('",
					)
				)

		else:
			token_nama_lokal = None
			if self.tokenSkrg.tipe != TokenParentesisKiri:
				return res.gagal(
					SintaksSalah(
						self.tokenSkrg.posisi_awal,
						self.tokenSkrg.posisi_akhir,
						"Dibutuhkan pengenal lokal atau '('",
					)
				)

		res.daftar_kemajuan()
		self.maju()
		nama_token_parameter = []

		if self.tokenSkrg.tipe == TokenIdentifier:
			nama_token_parameter.append(self.tokenSkrg)
			res.daftar_kemajuan()
			self.maju()

			while self.tokenSkrg.tipe == TokenKoma:
				res.daftar_kemajuan()
				self.maju()

				if self.tokenSkrg.tipe != TokenIdentifier:
					return res.gagal(
						SintaksSalah(
							self.tokenSkrg.posisi_awal,
							self.tokenSkrg.posisi_akhir,
							"Dibutuhkan pengenal lokal atau '('",
						)
					)

				nama_token_parameter.append(self.tokenSkrg)
				res.daftar_kemajuan()
				self.maju()

			if self.tokenSkrg.tipe != TokenParentesisKanan:
				return res.gagal(
					SintaksSalah(
						self.tokenSkrg.posisi_awal,
						self.tokenSkrg.posisi_akhir,
						"Dibutuhkan ',' atau ')'",
					)
				)
		else:
			if self.tokenSkrg.tipe != TokenParentesisKanan:
				return res.gagal(
					SintaksSalah(
						self.tokenSkrg.posisi_awal,
						self.tokenSkrg.posisi_akhir,
						"Dibutuhkan pengenal lokal atau ')'",
					)
				)

		res.daftar_kemajuan()
		self.maju()
		
		if self.tokenSkrg.tipe == TokenPanah:
			res.daftar_kemajuan()
			self.maju()

			isifungsi = res.daftar(self.expr())
			if res.error:
				return res

			return res.berhasil(
			   NodeBuatFungsi(token_nama_lokal, nama_token_parameter, isifungsi, True)
			)
	   
		if self.tokenSkrg.tipe != TokenLineBaru:
			return res.gagal(
				SintaksSalah(
					self.tokenSkrg.posisi_awal,
					self.tokenSkrg.posisi_akhir,
					"Dibutuhkan '->' atau baris baru \"\\n\"",
				)
			)

		res.daftar_kemajuan()
		self.maju()

		isistatement = res.daftar(self.statements())
		if res.error: return res

		if not self.tokenSkrg.sama_dengan(TokenKeyword, 'tutup'):
			return res.gagal(SintaksSalah(
				self.tokenSkrg.posisi_awal, self.tokenSkrg.posisi_akhir,
					"Dibutuhkan 'tutup'"
				))

		res.daftar_kemajuan()
		self.maju()

		return res.berhasil(
			NodeBuatFungsi(token_nama_lokal, nama_token_parameter, isistatement, False)
		)

	def binary_operator(self, fungsiA, option, fungsiB=None):
		if fungsiB == None:
			fungsiB = fungsiA

		hasil = HasilParse()
		kiri = hasil.daftar(fungsiA())
		if hasil.error:
			return hasil

		while (
			self.tokenSkrg.tipe in option
			or (self.tokenSkrg.tipe, self.tokenSkrg.value) in option
		):
			operator_token = self.tokenSkrg
			hasil.daftar_kemajuan()
			self.maju()
			kanan = hasil.daftar(fungsiB())
			if hasil.error:
				return hasil
			kiri = NodeOperasiBinary(kiri, operator_token, kanan)
		return hasil.berhasil(kiri)


# HASIL RUNTIME
class HasilRuntime:
	def __init__(self):
		self.reset()
	
	def reset(self):
		self.value = None
		self.error = None
		self.isi_returned_fungsi = None
		self.loop_lanjutkan = False
		self.loop_break = False

	def daftar(self, res):
		self.error = res.error
		self.isi_returned_fungsi = res.isi_returned_fungsi
		self.loop_lanjutkan = res.loop_lanjutkan
		self.loop_break = res.loop_break
		return res.value

	def berhasil(self, hasil):
		self.reset()
		self.value = hasil
		return self

	def berhasil_return(self, hasil):
		self.reset()
		self.isi_returned_fungsi = hasil
		return self

	def berhasil_lanjutkan(self):
		self.reset()
		self.loop_lanjutkan = True
		return self

	def berhasil_break(self):
		self.reset()
		self.loop_break = True
		return self

	def gagal(self, error):
		self.reset()
		self.error = error
		return self

	def harus_return(self):
		return (
			self.error or self.isi_returned_fungsi or self.loop_lanjutkan or self.loop_break
		)


# Nilai
class Isi:
	def __init__(self):
		self.atur_posisi()
		self.atur_konteks()

	def atur_posisi(self, posisi_awal=None, posisi_akhir=None):
		self.posisi_awal = posisi_awal
		self.posisi_akhir = posisi_akhir
		return self

	def atur_konteks(self, konteks=None):
		self.konteks = konteks
		return self

	def tambah_ke(self, lain):
		return None, self.operasi_illegal(lain)

	def kurangi_oleh(self, lain):
		return None, self.operasi_illegal(lain)

	def kali_oleh(self, lain):
		return None, self.operasi_illegal(lain)

	def bagi_oleh(self, lain):
		return None, self.operasi_illegal(lain)

	def pangkat_oleh(self, lain):
		return None, self.operasi_illegal(lain)

	def modulus_oleh(self, lain):
		return None, self.operasi_illegal(lain)

	def perbandingan_persamaan(self, lain):
		return None, self.operasi_illegal(lain)

	def perbandingan_tidak_sama(self, lain):
		return None, self.operasi_illegal(lain)

	def perbandingan_kurang_dari(self, lain):
		return None, self.operasi_illegal(lain)

	def perbandingan_lebih_dari(self, lain):
		return None, self.operasi_illegal(lain)

	def perbandingan_sama_kurang_dari(self, lain):
		return None, self.operasi_illegal(lain)

	def perbandingan_sama_lebih_dari(self, lain):
		return None, self.operasi_illegal(lain)

	def dan_oleh(self, lain):
		return None, self.operasi_illegal(lain)

	def atau_oleh(self, lain):
		return None, self.operasi_illegal(lain)

	def bukan(self, lain):
		return None, self.operasi_illegal(lain)

	def apakah_benar(self):
		return False

	def salin(self):
		raise Exception("Metode salin tidak diperbolehkan")

	def operasi_illegal(self, lain=None):
		if not lain:
			lain = self
		return RTError(
			self.posisi_awal, lain.posisi_akhir, "Operasi Illegal", self.konteks
		)


class Nil(Isi):
	def __init__(self):
		super().__init__()
		self.nilai = "nil"
	
	def tambah_ke(self, dataLain):
		if isinstance(dataLain, Angka):
			return dataLain.salin(), None
		if isinstance(dataLain, String):
			return String(self.nilai + dataLain.nilai), None
		return self.salin(), None

	def kurangi_oleh(self, dataLain):
		return self.salin(), None

	def kali_oleh(self, angkaLain):
		return self.salin(), None

	def pangkat_oleh(self, angkaLain):
		return self.salin(), None

	def modulus_oleh(self, angkaLain):
		return self.salin(), None

	def salin(self):
		salinan = Nil()
		salinan.atur_konteks(self.konteks)
		salinan.atur_posisi(self.posisi_awal, self.posisi_akhir)
		return salinan

	def __repr__(self):
		return "nil"


class Angka(Isi):
	def __init__(self, nilai):
		super().__init__()
		self.nilai = nilai

	def tambah_ke(self, angkaLain):
		if isinstance(angkaLain, Angka):
			return Angka(self.nilai + angkaLain.nilai).atur_konteks(self.konteks), None
		elif isinstance(angkaLain, Nil):
			return self.salin(), None
		else:
			return None, Isi.operasi_illegal(self, angkaLain)

	def kurangi_oleh(self, angkaLain):
		if isinstance(angkaLain, (Angka, Nil)):
			return Angka(self.nilai - angkaLain.nilai).atur_konteks(self.konteks), None
		else:
			return None, Isi.operasi_illegal(self, angkaLain)

	def kali_oleh(self, angkaLain):
		if isinstance(angkaLain, (Angka, Nil)):
			return Angka(self.nilai * angkaLain.nilai).atur_konteks(self.konteks), None
		else:
			return None, Isi.operasi_illegal(self, angkaLain)

	def bagi_oleh(self, angkaLain):
		if isinstance(angkaLain, Angka):
			if angkaLain.nilai == 0:
				return None, RTError(
					angkaLain.posisi_awal,
					angkaLain.posisi_akhir,
					"Pembagian dengan nol (Tak terbatas)",
					self.konteks,
				)
			return Angka(self.nilai / angkaLain.nilai).atur_konteks(self.konteks), None
		else:
			return None, Isi.operasi_illegal(self, angkaLain)

	def pangkat_oleh(self, angkaLain):
		if isinstance(angkaLain, (Angka, Nil)):
			return Angka(self.nilai ** angkaLain.nilai).atur_konteks(self.konteks), None
		else:
			return None, Isi.operasi_illegal(self, angkaLain)

	def modulus_oleh(self, angkaLain):
		if isinstance(angkaLain, (Angka, Nil)):
			return Angka(self.nilai % angkaLain.nilai).atur_konteks(self.konteks), None
		else:
			return None, Isi.operasi_illegal(self, angkaLain)

	def perbandingan_persamaan(self, lain):
		if isinstance(lain, Angka):
			return Angka(int(self.nilai == lain.nilai)).atur_konteks(self.konteks), None
		else:
			return None, Isi.operasi_illegal(self, lain)

	def perbandingan_tidak_sama(self, lain):
		if isinstance(lain, Angka):
			return Angka(int(self.nilai != lain.nilai)).atur_konteks(self.konteks), None
		else:
			return None, Isi.operasi_illegal(self, lain)

	def perbandingan_kurang_dari(self, lain):
		if isinstance(lain, Angka):
			return Angka(int(self.nilai < lain.nilai)).atur_konteks(self.konteks), None
		else:
			return None, Isi.operasi_illegal(self, lain)

	def perbandingan_lebih_dari(self, lain):
		if isinstance(lain, Angka):
			return Angka(int(self.nilai > lain.nilai)).atur_konteks(self.konteks), None
		else:
			return None, Isi.operasi_illegal(self, lain)

	def perbandingan_sama_kurang_dari(self, lain):
		if isinstance(lain, Angka):
			return Angka(int(self.nilai <= lain.nilai)).atur_konteks(self.konteks), None
		else:
			return None, Isi.operasi_illegal(self, lain)

	def perbandingan_sama_lebih_dari(self, lain):
		if isinstance(lain, Angka):
			return Angka(int(self.nilai >= lain.nilai)).atur_konteks(self.konteks), None
		else:
			return None, Isi.operasi_illegal(self, lain)

	def dan_oleh(self, lain):
		if isinstance(lain, Angka):
			return (
				Angka(int(self.nilai and lain.nilai)).atur_konteks(self.konteks),
				None,
			)
		else:
			return None, Isi.operasi_illegal(self, lain)

	def atau_oleh(self, lain):
		if isinstance(lain, Angka):
			return Angka(int(self.nilai or lain.nilai)).atur_konteks(self.konteks), None
		else:
			return None, Isi.operasi_illegal(self, lain)

	def bukan(self):
		return Angka(1 if self.nilai == 0 else 0).atur_konteks(self.konteks), None

	def salin(self):
		salin = Angka(self.nilai)
		salin.atur_konteks(self.konteks)
		salin.atur_posisi(self.posisi_awal, self.posisi_akhir)
		return salin

	def apakah_benar(self):
		return self.nilai != 0

	def __repr__(self):
		return str(self.nilai)


Angka.salah = Angka(0)
Angka.benar = Angka(1)
Angka.nil = Nil()


class String(Isi):
	def __init__(self, isi):
		super().__init__()
		self.nilai = isi

	def tambah_ke(self, stringLain):
		if isinstance(stringLain, (String, Angka)):
			return (
				String(self.nilai + str(stringLain.nilai)).atur_konteks(self.konteks),
				None,
			)
		else:
			return None, Isi.operasi_illegal(self, stringLain)

	def kali_oleh(self, angkaLain):
		if isinstance(angkaLain, Angka):
			return String(self.nilai * angkaLain.nilai).atur_konteks(self.konteks), None
		else:
			return None, Isi.operasi_illegal(self, angkaLain)

	def apakah_benar(self):
		return len(self.nilai) > 0

	def salin(self):
		salin = String(self.nilai)
		salin.atur_konteks(self.konteks)
		salin.atur_posisi(self.posisi_awal, self.posisi_akhir)
		return salin

	def __repr__(self):
		return f'"{self.nilai}"'


class Daftar(Isi):
	def __init__(self, isi_elemen):
		super().__init__()
		self.isi = isi_elemen

	def tambah_ke(self, lain):
		daftar_baru = self.salin()
		daftar_baru.isi.append(lain)
		return daftar_baru, None

	def kurangi_oleh(self, lain):
		if isinstance(lain, Angka):
			daftar_baru = self.salin()
			try:
				daftar_baru.isi.pop(lain.nilai)
				return daftar_baru, None
			except:
				return daftar_baru, None
		else:
			return None, Isi.operasi_illegal(self, lain)

	def kali_oleh(self, lain):
		if isinstance(lain, Daftar):
			daftar_baru = self.salin()
			daftar_baru.isi.extend(lain.isi)
			return daftar_baru, None
		else:
			return None, Isi.operasi_illegal(self, lain)

	def bagi_oleh(self, lain):
		if isinstance(lain, Angka):
			try:
				return self.isi[lain.nilai], None
			except:
				return (
					Nil()
					.atur_konteks(self.konteks)
					.atur_posisi(self.posisi_awal, self.posisi_akhir),
					None,
				)
		else:
			return None, Isi.operasi_illegal(self, lain)

	def salin(self):
		salinan = Daftar(self.isi)
		salinan.atur_konteks(self.konteks)
		salinan.atur_posisi(self.posisi_awal, self.posisi_akhir)
		return salinan

	def __repr__(self):
		return f'[{", ".join([str(isinya) for isinya in self.isi])}]'


class BaseFungsi(Isi):
	def __init__(self, nama):
		super().__init__()
		self.nama = nama or "<fungsi tidak diketahui>"

	def buat_konteks_baru(self):
		konteks_baru = Konteks(self.nama, self.konteks, self.posisi_awal)
		konteks_baru.TabelSimbol = TabelSimbol(konteks_baru.induk.TabelSimbol)

		return konteks_baru

	def cek_parameter(self, nama_parameter, parameter):
		res = HasilRuntime()

		if len(parameter) > len(nama_parameter):
			list_sementara = list(parameter)
			while len(list_sementara) > len(nama_parameter):
				list_sementara.pop()
			parameter = list_sementara
			
		if len(parameter) < len(nama_parameter):
			list_sementara = list(parameter)
			while len(list_sementara) < len(nama_parameter):
				list_sementara.append(
					Nil()
					.atur_konteks(self.konteks)
					.atur_posisi(self.posisi_awal, self.posisi_akhir)
				)
			parameter = list_sementara

		return res.berhasil(parameter)

	def hitung_parameter(self, nama_parameters, parameters, konteks):
		for i in range(len(parameters)):
			nama_parameter = nama_parameters[i]
			isi_parameter = parameters[i]
			isi_parameter.atur_konteks(konteks)
			konteks.TabelSimbol.tulis(nama_parameter, isi_parameter)

	def cek_dan_hitung_parameter(self, nama_parameter, parameter, konteks):
		res = HasilRuntime()
		parameter = res.daftar(self.cek_parameter(nama_parameter, parameter))
		if res.harus_return(): return res
		self.hitung_parameter(nama_parameter, parameter, konteks)
		return res.berhasil(None)


class Fungsi(BaseFungsi):
	def __init__(self, nama, isi_node, nama_parameter, harus_return_null):
		super().__init__(nama)
		# self.nama = nama or "<tidak diketahui>"
		self.isi_node = isi_node
		self.nama_parameter = nama_parameter
		self.harus_return_null = harus_return_null

	def esekusi(self, parameter):
		res = HasilRuntime()
		interpreter = Interpreter()
		konteks_baru = self.buat_konteks_baru()

		res.daftar(
			self.cek_dan_hitung_parameter(self.nama_parameter, parameter, konteks_baru)
		)
		if res.harus_return():
			return res

		nilai = res.daftar(interpreter.kunjungi(self.isi_node, konteks_baru))
		if res.harus_return() and res.isi_returned_fungsi == None:
			return res

		isi_yg_direturn = (nilai if self.harus_return_null else None) or res.isi_returned_fungsi or Angka.nil
		return res.berhasil(isi_yg_direturn)

	def salin(self):
		salinan = Fungsi(self.nama, self.isi_node, self.nama_parameter, self.harus_return_null)
		salinan.atur_konteks(self.konteks)
		salinan.atur_posisi(self.posisi_awal, self.posisi_akhir)
		return salinan

	def __repr__(self):
		return f"<fungsi {self.nama}>"


class BuiltInFungsi(BaseFungsi):
	def __init__(self, nama):
		super().__init__(nama)

	def esekusi(self, params):
		res = HasilRuntime() 
		konteks_esekusi = self.buat_konteks_baru()

		nama_metode = f"esekusi_{self.nama}"
		metode = getattr(self, nama_metode, self.HandleTidakKunjungi)

		res.daftar(
			self.cek_dan_hitung_parameter(
				metode.nama_parameter, params, konteks_esekusi
			)
		)
		if res.harus_return():
			return res

		hasil = res.daftar(metode(konteks_esekusi))
		if res.harus_return():
			return res
		return res.berhasil(hasil)

	def HandleTidakKunjungi(self, node, konteks):
		raise Exception(f"Tidak ada metode esekusi_{type(node).__name__}")

	def salin(self):
		salinan = BuiltInFungsi(self.nama)
		salinan.atur_konteks(self.konteks)
		salinan.atur_posisi(self.posisi_awal, self.posisi_akhir)
		return salinan

	def __repr__(self):
		return f"<built-in fungsi {self.nama}>"

	# ------------------- BUILT-IN FUNCTION ----------------------------- #

	def esekusi_print(self, konteks_esekusi):
		print(str(konteks_esekusi.TabelSimbol.dapat("isi") or Nil()))
		return HasilRuntime().berhasil(Angka.nil)
	esekusi_print.nama_parameter = ["isi"]

	def esekusi_tunggu(self, konteks_esekusi):
		detik = repr(konteks_esekusi.TabelSimbol.dapat("waitsecond") or 0.1)
		time.sleep(float(detik))
		return HasilRuntime().berhasil(Angka.nil)
		# lokal e = 0; saat e < 50 maka tulis(e + 1); tunggu(1); lokal e = e + 1 tutup
	esekusi_tunggu.nama_parameter = ["waitsecond"]

	def esekusi_tipe(self, konteks_esekusi):
		return HasilRuntime().berhasil(String(type(konteks_esekusi.TabelSimbol.dapat("data") or Nil()).__name__.lower()))
	esekusi_tipe.nama_parameter = ["data"]

	def esekusi_panjang(self, konteks_esekusi):
		dataparam = konteks_esekusi.TabelSimbol.dapat("strlistdata") or Nil()
		if isinstance(dataparam, (Daftar, String)):
			return HasilRuntime().berhasil(Angka(len(dataparam.isi if isinstance(dataparam, Daftar) else dataparam.nilai)))
		else:
			return HasilRuntime().berhasil(Angka(0))
	esekusi_panjang.nama_parameter = ["strlistdata"]

	def esekusi_masukkan(self, konteks_esekusi):
		list_ = konteks_esekusi.TabelSimbol.dapat("list")
		value = konteks_esekusi.TabelSimbol.dapat("value")

		if not isinstance(list_, Daftar):
			return HasilRuntime().gagal(RTError(
				self.posisi_awal, self.posisi_akhir,
				"Parameter pertama harus berupa Array",
			 	konteks_esekusi
	  		))
		
		if isinstance(value, Nil):
			return HasilRuntime().gagal(RTError(
				self.posisi_awal, self.posisi_akhir,
				"Parameter kedua tidak boleh nil",
			 	konteks_esekusi
	  		))

		list_.isi.append(value)
		return HasilRuntime().berhasil(Angka(len(list_.isi) - 1))
	esekusi_masukkan.nama_parameter = ["list", "value"]

	def esekusi_jalankan(self, konteks_esekusi):
		namaFile = konteks_esekusi.TabelSimbol.dapat("nama_file")

		if not isinstance(namaFile, String):
			return HasilRuntime().gagal(RTError(
				self.posisi_awal, self.posisi_akhir,
				"Parameter pertama harus berupa String",
			 	konteks_esekusi
	  		))

		namaFile = namaFile.nilai
		file_target = Path(namaFile)

		if not file_target.is_file():
			return HasilRuntime().gagal(RTError(
				self.posisi_awal, self.posisi_akhir,
				f"File {namaFile} tidak ditemukan",
			 	konteks_esekusi
	  		))
		
		script = file_target.read_text()
		hasil, error = esekusi(namaFile, script)
	
		if error:
			return HasilRuntime().gagal(RTError(
				self.posisi_awal, self.posisi_akhir,
				f"Gagal mengesekusi script, \"{namaFile}\"\n" +
				error.jadiString(),
				konteks_esekusi
	  		))

		return HasilRuntime().berhasil(Angka.nil)
	esekusi_jalankan.nama_parameter = ["nama_file"]

BuiltInFungsi.tulis = BuiltInFungsi("print")
BuiltInFungsi.wait = BuiltInFungsi("tunggu")
BuiltInFungsi.tipe = BuiltInFungsi("tipe")
BuiltInFungsi.panjang = BuiltInFungsi("panjang")
BuiltInFungsi.masuk = BuiltInFungsi("masukkan")
BuiltInFungsi.esekusi_builtin = BuiltInFungsi("jalankan")

# Konteks
class Konteks:
	def __init__(self, display_nama, induk=None, posisi_urutan_induk=None):
		self.display_nama = display_nama
		self.induk = induk
		self.posisi_urutan_induk = posisi_urutan_induk
		self.TabelSimbol = None


# Tabel simbol
class TabelSimbol:
	def __init__(self, induk=None):
		self.simbol = {}
		self.induk = induk

	def dapat(self, nama):
		isi = self.simbol.get(nama, None)
		if isi == None and self.induk:
			return self.induk.dapat(nama)
		return isi

	def tulis(self, nama, isi):
		self.simbol[nama] = isi

	def hapus(self, nama):
		del self.simbol[nama]


# INTERPRETER (di compile)
class Interpreter:
	def kunjungi(self, node, konteks):
		nama_metode = f"kunjungi_{type(node).__name__}"
		metode = getattr(self, nama_metode, self.HandleTidakKunjungi)
		return metode(node, konteks)

	def HandleTidakKunjungi(self, node, konteks):
		raise Exception(f"Tidak ada metode kunjungi_{type(node).__name__}")

	def kunjungi_NodeAkseslokal(self, node, konteks):
		res = HasilRuntime()
		nama_lokal = node.nama_token_lokal.value
		isi = konteks.TabelSimbol.dapat(nama_lokal)

		if not isi:
			return res.gagal(
				RTError(
					node.posisi_awal,
					node.posisi_akhir,
					f"lokal '{nama_lokal}' tidak dideklarasikan",
					konteks,
				)
			)

		isi = isi.salin().atur_posisi(node.posisi_awal, node.posisi_akhir).atur_konteks(konteks)
		return res.berhasil(isi)

	def kunjungi_NodeBuatlokal(self, node, konteks):
		res = HasilRuntime()
		nama_lokal = node.nama_token_lokal.value
		isi = res.daftar(self.kunjungi(node.isi_node, konteks))
		if res.harus_return():
			return res

		konteks.TabelSimbol.tulis(nama_lokal, isi)
		return res.berhasil(isi)

	def kunjungi_NodeAngka(self, node, konteks):
		return HasilRuntime().berhasil(
			Angka(node.token.value)
			.atur_konteks(konteks)
			.atur_posisi(node.posisi_awal, node.posisi_akhir)
		)

	def kunjungi_NodeString(self, node, konteks):
		return HasilRuntime().berhasil(
			String(node.token.value)
			.atur_konteks(konteks)
			.atur_posisi(node.posisi_awal, node.posisi_akhir)
		)

	def kunjungi_DaftarNode(self, node, konteks):
		res = HasilRuntime()
		isian = []

		for element_node in node.isi_daftar:
			isian.append(res.daftar(self.kunjungi(element_node, konteks)))
			if res.harus_return():
				return res


		return res.berhasil(
			Daftar(isian)
			.atur_konteks(konteks)
			.atur_posisi(node.posisi_awal, node.posisi_akhir)
		)

	def kunjungi_NodeOperasiBinary(self, node, konteks):
		hasil = HasilRuntime()
		kiri = hasil.daftar(self.kunjungi(node.node_kiri, konteks))
		if hasil.harus_return():
			return hasil
		kanan = hasil.daftar(self.kunjungi(node.node_kanan, konteks))
		if hasil.harus_return():
			return hasil
		# print(kiri)
		# print(node.operator_token.value)
		if node.operator_token.tipe == TokenTambah:
			jawaban, error = kiri.tambah_ke(kanan)
		elif node.operator_token.tipe == TokenKurang:
			jawaban, error = kiri.kurangi_oleh(kanan)
		elif node.operator_token.tipe == TokenKali:
			jawaban, error = kiri.kali_oleh(kanan)
		elif node.operator_token.tipe == TokenBagi:
			jawaban, error = kiri.bagi_oleh(kanan)
		elif node.operator_token.tipe == TokenPangkat:
			jawaban, error = kiri.pangkat_oleh(kanan)
		elif node.operator_token.tipe == TokenModulo:
			jawaban, error = kiri.modulus_oleh(kanan)
		elif node.operator_token.tipe == TokenSamaSama:
			jawaban, error = kiri.perbandingan_persamaan(kanan)
		elif node.operator_token.tipe == TokenTidakSama:
			jawaban, error = kiri.perbandingan_tidak_sama(kanan)
		elif node.operator_token.tipe == TokenKurangDari:
			jawaban, error = kiri.perbandingan_kurang_dari(kanan)
		elif node.operator_token.tipe == TokenLebihDari:
			jawaban, error = kiri.perbandingan_lebih_dari(kanan)
		elif node.operator_token.tipe == TokenKurangAtauSama:
			jawaban, error = kiri.perbandingan_sama_kurang_dari(kanan)
		elif node.operator_token.tipe == TokenLebihAtauSama:
			jawaban, error = kiri.perbandingan_sama_lebih_dari(kanan)
		elif node.operator_token.sama_dengan(TokenKeyword, "dan"):
			jawaban, error = kiri.dan_oleh(kanan)
		elif node.operator_token.sama_dengan(TokenKeyword, "atau"):
			jawaban, error = kiri.atau_oleh(kanan)
		# print(error)
		if error:
			return hasil.gagal(error)
		else:
			return hasil.berhasil(
				jawaban.atur_posisi(node.posisi_awal, node.posisi_akhir)
			)

	def kunjungi_NodeOperatorMinus(self, node, konteks):
		# print("nemu OperasiBinary minus")
		hasil = HasilRuntime()
		angka = hasil.daftar(self.kunjungi(node.node, konteks))
		if hasil.harus_return():
			return hasil

		error = None

		if node.operator_token.tipe == TokenKurang:
			angka, error = angka.kali_oleh(Angka(-1))
		elif node.operator_token.sama_dengan(TokenKeyword, "bukan"):
			angka, error = angka.bukan()

		if error:
			return hasil.gagal(error)
		else:
			return hasil.berhasil(
				angka.atur_posisi(node.posisi_awal, node.posisi_akhir)
			)

	def kunjungi_NodeIF(self, node, konteks):
		res = HasilRuntime()
	
		for kondisi, expr, harus_return_null in node.cases:
			kondisi_value = res.daftar(self.kunjungi(kondisi, konteks))
			if res.harus_return():
				return res

			if kondisi_value.apakah_benar():
				isi_expr = res.daftar(self.kunjungi(expr, konteks))
				if res.harus_return():
					return res
				return res.berhasil(Angka.nil if harus_return_null else isi_expr)

		if node.else_case:
			expr, harus_return_null = node.else_case
			isi_else = res.daftar(self.kunjungi(expr, konteks))
			if res.harus_return():
				return res
			return res.berhasil(Angka.nil if harus_return_null else isi_else)

		return res.berhasil(Angka.nil)

	def kunjungi_NodeFor(self, node, konteks):
		res = HasilRuntime()
		isi = []

		isi_awal = res.daftar(self.kunjungi(node.node_mulai_nilai, konteks))
		if res.harus_return():
			return res

		end_value = res.daftar(self.kunjungi(node.node_akhir_nilai, konteks))
		if res.harus_return():
			return res

		if node.node_step_nilai:
			step_value = res.daftar(self.kunjungi(node.node_step_nilai, konteks))
			if res.harus_return():
				return res
		else:
			step_value = Angka(1)

		i = isi_awal.nilai

		if step_value.nilai >= 0:
			condition = lambda: i < end_value.nilai
		else:
			condition = lambda: i > end_value.nilai

		while condition():
			konteks.TabelSimbol.tulis(node.namalokal_token.value, Angka(i))
			i += step_value.nilai

			isinode = res.daftar(self.kunjungi(node.isi_node, konteks))
			if res.harus_return() and res.loop_lanjutkan == False and res.loop_break == False: 
				return res

			if res.loop_lanjutkan:
				continue

			if res.loop_break:
				break

			isi.append(isinode)

		return res.berhasil(Angka.nil if node.harus_return_null else Daftar(isi).atur_konteks(konteks).atur_posisi(node.posisi_awal, node.posisi_akhir))

	def kunjungi_NodeWhile(self, node, konteks):
		res = HasilRuntime()
		isi = []

		while True:
			kondisi = res.daftar(self.kunjungi(node.kondisi, konteks))
			if res.harus_return():
				return res

			if not kondisi.apakah_benar() and res.loop_lanjutkan == False and res.loop_break == False: 
				break

			isinode = res.daftar(self.kunjungi(node.isi_node, konteks))
			if res.harus_return():
				return res

			if res.loop_lanjutkan:
				continue

			if res.loop_break:
				break

			isi.append(isinode)

		return res.berhasil(Angka.nil if node.harus_return_null else Daftar(isi).atur_konteks(konteks).atur_posisi(node.posisi_awal, node.posisi_akhir))

	def kunjungi_NodeBuatFungsi(self, node, konteks):
		res = HasilRuntime()

		nama_fungsi = node.namalokal_token.value if node.namalokal_token else None
		isi_node = node.isi_node
		nama_parameter = [nama_param.value for nama_param in node.nama_parameter_token]
		isi_fungsi = Fungsi(nama_fungsi, isi_node, nama_parameter, node.harus_return_null).atur_konteks(konteks).atur_posisi(node.posisi_awal, node.posisi_akhir)

		if node.namalokal_token:
			konteks.TabelSimbol.tulis(nama_fungsi, isi_fungsi)

		return res.berhasil(isi_fungsi)

	def kunjungi_NodePanggil(self, node, konteks):
		res = HasilRuntime()
		parameters = []

		isi_untuk_dipanggil = res.daftar(
			self.kunjungi(node.node_untuk_panggil, konteks)
		)
		if res.harus_return():
			return res
		isi_untuk_dipanggil = isi_untuk_dipanggil.salin().atur_posisi(
			node.posisi_awal, node.posisi_akhir
		)

		for arg_node in node.node_parameter:
			parameters.append(res.daftar(self.kunjungi(arg_node, konteks)))
			if res.harus_return():
				return res

		hasil = res.daftar(isi_untuk_dipanggil.esekusi(parameters))
		if res.harus_return():
			return res
		hasil = hasil.salin().atur_posisi(node.posisi_awal, node.posisi_akhir).atur_konteks(konteks)	
		return res.berhasil(hasil)

	def kunjungi_NodeReturn(self, node, konteks):
		res = HasilRuntime()

		if node.node_untuk_return:
			value = res.daftar(self.kunjungi(node.node_untuk_return, konteks))
			if res.harus_return(): return res
		else:
			value = Angka.nil
		
		#print("ketemu return ", value)
		return res.berhasil_return(value)

	def kunjungi_NodeLanjutkan(self, node, konteks):
		#print("ketemu continue")
		return HasilRuntime().berhasil_lanjutkan()

	def kunjungi_NodeBreak(self, node, context):
		#print("ketemu break")
		return HasilRuntime().berhasil_break()


# ESEKUSI (RUN)

global_tabel_simbol = TabelSimbol()
global_tabel_simbol.tulis("nil", Angka.nil)
global_tabel_simbol.tulis("salah", Angka.salah)  # false
global_tabel_simbol.tulis("benar", Angka.benar)  # true
global_tabel_simbol.tulis("tulis", BuiltInFungsi.tulis)
global_tabel_simbol.tulis("tunggu", BuiltInFungsi.wait)
global_tabel_simbol.tulis("tipe", BuiltInFungsi.tipe)
global_tabel_simbol.tulis("panjang", BuiltInFungsi.panjang)
global_tabel_simbol.tulis("masuk", BuiltInFungsi.masuk)
global_tabel_simbol.tulis("esekusi", BuiltInFungsi.esekusi_builtin)

def esekusi(namafile, teks):
	lexer = Lexer(namafile, teks)
	tokens, error = lexer.buatToken()
	if error:
		return None, error

	# Buat AST (Abstract Syntax Tree)
	parser = Parser(tokens)
	ast = parser.parse()
	if ast.error:
		return None, ast.error

	# Jalankan Program
	interpreter = Interpreter()
	konteks = Konteks("<program>")
	konteks.TabelSimbol = global_tabel_simbol
	hasil = interpreter.kunjungi(ast.node, konteks)

	return hasil.value, hasil.error
