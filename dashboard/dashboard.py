import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Konfigurasi Tampilan
st.set_page_config(page_title="Analisis Penyewaan Sepeda", layout="wide")

# Load Dataset
@st.cache_data
def load_data():
    # Cek apakah path pertama tersedia
    hour_path = "../data/hour.csv" if os.path.exists("../data/hour.csv") else "data/hour.csv"
    day_path = "../data/day.csv" if os.path.exists("../data/day.csv") else "data/day.csv"
    
    df_hour = pd.read_csv(hour_path)  # Dataset per jam
    df_day = pd.read_csv(day_path)    # Dataset per hari
    return df_hour, df_day

df_hour, df_day = load_data()


# Data Preprocessing
df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])
df_day['dteday'] = pd.to_datetime(df_day['dteday'])

# Mapping nama hari
day_map = {0: "Minggu", 1: "Senin", 2: "Selasa", 3: "Rabu", 
           4: "Kamis", 5: "Jumat", 6: "Sabtu"}

df_hour['weekday'] = df_hour['weekday'].map(day_map)
df_day['weekday'] = df_day['weekday'].map(day_map)

# Tabel proporsi user
users_frequency_prop = df_hour[['casual', 'registered']].sum() / df_hour['cnt'].sum()
users_frequency_prop = users_frequency_prop.to_frame().rename(columns={0: 'Proportion'})

unique_users_count = df_hour[['casual', 'registered']].nunique()
unique_users_prop = unique_users_count / unique_users_count.sum()
unique_users_prop = unique_users_prop.to_frame().rename(columns={0: 'Proportion'})

# Mapping angka ke nama musim
season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
df_hour["season_label"] = df_hour["season"].map(season_mapping)
df_day["season_label"] = df_day["season"].map(season_mapping)

# Sidebar Navigation
st.sidebar.markdown("<h1 style='color: darkblue; font-weight: bold;'>Dashboard Penyewaan Sepeda</h1>", unsafe_allow_html=True)
st.sidebar.markdown("##### Made by: Putri Sekar Ayu")

# Filter di Sidebar
st.sidebar.subheader("🎛 Filter Data")

# Pilih Rentang Tanggal
selected_dates = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    [df_day['dteday'].min(), df_day['dteday'].max()],
    min_value=df_day['dteday'].min(),
    max_value=df_day['dteday'].max()
)

# Pilih Musim
selected_season = st.sidebar.multiselect(
    "Pilih Musim",
    df_day['season_label'].unique(),
    default=df_day['season_label'].unique()
)

# Filter data berdasarkan input
filtered_df = df_day[
    (df_day['dteday'] >= pd.Timestamp(selected_dates[0])) & 
    (df_day['dteday'] <= pd.Timestamp(selected_dates[1])) & 
    (df_day['season_label'].isin(selected_season))
]

# UI dengan Tabs
tab1, tab2, tab3 = st.tabs(["Penyewaan Sepeda", "Statistik Pengguna", "Analisis Cuaca"])

