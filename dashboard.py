import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .kpi-card {
        background: linear-gradient(135deg, #1d3557 0%, #457B9D 100%);
        border-radius: 14px; padding: 1.1rem 1.3rem;
        color: white; margin-bottom: 0.4rem;
    }
    .kpi-card h2 { margin: 0; font-size: 1.9rem; color: white; }
    .kpi-card p  { margin: 0; font-size: 0.8rem; opacity: 0.85; }
    .section-title { font-size: 1.05rem; font-weight: 700; color: #1d3557; margin-bottom: 0.3rem; }
    .insight-box {
        background: #eaf4fb; border-left: 4px solid #457B9D;
        border-radius: 8px; padding: 0.8rem 1rem; margin-top: 0.5rem;
        font-size: 0.88rem; color: #1d3557;
    }
</style>
""", unsafe_allow_html=True)

# ── Data loader ───────────────────────────────────────────────────────────────
BASE = "."  # atau os.path.dirname(__file__)

@st.cache_data
def load_main():
    df = pd.read_csv(os.path.join(BASE, "main_data.csv"), parse_dates=["order_purchase_timestamp"])
    df["year"]       = df["order_purchase_timestamp"].dt.year
    df["year_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    return df

@st.cache_data
def load_rfm():
    return pd.read_csv(os.path.join(BASE, "rfm_data.csv"))

main = load_main()
rfm  = load_rfm()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🛍️ Olist Dashboard")
st.sidebar.caption("E-Commerce Public Dataset · Brasil 2016–2018")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigasi", [
    "🏠 Overview",
    "📦 Analisis Revenue",
    "🚚 Analisis Pengiriman",
    "👥 RFM Analysis",
])

years = sorted(main["year"].dropna().unique().astype(int))
selected_years = st.sidebar.multiselect("Filter Tahun", years, default=years)
st.sidebar.markdown("---")
st.sidebar.caption("Proyek Analisis Data — Dicoding")

df = main[main["year"].isin(selected_years)].copy()
rfm_f = rfm.copy()   # RFM tidak perlu filter tahun

# ═══════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("🛍️ Olist E-Commerce — Analisis Data Interaktif")
    st.markdown("Dashboard analisis data platform e-commerce Olist Brasil (Oktober 2016 – Oktober 2018).")

    total_orders  = df["order_id"].nunique()
    total_revenue = df["price"].sum()
    avg_score     = df["review_score"].mean()
    pct_ontime    = (df["delay_days"] <= 0).mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    for col, title, val in [
        (c1, "Total Pesanan", f"{total_orders:,}"),
        (c2, "Total Revenue", f"BRL {total_revenue/1e6:.2f}M"),
        (c3, "Avg Review Score", f"{avg_score:.2f} / 5"),
        (c4, "Tepat Waktu", f"{pct_ontime:.1f}%"),
    ]:
        col.markdown(f'<div class="kpi-card"><p>{title}</p><h2>{val}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<p class="section-title">📈 Tren Pesanan Bulanan</p>', unsafe_allow_html=True)
        monthly = df.groupby("year_month")["order_id"].nunique().reset_index().sort_values("year_month")
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.fill_between(range(len(monthly)), monthly["order_id"], alpha=0.25, color="#457B9D")
        ax.plot(range(len(monthly)), monthly["order_id"], color="#457B9D", lw=2.2)
        step = max(1, len(monthly)//8)
        ax.set_xticks(range(0, len(monthly), step))
        ax.set_xticklabels(monthly["year_month"].iloc[::step], rotation=40, ha="right", fontsize=7.5)
        ax.set_ylabel("Jumlah Pesanan"); ax.spines[["top","right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.3); plt.tight_layout(); st.pyplot(fig); plt.close()

    with col_r:
        st.markdown('<p class="section-title">⭐ Distribusi Review Score</p>', unsafe_allow_html=True)
        sc = df["review_score"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(6, 3.5))
        colors = ["#e63946","#f4a261","#e9c46a","#90be6d","#2a9d8f"]
        bars = ax.bar(sc.index, sc.values, color=colors, edgecolor="white", width=0.65)
        for bar, v in zip(bars, sc.values):
            ax.text(bar.get_x()+bar.get_width()/2, v+200, f"{v:,}", ha="center", fontsize=8)
        ax.set_xlabel("Review Score"); ax.set_ylabel("Jumlah Ulasan")
        ax.spines[["top","right"]].set_visible(False); ax.grid(axis="y", alpha=0.3)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Volume pesanan tumbuh secara konsisten '
                'sejak awal 2017 dengan puncak di <b>November 2017</b> (Black Friday Brasil). '
                'Sekitar <b>57% ulasan</b> pelanggan memberi skor maksimal 5 bintang.</div>',
                unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# ANALISIS REVENUE
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📦 Analisis Revenue":
    st.title("📦 Analisis Revenue per Kategori Produk")
    st.markdown(
        "> **Pertanyaan Bisnis 1:** Kategori produk apa yang menghasilkan total revenue tertinggi "
        "dan bagaimana tren pendapatannya secara bulanan dari Oktober 2016 hingga Oktober 2018?"
    )

    cat_rev = (
        df.groupby("product_category_name_english")["price"]
          .sum().sort_values(ascending=False)
          .reset_index().rename(columns={"price":"total_revenue"})
    )
    total_rev_all = cat_rev["total_revenue"].sum()
    cat_rev["share_%"] = cat_rev["total_revenue"] / total_rev_all * 100

    n_top = st.slider("Tampilkan Top-N Kategori", 5, 20, 10)
    top_n = cat_rev.head(n_top)
    top5  = cat_rev.head(5)["product_category_name_english"].tolist()

    col1, col2 = st.columns([1.15, 0.85])

    with col1:
        st.markdown(f'<p class="section-title">Top {n_top} Kategori — Total Revenue</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(7.5, max(4.5, n_top*0.52)))
        palette = ["#E63946" if i==0 else "#457B9D" if i<5 else "#A8DADC" for i in range(n_top)]
        bars = ax.barh(top_n["product_category_name_english"][::-1],
                       top_n["total_revenue"][::-1], color=palette[::-1], edgecolor="white")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"BRL {x/1e3:.0f}K"))
        for bar, (_, row) in zip(bars, top_n[::-1].iterrows()):
            ax.text(row["total_revenue"] + top_n["total_revenue"].max()*0.01,
                    bar.get_y()+bar.get_height()/2,
                    f"BRL {row['total_revenue']/1e3:.0f}K  ({row['share_%']:.1f}%)",
                    va="center", fontsize=7.5)
        ax.set_xlim(0, top_n["total_revenue"].max()*1.22)
        ax.spines[["top","right"]].set_visible(False); ax.grid(axis="x", alpha=0.3)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with col2:
        st.markdown('<p class="section-title">Tabel Revenue Top 10</p>', unsafe_allow_html=True)
        display_df = cat_rev.head(10).copy()
        display_df["total_revenue"] = display_df["total_revenue"].map("BRL {:,.0f}".format)
        display_df["share_%"]       = display_df["share_%"].map("{:.1f}%".format)
        display_df.columns = ["Kategori", "Revenue", "Share"]
        st.dataframe(display_df, use_container_width=True, height=375)

    st.markdown("---")
    st.markdown('<p class="section-title">📈 Tren Revenue Bulanan</p>', unsafe_allow_html=True)

    sel_cats = st.multiselect("Pilih kategori:", cat_rev["product_category_name_english"].tolist(), default=top5)
    if sel_cats:
        monthly = (
            df[df["product_category_name_english"].isin(sel_cats)]
            .groupby(["year_month","product_category_name_english"])["price"]
            .sum().reset_index().sort_values("year_month")
        )
        fig, ax = plt.subplots(figsize=(12, 4))
        for i, cat in enumerate(sel_cats):
            d = monthly[monthly["product_category_name_english"]==cat]
            ax.plot(d["year_month"], d["price"]/1000, marker="o", markersize=3.5,
                    lw=2, label=cat.replace("_"," ").title(),
                    color=sns.color_palette("tab10", len(sel_cats))[i])
        unique_months = sorted(monthly["year_month"].unique())
        step = max(1, len(unique_months)//10)
        ax.set_xticks(range(0, len(unique_months), step))
        ax.set_xticklabels(unique_months[::step], rotation=40, ha="right", fontsize=8)
        ax.set_ylabel("Revenue (BRL Ribu)"); ax.grid(alpha=0.25)
        ax.legend(fontsize=8, bbox_to_anchor=(1.01,1), loc="upper left")
        ax.spines[["top","right"]].set_visible(False); plt.tight_layout()
        st.pyplot(fig); plt.close()

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> <b>health_beauty</b> dan '
                '<b>watches_gifts</b> secara konsisten mendominasi revenue. Lonjakan '
                '<b>November 2017</b> (Black Friday) terlihat di hampir semua kategori — '
                'peluang besar untuk kampanye seasonal.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# ANALISIS PENGIRIMAN
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🚚 Analisis Pengiriman":
    st.title("🚚 Keterlambatan Pengiriman vs Kepuasan Pelanggan")
    st.markdown(
        "> **Pertanyaan Bisnis 2:** Bagaimana hubungan antara keterlambatan pengiriman (delay hari) "
        "terhadap rata-rata review score pelanggan pada pesanan delivered di platform Olist 2017–2018?"
    )

    delay_df = df.dropna(subset=["review_score","delay_days"]).copy()
    pct_late  = (delay_df["delay_days"] > 0).mean() * 100
    avg_delay = delay_df[delay_df["delay_days"]>0]["delay_days"].mean()
    corr      = delay_df["delay_days"].corr(delay_df["review_score"])
    avg_ontime = delay_df[delay_df["delay_days"]<=0]["review_score"].mean()
    avg_late   = delay_df[delay_df["delay_days"]>0]["review_score"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("% Terlambat",        f"{pct_late:.1f}%")
    c2.metric("Avg Delay Terlambat",f"{avg_delay:.1f} hari")
    c3.metric("Korelasi (r)",       f"{corr:.3f}")
    c4.metric("Score: Tepat vs Telat", f"{avg_ontime:.2f} vs {avg_late:.2f}")

    st.markdown("---")

    delay_df["delay_category"] = pd.cut(
        delay_df["delay_days"],
        bins=[-np.inf,-7,-3,0,3,7,14,np.inf],
        labels=["≤-7 hari","-7~-3 hari","-3~0 hari","0~3 hari","3~7 hari","7~14 hari",">14 hari"]
    )
    delay_agg = (
        delay_df.groupby("delay_category", observed=True)["review_score"]
        .agg(avg_score="mean", n="count").reset_index()
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">Avg Review Score per Kategori Delay</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(7,4.5))
        bar_c = ["#2a9d8f" if "≤" in str(c) or "-" in str(c)
                 else "#f4a261" if "0~3" in str(c)
                 else "#e76f51" for c in delay_agg["delay_category"]]
        bars = ax.bar(delay_agg["delay_category"], delay_agg["avg_score"],
                      color=bar_c, edgecolor="white", width=0.65)
        ax.axhline(delay_df["review_score"].mean(), color="#264653", ls="--", lw=1.5,
                   label=f"Rata-rata ({delay_df['review_score'].mean():.2f})")
        for bar, (_, r) in zip(bars, delay_agg.iterrows()):
            ax.text(bar.get_x()+bar.get_width()/2, r["avg_score"]+0.06,
                    f"{r['avg_score']:.2f}\n(n={r['n']:,})", ha="center", va="bottom", fontsize=7)
        ax.set_ylim(0, 5.8); ax.tick_params(axis="x", rotation=30)
        ax.set_ylabel("Avg Review Score"); ax.legend(fontsize=8.5)
        ax.spines[["top","right"]].set_visible(False); ax.grid(axis="y", alpha=0.3)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with col2:
        st.markdown('<p class="section-title">Scatter: Delay vs Review Score</p>', unsafe_allow_html=True)
        samp = delay_df[delay_df["delay_days"].between(-30,45)].sample(min(4000, len(delay_df)), random_state=42)
        fig, ax = plt.subplots(figsize=(7,4.5))
        ax.scatter(samp["delay_days"], samp["review_score"], alpha=0.08, s=10, color="#457B9D")
        m,b = np.polyfit(delay_df["delay_days"], delay_df["review_score"], 1)
        x_  = np.linspace(-30, 45, 100)
        ax.plot(x_, m*x_+b, color="#E63946", lw=2.5, label=f"Regresi linier (r={corr:.3f})")
        ax.axvline(0, color="gray", ls="--", alpha=0.5)
        ax.axvline(3, color="#f4a261", ls=":", lw=2, label="Batas kritis (3 hari)")
        ax.set_xlabel("Delay (hari)"); ax.set_ylabel("Review Score"); ax.set_yticks([1,2,3,4,5])
        ax.legend(fontsize=8.5); ax.spines[["top","right"]].set_visible(False); ax.grid(alpha=0.2)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    st.warning("⚠️ **Titik Kritis:** Delay **> 3 hari** menyebabkan skor rata-rata turun drastis "
               "dari **3.77 → 2.32**. Tim logistik perlu menjaga delay di bawah ambang ini.")
    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Korelasi negatif (r = '
                f'{corr:.3f}) mengonfirmasi bahwa semakin lama keterlambatan, semakin rendah '
                'kepuasan pelanggan. <b>76%</b> pesanan berhasil dikirim tepat atau lebih cepat '
                'dari estimasi — ini aset utama platform Olist.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# RFM ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "👥 RFM Analysis":
    st.title("👥 RFM Analysis — Segmentasi Pelanggan")
    st.markdown(
        "**Analisis Lanjutan:** RFM (Recency, Frequency, Monetary) digunakan untuk "
        "mengelompokkan pelanggan berdasarkan perilaku pembelian mereka — "
        "kapan terakhir membeli, seberapa sering, dan berapa total pengeluarannya."
    )

    seg_cnt  = rfm_f["Segment"].value_counts().reset_index()
    seg_cnt.columns = ["Segment","Count"]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">Distribusi Segmen Pelanggan</p>', unsafe_allow_html=True)
        seg_colors = {
            "Champions":          "#2a9d8f",
            "Loyal Customers":    "#457B9D",
            "Potential Loyalists":"#A8DADC",
            "Recent Customers":   "#e9c46a",
            "At Risk":            "#f4a261",
            "Lost":               "#e63946",
        }
        colors = [seg_colors.get(s,"#999") for s in seg_cnt["Segment"]]
        fig, ax = plt.subplots(figsize=(7, 4.5))
        bars = ax.barh(seg_cnt["Segment"], seg_cnt["Count"], color=colors, edgecolor="white")
        for bar, (_, r) in zip(bars, seg_cnt.iterrows()):
            pct = r["Count"] / seg_cnt["Count"].sum() * 100
            ax.text(r["Count"]+300, bar.get_y()+bar.get_height()/2,
                    f"{r['Count']:,}  ({pct:.1f}%)", va="center", fontsize=8)
        ax.set_xlim(0, seg_cnt["Count"].max()*1.22)
        ax.set_xlabel("Jumlah Pelanggan")
        ax.spines[["top","right"]].set_visible(False); ax.grid(axis="x", alpha=0.3)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with col2:
        st.markdown('<p class="section-title">Statistik RFM per Segmen</p>', unsafe_allow_html=True)
        rfm_stats = rfm_f.groupby("Segment")[["Recency","Frequency","Monetary"]].mean().round(1)
        rfm_stats["Monetary"] = rfm_stats["Monetary"].map("BRL {:.1f}".format)
        rfm_stats.index.name = "Segmen"
        st.dataframe(rfm_stats, use_container_width=True, height=270)

        st.markdown("""
| Segmen | Deskripsi |
|---|---|
| **Champions** | Baru beli, sering, pengeluaran besar |
| **Loyal Customers** | Sering beli, nilai tinggi |
| **Potential Loyalists** | Cukup aktif, potensi besar |
| **Recent Customers** | Baru bergabung, perlu nurturing |
| **At Risk** | Dulu aktif, kini mulai pergi |
| **Lost** | Sudah lama tidak bertransaksi |
""")

    st.markdown("---")
    st.markdown('<p class="section-title">📊 Distribusi RFM Score</p>', unsafe_allow_html=True)

    col3, col4, col5 = st.columns(3)
    for col, metric, color, label in [
        (col3, "Recency",   "#e63946", "Recency (hari)"),
        (col4, "Frequency", "#457B9D", "Frequency (transaksi)"),
        (col5, "Monetary",  "#2a9d8f", "Monetary (BRL)"),
    ]:
        with col:
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.hist(rfm_f[metric].clip(upper=rfm_f[metric].quantile(0.99)),
                    bins=30, color=color, alpha=0.8, edgecolor="white")
            ax.set_title(label, fontsize=9, fontweight="bold")
            ax.set_xlabel(label, fontsize=8); ax.set_ylabel("Frekuensi", fontsize=8)
            ax.spines[["top","right"]].set_visible(False); ax.grid(axis="y", alpha=0.3)
            plt.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown('<div class="insight-box">💡 <b>Insight RFM:</b> Segmen <b>At Risk</b> '
                '(24%) adalah prioritas utama — pelanggan ini pernah aktif namun mulai menjauh. '
                'Program <b>win-back campaign</b> berupa voucher eksklusif dapat memulihkan mereka. '
                'Sementara <b>Champions</b> (16%) perlu dipertahankan dengan program loyalitas '
                'premium untuk menjaga revenue utama platform.</div>', unsafe_allow_html=True)
