import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ✅ Page Config
st.set_page_config(page_title="Zomato Dashboard", layout="wide")

# 🎨 Theme toggle
theme = st.sidebar.radio("🌓 Select Theme", ["Light", "Dark"])

if theme == "Dark":
    plt.style.use("dark_background")
    sns.set_theme(style="darkgrid")
    st.markdown("""
        <style>
        body, .stApp {
            background-color: #0E1117;
            color: white;
        }
        .block-container {
            background-color: #0E1117;
            color: white;
        }
        [data-testid="metric-container"] {
            background-color: #1c1f26;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 16px;
            margin: 10px 5px;
            box-shadow: 0 0 5px rgba(255,255,255,0.05);
        }
        [data-testid="metric-container"] > div {
            justify-content: center;
        }
        @media only screen and (max-width: 768px) {
            [data-testid="metric-container"] {
                width: 100% !important;
                margin-bottom: 12px;
            }
        }
        </style>
    """, unsafe_allow_html=True)
else:
    sns.set_theme(style="whitegrid")

# 🏠 Title
st.markdown("<h1 style='text-align: center;'>🍴 Zomato Restaurant Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

try:
    df = pd.read_csv("zomato_sample.csv")

    # 🔍 Data Cleaning
    df['rate'] = df['rate'].astype(str).str.replace("/5", "").replace(["NEW", "-"], None)
    df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
    df['votes'] = pd.to_numeric(df['votes'], errors='coerce')
    df.rename(columns={"approx_cost(for two people)": "cost"}, inplace=True)
    df['cost'] = df['cost'].astype(str).str.replace(",", "")
    df['cost'] = pd.to_numeric(df['cost'], errors='coerce')
    df = df.dropna(subset=["cost"])
    df['rate'] = df['rate'].fillna(0)
    df['votes'] = df['votes'].fillna(0)

    # 📂 Sidebar Filters
    st.sidebar.header("📂 Filter Options")
    selected_type = st.sidebar.multiselect(
        "Restaurant Type:",
        options=df["listed_in(type)"].dropna().unique(),
        default=df["listed_in(type)"].dropna().unique()
    )
    rating_range = st.sidebar.slider("⭐ Rating Range", 0.0, 5.0,
                                     (float(df['rate'].min()), float(df['rate'].max())), step=0.1)
    votes_range = st.sidebar.slider("🗳️ Votes Range", int(df['votes'].min()), int(df['votes'].max()),
                                    (int(df['votes'].min()), int(df['votes'].max())))
    cost_range = st.sidebar.slider("💰 Cost for Two", int(df['cost'].min()), int(df['cost'].max()),
                                   (int(df['cost'].min()), int(df['cost'].max())))
    search_query = st.sidebar.text_input("🔍 Search by Restaurant Name")

    # ✅ Apply filters
    filtered_df = df[
        (df["listed_in(type)"].isin(selected_type)) &
        (df["rate"].between(*rating_range)) &
        (df["votes"].between(*votes_range)) &
        (df["cost"].between(*cost_range))
    ]
    if search_query:
        filtered_df = filtered_df[filtered_df["name"].str.contains(search_query, case=False, na=False)]

    # 🔍 Advanced Search Result Viewer
    # 🔍 Advanced Search Result Viewer
    # 🔍 Advanced Search Result Viewer
    if search_query:
        st.markdown("### 🔍 Search Result")
        matched = df[df["name"].str.contains(search_query, case=False, na=False)]
        if not matched.empty:
            for idx, row in matched.iterrows():
                with st.expander(f"📌 {row['name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**🍽️ Type:** {row.get('listed_in(type)', 'N/A')}")
                        st.write(f"**📍 Location:** {row.get('location', 'N/A')}")
                        st.write(f"**⭐ Rating:** {row.get('rate', 'N/A')}")
                        st.write(f"**👥 Votes:** {int(row.get('votes', 0))}")
                        st.write(f"**💰 Cost for Two:** ₹{int(row.get('cost', 0))}")
                    with col2:
                        st.write(f"**🛵 Online Delivery:** {row.get('online_order', 'N/A')}")
                        st.write(f"**📅 Table Booking:** {row.get('book_table', 'N/A')}")
                        st.write(f"**📞 Phone:** {row.get('phone', 'Not Available')}")
        else:
            st.warning("❌ No matching restaurants found.")

    # ✨ KPI Cards
    col1, col2, col3 = st.columns(3)
    col1.metric("📈 Avg Rating", f"{filtered_df['rate'].mean():.2f}")
    col2.metric("👥 Total Votes", int(filtered_df['votes'].sum()))
    col3.metric("💸 Avg Cost", f"₹{int(filtered_df['cost'].mean())}")

    col4, col5, col6 = st.columns(3)
    col4.metric("💎 Max Cost", f"₹{int(filtered_df['cost'].max())}")
    col5.metric("🪙 Min Cost", f"₹{int(filtered_df['cost'].min())}")
    col6.metric("🍽️ Restaurants Shown", len(filtered_df))

    st.markdown("<br>", unsafe_allow_html=True)

    # 🏆 Top Rated Restaurants
    st.subheader("🏆 Top 10 Rated Restaurants")
    col7, col8 = st.columns([1, 2])
    top_rated = filtered_df.sort_values(by="rate", ascending=False).dropna(subset=["rate"]).head(15)
    with col7:
        st.dataframe(top_rated[["name", "rate"]].reset_index(drop=True), use_container_width=True)
    with col8:
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        sns.barplot(data=top_rated, y="name", x="rate", hue="name", dodge=False, palette="coolwarm", legend=False, ax=ax1)
        ax1.set_title("Top 10 Restaurants")
        st.pyplot(fig1)

    # 📊 Type Distribution + Votes
    st.subheader("📊 Restaurant Type Distribution")
    col9, col10 = st.columns(2)
    with col9:
        type_counts = filtered_df["listed_in(type)"].value_counts().head(6)
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        ax2.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', startangle=140)
        ax2.axis('equal')
        st.pyplot(fig2)
    with col10:
        top_votes = filtered_df.sort_values(by="votes", ascending=False).dropna(subset=["votes"]).head(10)
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        sns.barplot(data=top_votes, y="name", x="votes", hue="name", palette="viridis", legend=False, ax=ax3)
        ax3.set_title("Top 10 Most Voted Restaurants")
        st.pyplot(fig3)

    # 💸 Votes vs Cost
    st.subheader("💸 Votes vs Cost for Two")
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        data=filtered_df,
        x="cost",
        y="votes",
        hue="listed_in(type)",
        palette="tab10",
        alpha=0.7,
        ax=ax4
    )
    ax4.set_title("Votes vs Cost")
    ax4.set_xlabel("Approx Cost for Two")
    ax4.set_ylabel("Votes")
    st.pyplot(fig4)

    # 💎 Top Costly Restaurants
    st.subheader("💎 Top 15 Most Expensive Restaurants")
    top_costly = df[["name", "cost"]].sort_values(by="cost", ascending=False).dropna().head(15)
    fig5, ax5 = plt.subplots(figsize=(12, 5))
    ax5.plot(top_costly["name"], top_costly["cost"], marker='o', color='teal')
    ax5.set_title("Top 15 Restaurants by Approximate Cost")
    ax5.set_ylabel("Approx Cost (for two people)")
    ax5.set_xticks(range(len(top_costly)))
    ax5.set_xticklabels(top_costly["name"])
    ax5.tick_params(axis='x', rotation=45)
    ax5.grid(True)
    st.pyplot(fig5)

    # 🖊️ Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center;'>👨‍💻 Made by <b>Saurabh Papaa Sharma</b> | 📍 Mathura</p>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Error loading data: {e}")