with tab1:
    # Header
    st.subheader("📅 Data Penyewaan Sepeda (Harian)")

    # Hitung rata-rata penyewaan per hari setelah filter
    grouped_df = filtered_df.groupby("weekday", observed=False)["cnt"].mean().reset_index()

    # Urutkan sesuai urutan hari
    ordered_days = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    grouped_df["weekday"] = pd.Categorical(grouped_df["weekday"], categories=ordered_days, ordered=True)
    grouped_df = grouped_df.sort_values(by="weekday")

    # Temukan nilai maksimum berdasarkan data yang tersedia
    max_value = grouped_df["cnt"].max()

    # Warna bar: Highlight hanya untuk nilai maksimum yang tersedia
    colors = ["#87CEEB" if cnt != max_value else "#003f5c" for cnt in grouped_df["cnt"]]

    # Visualisasi dengan bar plot
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=grouped_df, x="weekday", y="cnt", ax=ax, palette=colors)

    # Tambahkan label di atas bar dengan posisi yang benar
    for bar, (_, row) in zip(ax.patches, grouped_df.iterrows()):
        value = round(row["cnt"], 2) if row["cnt"] % 1 != 0 else int(row["cnt"])  # Format angka
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # Posisi tengah bar
            bar.get_height() + (max_value)*0.005, # Label diatas bar 
            str(value),
            ha='center', va='bottom', fontsize=9, fontweight='bold', color='black'
        )

    # Judul & Label
    ax.set_title("Rata-rata Penyewaan Sepeda per Hari dalam Seminggu", fontsize=14, fontweight="bold")
    ax.set_ylabel("Jumlah Penyewaan", fontsize=12)
    ax.set_xlabel("")

    # Tampilkan grafik di Streamlit
    st.pyplot(fig)

    st.markdown("<br>", unsafe_allow_html=True)
    

    st.subheader("🕒 Trend Penyewaan Sepeda Berdasarkan Jam")

    # Filter data berdasarkan rentang tanggal dan musim yang dipilih
    filtered_hour_df = df_hour[
        (df_hour["dteday"] >= pd.Timestamp(selected_dates[0])) &
        (df_hour["dteday"] <= pd.Timestamp(selected_dates[1])) &
        (df_hour["season_label"].isin(selected_season))
    ]

    # Menghitung rata-rata penyewaan per jam
    grouped_hour_df = filtered_hour_df.groupby("hr")["cnt"].mean().reset_index()

    # Visualisasi dengan Line Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=grouped_hour_df, x="hr", y="cnt", marker="o", ax=ax, color="royalblue")

    # Judul & Label
    ax.set_title(" Tren Rata-rata Penyewaan Sepeda per Jam", fontsize=14, fontweight="bold")
    ax.set_xlabel("Jam", fontsize=12)
    ax.set_ylabel("Jumlah Penyewaan (Rata-rata)", fontsize=12)
    ax.set_xticks(range(0, 24))
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Tampilkan plot di Streamlit
    st.pyplot(fig)


with tab2:
    st.subheader("📊 Tren Jumlah Pengguna per Jam")

    st.markdown("##### 👥 Perbandingan Casual vs Registered Users")
    st.markdown("<br>", unsafe_allow_html=True)

    # Filter data berdasarkan tanggal & musim yang dipilih
    filtered_hour_df = df_hour[
        (df_hour["dteday"] >= pd.Timestamp(selected_dates[0])) &
        (df_hour["dteday"] <= pd.Timestamp(selected_dates[1])) &
        (df_hour["season_label"].isin(selected_season))
    ]

    # Tabel proporsi user berdasarkan filter
    users_frequency_prop = filtered_hour_df[['casual', 'registered']].sum() / filtered_hour_df['cnt'].sum()
    users_frequency_prop = users_frequency_prop.to_frame().rename(columns={0: 'Proportion'})

    unique_users_count = filtered_hour_df[['casual', 'registered']].nunique()
    unique_users_prop = unique_users_count / unique_users_count.sum()
    unique_users_prop = unique_users_prop.to_frame().rename(columns={0: 'Proportion'})

    # Warna Pie Chart
    colors = ['#FFAA33', '#3399FF']
    edge_color = '#444444'

    col1, col2 = st.columns(2)

    with col1:
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax1.pie(unique_users_prop.squeeze(), labels=['Casual Users', 'Registered Users'], 
                                           autopct='%1.1f%%', colors=colors, startangle=140, 
                                           wedgeprops={'edgecolor': edge_color, 'linewidth': 1.2})
        ax1.set_title('Perbandingan Jumlah Casual dan Registered Users', fontsize=12, fontweight='bold')
        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax2.pie(users_frequency_prop.squeeze(), labels=['Casual Users', 'Registered Users'], 
                                           autopct='%1.1f%%', colors=colors, startangle=140, 
                                           wedgeprops={'edgecolor': edge_color, 'linewidth': 1.2})
        ax2.set_title('Frekuensi Penyewaan Sepeda oleh Casual vs Registered Users', fontsize=12, fontweight='bold')
        st.pyplot(fig2)

    with st.expander("📌 **Rangkuman Grafik**", expanded=True):
        st.markdown(f"""
        Berdasarkan rentang tanggal **{selected_dates[0]} - {selected_dates[1]}** dan musim **{', '.join(selected_season)}**,  
        - **{round(unique_users_prop.loc['registered', 'Proportion'] * 100, 1)}%** dari seluruh pengguna adalah **Registered Users**.  
        - **{round(users_frequency_prop.loc['registered', 'Proportion'] * 100, 1)}%** dari total penyewaan dilakukan oleh **Registered Users**.  
        """)


