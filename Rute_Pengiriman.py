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
# DATA JALUR AWAL
# =====================================

g = Graph()

g.tambah_jalur("Jakarta", "Bandung", 150)
g.tambah_jalur("Bandung", "Semarang", 300)
g.tambah_jalur("Semarang", "Surabaya", 350)
g.tambah_jalur("Jakarta", "Yogyakarta", 500)
g.tambah_jalur("Yogyakarta", "Surabaya", 320)

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

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # =====================================
    # MENU ADMIN
    # =====================================

    if st.session_state.role == "admin":

        st.header("Panel Admin")

        menu = st.selectbox(
            "Pilih Menu",
            [
                "Tambah Jalur",
                "Hapus Jalur",
                "Lihat Graph"
            ]
        )

        if menu == "Tambah Jalur":

            asal = st.text_input("Kota Asal")
            tujuan = st.text_input("Kota Tujuan")
            jarak = st.number_input(
                "Jarak (KM)",
                min_value=1
            )

            if st.button("Tambah"):

                g.tambah_jalur(
                    asal,
                    tujuan,
                    jarak
                )

                st.success("Jalur berhasil ditambahkan")

        elif menu == "Hapus Jalur":

            asal = st.text_input("Asal")
            tujuan = st.text_input("Tujuan")

            if st.button("Hapus"):

                g.hapus_jalur(
                    asal,
                    tujuan
                )

                st.success("Jalur berhasil dihapus")

        elif menu == "Lihat Graph":

            st.write(g.graph)

    # =====================================
    # MENU KONSUMEN
    # =====================================

    else:

        st.header("Cari Rute Pengiriman")

        asal = st.selectbox(
            "Kota Asal",
            list(g.graph.keys())
        )

        tujuan = st.selectbox(
            "Kota Tujuan",
            list(g.graph.keys())
        )

        if st.button("Cari Rute"):

            path, jarak = g.dijkstra(
                asal,
                tujuan
            )

            if jarak == float("inf"):
                st.error("Rute tidak ditemukan")
            else:

                kode = str(uuid.uuid4())[:8]

                data = {
                    "kode": kode,
                    "tanggal": datetime.now(),
                    "asal": asal,
                    "tujuan": tujuan,
                    "rute": " -> ".join(path),
                    "jarak": jarak
                }

                st.session_state.pengiriman.append(data)

                st.success("Rute ditemukan")

                st.write("### Detail Pengiriman")
                st.write(f"Kode : {kode}")
                st.write(f"Rute : {' -> '.join(path)}")
                st.write(f"Jarak : {jarak} KM")

        if st.session_state.pengiriman:

            st.write("### Riwayat Pengiriman")

            st.dataframe(
                st.session_state.pengiriman
            )