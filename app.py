import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Wind Data Da!", layout="wide")

st.title("Wind Speed & Direction Finder – NASA POWER")
st.write("CSV-la irukura lat/long upload pannu da, date range select pannu... data vanthurum!")

# CSV upload button
uploaded = st.file_uploader("Ipo un lat-long.csv podu da", type="csv")

if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.success(f"{len(df)} locations irukku da!")
    st.write("First 10 rows paaru:")
    st.dataframe(df.head(10))

    # Date pick pannu
    start = st.date_input("Start Date", value=pd.to_datetime("2024-01-01"))
    end   = st.date_input("End Date",   value=pd.to_datetime("2024-12-31"))

    if st.button("Data Fetch Pannu Da! 🚀"):
        with st.spinner("Wait da machi, 350+ irundha 5-15 mins aagum..."):
            results = []
            progress = st.progress(0)

            for i, row in df.iterrows():
                lat = row['Latitude']
                lon = row['Longitude']

                url = (
                    f"https://power.larc.nasa.gov/api/temporal/daily/point?"
                    f"parameters=WS10M,WD10M&community=RE"
                    f"&longitude={lon}&latitude={lat}"
                    f"&start={start.strftime('%Y%m%d')}&end={end.strftime('%Y%m%d')}&format=JSON"
                )

                try:
                    r = requests.get(url, timeout=15)
                    r.raise_for_status()
                    data = r.json()['properties']['parameter']

                    ws = list(data['WS10M'].values())
                    wd = list(data['WD10M'].values())

                    avg_ws = sum(ws)/len(ws) if ws else None
                    avg_wd = sum(wd)/len(wd) if wd else None

                    results.append({
                        'Latitude': lat,
                        'Longitude': lon,
                        'Avg Wind Speed (m/s)': round(avg_ws, 2) if avg_ws else None,
                        'Avg Wind Direction (deg)': round(avg_wd, 1) if avg_wd else None
                    })
                except Exception as e:
                    results.append({
                        'Latitude': lat,
                        'Longitude': lon,
                        'Avg Wind Speed (m/s)': None,
                        'Avg Wind Direction (deg)': None,
                        'Error': str(e)
                    })

                progress.progress((i+1) / len(df))
                time.sleep(1.2)   # NASA angry aagama irukka safe delay

            final_df = pd.DataFrame(results)
            st.success("Done da boss!")
            st.dataframe(final_df)

            # Download button
            csv_data = final_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Result CSV Download Pannu",
                data=csv_data,
                file_name="wind_data_nasa.csv",
                mime="text/csv"
            )