with tab3:
    st.subheader("⛅ Analisis Pengaruh Cuaca terhadap Pengguna")

    # Filter Data Sesuai Pilihan Pengguna
    filtered_df = df_day[
        (df_day['dteday'] >= pd.Timestamp(selected_dates[0])) & 
        (df_day['dteday'] <= pd.Timestamp(selected_dates[1])) & 
        (df_day["season_label"].isin(selected_season))
    ].copy()

    # Kategorisasi Suhu
    bins = [0, 0.366, 0.732, 1]  # Rentang normalisasi (0-1)
    labels = ["Dingin (<15°C)", "Sedang (15-30°C)", "Ekstrem (>30°C)"]

    filtered_df["temp_category"] = pd.cut(filtered_df["temp"], bins=bins, labels=labels, include_lowest=True)

    # Hitung jumlah rata-rata penyewaan sepeda per kategori suhu
    temp_counts = filtered_df.groupby("temp_category")["cnt"].mean().sort_index()

    # Menentukan kategori suhu dengan penyewaan tertinggi
    highlight_index = temp_counts.idxmax()

    # Buat daftar warna untuk highlight kategori tertinggi
    bar_colors = ["lightblue" if category != highlight_index else "darkblue" for category in temp_counts.index]

    # Buat visualisasi
    fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=100)
    sns.barplot(x=temp_counts.index, y=temp_counts.values, palette=bar_colors, edgecolor="black", ax=ax, errorbar=None, width=0.5)
    
    # Tambahkan judul, label, x axis, y axis
    ax.set_title("Rata-rata Penyewaan Sepeda berdasarkan Kategori Suhu", fontsize=9, fontweight="bold")

    ax.set_xticklabels(ax.get_xticklabels(), fontsize=4)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=4)

    ax.set_xlabel("")
    ax.set_ylabel("Rata-rata Penyewaan", fontsize=6)

    # Tampilkan di Streamlit
    st.pyplot(fig, use_container_width=False)

    # Penjelasan kategori suhu
    with st.expander("ℹ️ **Penjelasan Kategori Suhu**", expanded=True):
        st.write("""
        Suhu dalam dataset telah dinormalisasi dalam rentang **0–1** berdasarkan nilai maksimum **40°C**.  
        Untuk analisis ini, suhu dikategorikan sebagai berikut:

        - **Dingin**: Suhu < **15°C** (`temp_normalized * 40 < 15`)  
        - **Sedang**: Suhu **15°C – 30°C** (`15 ≤ temp_normalized * 40 ≤ 30`)  
        - **Ekstrem**: Suhu > **30°C** (`temp_normalized * 40 > 30`)  
        """)

    # Rangkuman hasil analisis
    with st.expander("📌 **Rangkuman Grafik**", expanded=True):
        max_category = highlight_index if highlight_index else "tidak ada data yang tersedia"
        st.markdown(f"""
        - Penyewaan sepeda terbanyak terjadi pada kategori suhu **{max_category}**.
        - Hasil ini didasarkan pada rentang waktu dan musim yang telah dipilih.
        """)

