import streamlit as st
import heapq
import uuid
from datetime import datetime

# =====================================
# DATA USER
# =====================================

users = {
    "admin": {"password": "admin123", "role": "admin"},
    "konsumen": {"password": "user123", "role": "user"}
}

# =====================================
# SESSION STATE INIT
# =====================================

if "pengiriman" not in st.session_state:
    st.session_state.pengiriman = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

# =====================================
# GRAPH
# =====================================

class Graph:
    def __init__(self):
        self.graph = {}

    def tambah_kota(self, kota):
        if kota not in self.graph:
            self.graph[kota] = []

    def hapus_kota(self, kota):
        if kota in self.graph:
            del self.graph[kota]

            for node in self.graph:
                self.graph[node] = [
                    (t, j)
                    for t, j in self.graph[node]
                    if t != kota
                ]

    def tambah_jalur(self, asal, tujuan, jarak):
        self.tambah_kota(asal)
        self.tambah_kota(tujuan)

        self.graph[asal].append((tujuan, jarak))
        self.graph[tujuan].append((asal, jarak))

    def hapus_jalur(self, asal, tujuan):

        if asal in self.graph:
            self.graph[asal] = [
                (n, d)
                for n, d in self.graph[asal]
                if n != tujuan
            ]

        if tujuan in self.graph:
            self.graph[tujuan] = [
                (n, d)
                for n, d in self.graph[tujuan]
                if n != asal
            ]

    def dijkstra(self, start, end):

        if start not in self.graph or end not in self.graph:
            return [], float("inf")

        distances = {
            city: float("inf")
            for city in self.graph
        }

        previous = {
            city: None
            for city in self.graph
        }

        distances[start] = 0

        pq = [(0, start)]

        while pq:

            current_distance, current_city = heapq.heappop(pq)

            if current_city == end:
                break

            for neighbor, weight in self.graph[current_city]:

                distance = current_distance + weight

                if distance < distances[neighbor]:

                    distances[neighbor] = distance
                    previous[neighbor] = current_city

                    heapq.heappush(
                        pq,
                        (distance, neighbor)
                    )

        path = []
        current = end

        while current:
            path.insert(0, current)
            current = previous[current]

        return path, distances[end]


# =====================================
# FUNGSI
# =====================================

def hitung_biaya(jarak, berat, kendaraan, prioritas):

    tarif = {
        "motor": 1000,
        "mobil": 2000,
        "truk": 3000
    }

    biaya = jarak * tarif[kendaraan]
    biaya += berat * 5000

    if prioritas == "express":
        biaya *= 1.5
    elif prioritas == "same_day":
        biaya *= 2

    return biaya


# =====================================
# DATA JALUR AWAL (PERSISTEN DI SESSION STATE)
# =====================================

jalur_awal = [
    ("Jakarta", "Bandung", 150),
    ("Bandung", "Semarang", 300),
    ("Semarang", "Surabaya", 350),
    ("Jakarta", "Yogyakarta", 500),
    ("Yogyakarta", "Surabaya", 320),
]

if "navigator" not in st.session_state:

    navigator = Graph()

    for a, b, c in jalur_awal:
        navigator.tambah_jalur(a, b, c)

    st.session_state.navigator = navigator

navigator = st.session_state.navigator

# =====================================
# LOGIN
# =====================================

st.title("🚚 Sistem Rute Pengiriman")

if not st.session_state.logged_in:

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if (
            username in users and
            users[username]["password"] == password
        ):

            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users[username]["role"]

            st.success("Login berhasil")
            st.rerun()

        else:
            st.error("Username atau Password salah")

