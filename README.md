# SimpleWebSocket
Simple WebSocket server implemented using Python 3

## Kelompok HidupMahasiswa

## How to use

1. Pastikan Python 3 telah ter-install di komputer atau laptop Anda
2. Install dan connect account ngrok
3. Jalankan ngrok pada port 3000 dengan mengetik command

``./ngrok http 3000``

4. Buka folder src pada file zip yang telah diunduh
5. Buka terminal sesuai dengan folder yang berisi file server.py
6. Pastikan PORT yang akan digunakan belum terpakai oleh proses lain
7. Ketikkan command untuk menjalankan server

``python3 server.py``

8. Ketik ``localhost:4040/inspect/http`` pada kolom url
9. Buka website https://jarkom.tenshi.dev/ di tab atau window lain
10. Pindah ke halaman submit atau submission
11. Masukkan NIM dan nama
12. Masukkan websocket dengan menuliskan ``ws://`` ditambah headers host yang didapat dari localhost:4040/inspect/http
13. Klik submit
14. Masukkan token yang diterima melalui email std
15. Program sudah berjalan
 

## Pembagian Kerja
__________________________________________________________________________________
NIM      | Nama                     | Apa yang dikerjakan  | Persentase Kontribusi|
---------|--------------------------|----------------------|----------------------|
13517005 | Muhammad Rafi Zhafran    | server.py dan readme | 33%                  |
13517083 | Abiyyu Avicena Ismunandar| server.py dan readme | 33%                  |
13517101 | Jeremy Arden Hartono     | server.py dan readme | 33%                  |