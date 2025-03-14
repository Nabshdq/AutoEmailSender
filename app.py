from flask import Flask, render_template, request, jsonify
import smtplib
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from config import (
    SMTP_SERVER,
    SMTP_PORT,
    EMAIL_SENDER,
    EMAIL_PASSWORD,
    EMAIL_RECEIVER,
    EMAIL_CC,
)

app = Flask(__name__)

# Folder tempat menyimpan dokumen
DOCUMENTS_FOLDER = os.path.abspath("documents")  # Menggunakan path absolut untuk memastikan folder yang benar

TIME_DELAY = 10  # Waktu tunggu antara pengiriman email dalam detik

# Fungsi untuk mengirim email dengan percobaan ulang jika gagal
def send_email(subject, body, attachment, sender, password, receiver, cc, retries=3):
    attempt = 0
    status_messages = []
    while attempt < retries:
        try:
            print(f"Mencoba mengirim email: {attachment}")  # Log untuk debugging
            # Buat objek email
            msg = MIMEMultipart()
            msg["From"] = sender
            msg["To"] = receiver
            msg["Subject"] = subject
            msg["Cc"] = ", ".join(cc)

            # Tambahkan teks email
            msg.attach(MIMEText(body, "plain"))

            # Tambahkan lampiran
            attachment_path = os.path.join(DOCUMENTS_FOLDER, attachment)  # Menggunakan path absolut
            with open(attachment_path, "rb") as file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={attachment}")
                msg.attach(part)

            # Koneksi ke server SMTP
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
            server.starttls()  # Enkripsi koneksi
            server.login(sender, password)
            text = msg.as_string()

            # Gabungkan penerima utama dan CC
            recipients = [receiver] + cc
            server.sendmail(sender, recipients, text)
            server.quit()

            status_messages.append(f"✅ Email dengan {attachment} berhasil dikirim!")
            print(f"✅ Email dengan {attachment} berhasil dikirim!")  # Log sukses email
            return status_messages  # Keluar dari fungsi jika email berhasil dikirim
        except Exception as e:
            attempt += 1
            status_messages.append(f"❌ Gagal mengirim email dengan {attachment}. Percobaan ke-{attempt} gagal. Error: {e}")
            print(f"❌ Gagal mengirim email dengan {attachment}. Percobaan ke-{attempt} gagal. Error: {e}")  # Log error
            if attempt < retries:
                status_messages.append(f"⏳ Mencoba lagi...")
                print("⏳ Mencoba lagi...")  # Log mencoba lagi
                time.sleep(5)  # Tunggu 5 detik sebelum mencoba lagi
            else:
                status_messages.append(f"❌ Gagal mengirim email setelah {retries} percobaan. Melanjutkan ke file berikutnya.")
                print(f"❌ Gagal mengirim email setelah {retries} percobaan. Melanjutkan ke file berikutnya.")  # Log kegagalan terakhir
                break
    return status_messages


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Log data form untuk debug
        print(f"Data form: {request.form}")

        sender = request.form["sender"] or EMAIL_SENDER
        password = request.form["password"] or EMAIL_PASSWORD
        receiver = request.form["receiver"] or EMAIL_RECEIVER
        # Jika CC tidak diisi, gunakan list kosong
        cc = request.form.getlist("cc")
        cc = [email for email in cc if email]  # Hapus email kosong

        if not cc:  # Jika CC kosong, kita gunakan EMAIL_CC dari config.py
            cc = EMAIL_CC

        # Ambil file yang diupload
        uploaded_files = request.files.getlist("files[]")
        # Simpan file sementara ke folder documents
        file_paths = []
        for file in uploaded_files:
            filename = os.path.join(DOCUMENTS_FOLDER, file.filename)
            file.save(filename)  # Simpan file ke folder documents
            file_paths.append(filename)  # Simpan path file untuk dikirim

        status_messages = []
        # Loop untuk mengirim email satu per satu
        for idx, file_path in enumerate(file_paths, start=1):
            subject = os.path.basename(file_path)  # Mengambil nama file sebagai subject
            body = ""  # Body email yang tetap sama
            email_status = send_email(subject, body, file_path, sender, password, receiver, cc, retries=3)
            status_messages.append(email_status[0])  # Menambahkan status per email

            if idx < len(file_paths):  # Jangan tunggu setelah email terakhir
                time.sleep(TIME_DELAY)

            # Hapus file yang telah digunakan setelah dikirim
            os.remove(file_path)  # Menghapus file yang sudah digunakan

        return jsonify({"status": status_messages})  # Kembalikan status dalam format JSON

    return render_template("index.html", success=False)


if __name__ == "__main__":
    app.run(debug=True)
