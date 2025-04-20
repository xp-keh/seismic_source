# Layanan Producer

Layanan ini bertujuan untuk melakukan query data seismik ke jaringan GEOFON yang kemudian akan memparsingnya ke format JSON dan mengirimkannya ke Kafka sesuai dengan topik yang ditentukan.

## Persyaratan

- Docker
- docker-compose
- Git

## Langkah 1: Clone Repositori

Clone repositori ke mesin lokal Anda menggunakan perintah berikut:

```bash
git clone https://github.com/distributed-eews/producer.git
cd producer
```

## Langkah 2: Atur Variabel Lingkungan

Ubah nama file `.env.example` menjadi `.env` dan atur variabel lingkungan berikut sesuai konfigurasi Anda:

```plaintext
BOOTSTRAP_SERVER=<Alamat Kafka>
TOPIC_NAME=<Nama topik Kafka yang akan dikirimkan data>
REDIS_HOST=<Host Redis>
REDIS_PORT=<Port Redis>
PORT=<Port layanan ini akan dijalankan>
```

## Langkah 3: Mulai Kontainer Docker

Gunakan docker-compose untuk memulai layanan:

```bash
docker-compose up -d
```

## Langkah 4: Verifikasi Deployment

Pastikan kontainer berjalan tanpa masalah:

```bash
docker-compose ps
```

## Langkah 5: Akses Layanan

Setelah kontainer berjalan, Anda dapat mengakses layanan yang berfungsi sebagai servis untuk melakukan query data seismik ke jaringan GEOFON. Layanan akan memparsing data tersebut menjadi format JSON dan mengirimkannya ke Kafka sesuai dengan topik yang ditentukan.

## Catatan Tambahan

- Pastikan layanan yang diperlukan seperti Kafka dan Redis dapat diakses dan dikonfigurasi dengan benar sebelum memulai deployment.
- Pantau log dan perilaku layanan untuk menyelesaikan masalah selama proses deployment.

Dengan langkah-langkah ini, Layanan Prooducer Anda seharusnya berhasil didaftarkan dan berjalan di lingkungan Anda.
