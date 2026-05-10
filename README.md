# Post Manager Desktop App

Aplikasi desktop CRUD Post Manager menggunakan Python, PySide6, dan REST API.

## Deskripsi

Aplikasi ini dibuat untuk mengelola data post menggunakan API nyata:

https://api.pahrul.my.id/api/posts

Aplikasi mendukung operasi CRUD lengkap:
- GET (menampilkan data post)
- POST (menambah post)
- PUT (mengedit post)
- DELETE (menghapus post)

Semua request API dijalankan menggunakan thread terpisah agar aplikasi tidak freeze saat proses request berlangsung.

---

# Teknologi yang Digunakan

- Python
- PySide6
- Requests
- REST API
- QThread

---

# Fitur Aplikasi

## 1. Menampilkan Semua Post
Menampilkan daftar post dalam bentuk tabel:
- ID
- Title
- Author
- Status

---

## 2. Detail Post
Saat baris tabel dipilih, aplikasi menampilkan:
- Title
- Body
- Author
- Slug
- Status
- Comments

---

## 3. Tambah Post
User dapat menambahkan post baru menggunakan form input.

---

## 4. Edit Post
User dapat mengubah data post yang dipilih.

---

## 5. Hapus Post
User dapat menghapus post dengan konfirmasi dialog terlebih dahulu.

---

## 6. Threading
Semua request API berjalan di thread terpisah menggunakan QThread sehingga UI tetap responsif.

---

## 7. Error Handling
Aplikasi menangani:
- timeout
- connection error
- validasi slug unik