else:

    st.sidebar.success(
        f"Login sebagai {st.session_state.username}"
    )

    # =====================================
    # MENU ADMIN
    # =====================================

    if st.session_state.role == "admin":

        menu = st.sidebar.selectbox(
            "Menu Admin",
            [
                "Tambah Kota",
                "Tambah Jalur",
                "Cari Rute",
                "Kirim Barang",
                "Tracking",
                "Update Status",
                "Statistik",
                "Logout"
            ]
        )

        st.header("Panel Admin")

        if menu == "Tambah Kota":

            kota_baru = st.text_input("Nama Kota Baru")

            if st.button("Tambah Kota"):
                if kota_baru:
                    navigator.tambah_kota(kota_baru)
                    st.success(f"Kota '{kota_baru}' berhasil ditambahkan")
                else:
                    st.warning("Nama kota tidak boleh kosong")

        elif menu == "Tambah Jalur":

            asal = st.text_input("Kota Asal")
            tujuan = st.text_input("Kota Tujuan")
            jarak = st.number_input("Jarak (KM)", min_value=1)

            if st.button("Tambah Jalur"):
                navigator.tambah_jalur(asal, tujuan, jarak)
                st.success("Jalur berhasil ditambahkan")

            st.write("### Graph Saat Ini")
            st.write(navigator.graph)

        elif menu == "Cari Rute":

            if navigator.graph:

                asal = st.selectbox("Kota Asal", list(navigator.graph.keys()))
                tujuan = st.selectbox("Kota Tujuan", list(navigator.graph.keys()))

                if st.button("Cari Rute"):

                    path, jarak = navigator.dijkstra(asal, tujuan)

                    if jarak == float("inf"):
                        st.error("Rute tidak ditemukan")
                    else:
                        st.success(f"Rute: {' -> '.join(path)} | Jarak: {jarak} KM")
            else:
                st.info("Belum ada data kota/jalur")

        elif menu == "Kirim Barang":

            st.subheader("Input Pengiriman Baru")

            if navigator.graph:

                asal = st.selectbox("Kota Asal", list(navigator.graph.keys()), key="kirim_asal")
                tujuan = st.selectbox("Kota Tujuan", list(navigator.graph.keys()), key="kirim_tujuan")
                berat = st.number_input("Berat Barang (KG)", min_value=0.1, value=1.0)
                kendaraan = st.selectbox("Jenis Kendaraan", ["motor", "mobil", "truk"])
                prioritas = st.selectbox("Prioritas", ["reguler", "express", "same_day"])

                if st.button("Kirim Barang"):

                    path, jarak = navigator.dijkstra(asal, tujuan)

                    if jarak == float("inf"):
                        st.error("Rute tidak ditemukan, pengiriman tidak bisa diproses")
                    else:

                        biaya = hitung_biaya(jarak, berat, kendaraan, prioritas)
                        kode = str(uuid.uuid4())[:8]

                        data = {
                            "kode": kode,
                            "tanggal": datetime.now(),
                            "asal": asal,
                            "tujuan": tujuan,
                            "rute": " -> ".join(path),
                            "jarak": jarak,
                            "berat": berat,
                            "kendaraan": kendaraan,
                            "prioritas": prioritas,
                            "biaya": biaya,
                            "status": "Diproses"
                        }

                        st.session_state.pengiriman.append(data)

                        st.success("Pengiriman berhasil dibuat")
                        st.write(f"Kode Pengiriman : **{kode}**")
                        st.write(f"Rute : {' -> '.join(path)}")
                        st.write(f"Jarak : {jarak} KM")
                        st.write(f"Estimasi Biaya : Rp {biaya:,.0f}")
            else:
                st.info("Belum ada data kota/jalur")

        elif menu == "Tracking":

            st.subheader("Lacak Semua Pengiriman")

            if st.session_state.pengiriman:
                st.dataframe(st.session_state.pengiriman)
            else:
                st.info("Belum ada data pengiriman")

        elif menu == "Update Status":

            st.subheader("Update Status Pengiriman")

            if st.session_state.pengiriman:

                kode_list = [p["kode"] for p in st.session_state.pengiriman]
                kode_pilih = st.selectbox("Pilih Kode Pengiriman", kode_list)

                status_baru = st.selectbox(
                    "Status Baru",
                    ["Diproses", "Dikirim", "Dalam Perjalanan", "Selesai", "Dibatalkan"]
                )

                if st.button("Update Status"):
                    for p in st.session_state.pengiriman:
                        if p["kode"] == kode_pilih:
                            p["status"] = status_baru

                    st.success(f"Status pengiriman {kode_pilih} diupdate menjadi {status_baru}")
            else:
                st.info("Belum ada data pengiriman")

        elif menu == "Statistik":

            st.subheader("Statistik Pengiriman")

            if st.session_state.pengiriman:

                total_kiriman = len(st.session_state.pengiriman)
                total_biaya = sum(p["biaya"] for p in st.session_state.pengiriman)
                total_jarak = sum(p["jarak"] for p in st.session_state.pengiriman)

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Pengiriman", total_kiriman)
                col2.metric("Total Pendapatan", f"Rp {total_biaya:,.0f}")
                col3.metric("Total Jarak Tempuh", f"{total_jarak} KM")

                st.write("### Detail Semua Pengiriman")
                st.dataframe(st.session_state.pengiriman)
            else:
                st.info("Belum ada data pengiriman")

        elif menu == "Logout":
            st.session_state.logged_in = False
            st.rerun()

    # =====================================
    # MENU KONSUMEN
    # =====================================

    else:

        st.sidebar.title("Menu Konsumen")

        menu = st.sidebar.selectbox(
            "Pilih",
            ["Cari Rute", "Lacak Pengiriman", "Logout"]
        )

        if menu == "Cari Rute":

            st.header("Cari Rute Pengiriman")

            if navigator.graph:

                asal = st.selectbox("Kota Asal", list(navigator.graph.keys()))
                tujuan = st.selectbox("Kota Tujuan", list(navigator.graph.keys()))
                berat = st.number_input("Berat Barang (KG)", min_value=0.1, value=1.0)
                kendaraan = st.selectbox("Jenis Kendaraan", ["motor", "mobil", "truk"])
                prioritas = st.selectbox("Prioritas", ["reguler", "express", "same_day"])

                if st.button("Cari Rute"):

                    path, jarak = navigator.dijkstra(asal, tujuan)

                    if jarak == float("inf"):
                        st.error("Rute tidak ditemukan")
                    else:

                        biaya = hitung_biaya(jarak, berat, kendaraan, prioritas)
                        kode = str(uuid.uuid4())[:8]

                        data = {
                            "kode": kode,
                            "tanggal": datetime.now(),
                            "asal": asal,
                            "tujuan": tujuan,
                            "rute": " -> ".join(path),
                            "jarak": jarak,
                            "berat": berat,
                            "kendaraan": kendaraan,
                            "prioritas": prioritas,
                            "biaya": biaya,
                            "status": "Diproses"
                        }

                        st.session_state.pengiriman.append(data)

                        st.success("Rute ditemukan & pengiriman dibuat")

                        st.write("### Detail Pengiriman")
                        st.write(f"Kode : {kode}")
                        st.write(f"Rute : {' -> '.join(path)}")
                        st.write(f"Jarak : {jarak} KM")
                        st.write(f"Estimasi Biaya : Rp {biaya:,.0f}")
            else:
                st.info("Belum ada data kota/jalur")

            if st.session_state.pengiriman:
                st.write("### Riwayat Pengiriman Saya")
                st.dataframe(st.session_state.pengiriman)

        elif menu == "Lacak Pengiriman":

            st.header("Lacak Pengiriman")

            kode_cari = st.text_input("Masukkan Kode Pengiriman")

            if st.button("Lacak"):

                hasil = [
                    p for p in st.session_state.pengiriman
                    if p["kode"] == kode_cari
                ]

                if hasil:
                    p = hasil[0]
                    st.success(f"Status: {p['status']}")
                    st.write(f"Rute : {p['rute']}")
                    st.write(f"Jarak : {p['jarak']} KM")
                    st.write(f"Estimasi Biaya : Rp {p['biaya']:,.0f}")
                else:
                    st.error("Kode pengiriman tidak ditemukan")

        elif menu == "Logout":
            st.session_state.logged_in = False
            st.rerun()