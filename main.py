import streamlit as st
import pandas as pd
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# 载入 .env 文件
load_dotenv()

# 连接 MongoDB
def connect_mongodb():
    uri = os.getenv("MONGO_URI")  # 从 .env 获取连接字符串
    return MongoClient(uri)

@st.cache_data
def load_data():
    client = connect_mongodb()
    db = client["Organization6"]

    jobs = list(db["Jobs"].find())
    small_jobs = list(db["SmallJobs"].find())

    def normalize(entry, category):
        return {
            "Name": entry.get("name", ""),
            "Homepage": entry.get("homepage_url", ""),
            "Job Links": entry.get("job_links", []),
            "Address": entry.get("address", ""),
            "Staff Count": entry.get("staff_count", ""),
            "Industry": entry.get("industry", ""),
            "Ticker": entry.get("ticker", ""),
            "Ownership Type": entry.get("ownership_type", ""),
            "Sales (USD)": entry.get("sales_usd", ""),
            "Description": entry.get("business_description", ""),
            "Category": category
        }

    all_data = [normalize(doc, "Large") for doc in jobs] + \
               [normalize(doc, "Small") for doc in small_jobs]
    df = pd.DataFrame(all_data)
    df = df.sort_values("Name")
    return df

def main():
    st.set_page_config(page_title="Company Job Explorer", layout="wide")
    st.title("📊 Collected Companies with Job Links")

    df = load_data()

    with st.sidebar:
        st.header("🔍 Filters")
        category = st.selectbox("Company Size", ["All", "Large", "Small"])
        industry = st.multiselect("Industry", options=sorted(df["Industry"].dropna().unique()))

    filtered = df.copy()
    if category != "All":
        filtered = filtered[filtered["Category"] == category]
    if industry:
        filtered = filtered[filtered["Industry"].isin(industry)]

    st.markdown(f"### Showing **{len(filtered)}** companies")

    for _, row in filtered.iterrows():
        with st.expander(f"🔹 {row['Name']} — {row['Industry']} ({row['Category']})"):
            st.markdown(f"**Homepage**: [{row['Homepage']}]({row['Homepage']})", unsafe_allow_html=True)
            st.markdown(f"**Address**: {row['Address']}")
            st.markdown(f"**Staff Count**: {row['Staff Count']}")
            st.markdown(f"**Ownership Type**: {row['Ownership Type']}")
            st.markdown(f"**Ticker**: `{row['Ticker']}`")
            st.markdown(f"**Sales (USD)**: {row['Sales (USD)']}")
            st.markdown(f"**Description**:\n{row['Description']}", unsafe_allow_html=True)

            st.markdown("**Job Links:**")
            if row["Job Links"]:
                for link in row["Job Links"]:
                    st.markdown(f"- 🔗 [{link}]({link})", unsafe_allow_html=True)
            else:
                st.markdown("_No job links found._")

if __name__ == "__main__":
    main()
