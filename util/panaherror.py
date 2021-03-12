def panaherror(text, posisi_awal, posisi_akhir):
    result = ''

    idx_start = max(text.rfind('\n', 0, posisi_awal.indeks), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)
    
    line_count = posisi_akhir.baris - posisi_awal.baris + 1
    for i in range(line_count):
        # Hitung kolom baris
        line = text[idx_start:idx_end]
        col_start = posisi_awal.kolom if i == 0 else 0
        col_end = posisi_akhir.kolom if i == line_count - 1 else len(line) - 1

        # Masukkan hasil
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Menghitung ulang indeks
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

    return result.replace('\t', '')
