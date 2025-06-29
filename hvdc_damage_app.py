import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# Set file path
DATA_FILE = "data/damage_log.csv"
os.makedirs("data", exist_ok=True)

# Ensure the CSV file exists
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        "Date", "SKU", "Product Name", "Quantity",
        "Damage Type", "Storage Zone", "Team", "Notes"
    ])
    df.to_csv(DATA_FILE, index=False)
else:
    df = pd.read_csv(DATA_FILE)

# Set up Streamlit page
st.set_page_config(page_title="HVDC Damage Reporting", layout="centered")

# Sidebar menu
page = st.sidebar.selectbox(
    "Choose Page", ["📝 Submit Damage Report", "📊 View Dashboard"]
)

# -------------------------------------
# PAGE 1: SUBMIT DAMAGE REPORT
# -------------------------------------
if page == "📝 Submit Damage Report":
    st.title("🛒 HVDC Grocery Warehouse - Damage Reporting App")
    st.subheader("📋 Submit a New Damage Report")

    with st.form("damage_form"):
        incident_date = st.date_input("Date of Incident", value=date.today())
        sku = st.text_input("Product SKU or PLU")
        product = st.text_input("Product Name")
        qty = st.number_input("Quantity Damaged", min_value=1, step=1)
        damage_type = st.selectbox("Type of Damage", [
            "Crushed", "Leaking", "Broken Packaging", "Spoiled", "Other"
        ])
        zone = st.selectbox("Storage Zone", [
            "Dry", "Cooler", "Freezer", "Loading Dock"
        ])
        team = st.selectbox("Responsible Team", [
            "Receiving", "Shipping", "Stocking", "Replens", "Unknown"
        ])
        notes = st.text_area("Optional Notes")

        submitted = st.form_submit_button("Submit Report")

        if submitted:
            # Simple validation
            if not sku or not product or qty < 1:
                st.warning("Please fill out all required fields.")
            else:
                new_row = {
                    "Date": incident_date.strftime("%Y-%m-%d"),
                    "SKU": sku,
                    "Product Name": product,
                    "Quantity": int(qty),
                    "Damage Type": damage_type,
                    "Storage Zone": zone,
                    "Team": team,
                    "Notes": notes
                }

                df = pd.read_csv(DATA_FILE)
                df = pd.concat([df, pd.DataFrame([new_row])],
                               ignore_index=True)
                df.to_csv(DATA_FILE, index=False)

                st.success("✅ Damage report submitted and saved!")

# -------------------------------------
# PAGE 2: DAMAGE DASHBOARD
# -------------------------------------
elif page == "📊 View Dashboard":
    st.title("📊 HVDC Damage Report Dashboard")

    try:
        df = pd.read_csv(DATA_FILE)

        if df.empty:
            st.info("No reports yet. Submit some damage reports first.")
        else:
            st.metric("📝 Total Reports Logged", len(df))

            # Filters
            with st.expander("🔍 Filter Report Data"):
                team_filter = st.multiselect(
                    "Filter by Team", df["Team"].unique())
                zone_filter = st.multiselect(
                    "Filter by Storage Zone", df["Storage Zone"].unique())
                damage_filter = st.multiselect(
                    "Filter by Damage Type", df["Damage Type"].unique())

                filtered_df = df.copy()
                if team_filter:
                    filtered_df = filtered_df[filtered_df["Team"].isin(
                        team_filter)]
                if zone_filter:
                    filtered_df = filtered_df[filtered_df["Storage Zone"].isin(
                        zone_filter)]
                if damage_filter:
                    filtered_df = filtered_df[filtered_df["Damage Type"].isin(
                        damage_filter)]
            st.write("")

            # Charts
            st.subheader("🔧 Damage by Type")
            st.bar_chart(filtered_df["Damage Type"].value_counts())

            st.subheader("❄️ Damage by Storage Zone")
            st.bar_chart(filtered_df["Storage Zone"].value_counts())

            st.subheader("👥 Damage by Team")
            st.bar_chart(filtered_df["Team"].value_counts())

            st.subheader("🔥 Top 5 Most Damaged Products")
            st.dataframe(filtered_df["Product Name"].value_counts().head(5))

            st.subheader("📄 Full Damage Log")
            st.dataframe(filtered_df)

            # Download button (ensure proper bytes output)
            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Filtered Report as CSV",
                data=csv,
                file_name="filtered_damage_report.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error loading data: {e}")
