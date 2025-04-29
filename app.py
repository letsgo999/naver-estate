import streamlit as st
import requests
import pandas as pd

# Streamlit page setup
st.set_page_config(page_title="Real Estate Listings Viewer", layout="wide")
st.title("Real Estate Listings from Pages 1 to 10")
st.markdown("This page fetches and displays real estate listings from pages 1 to 10 using the Naver Real Estate API.")

# Define the cookies and headers as provided
cookies = {
    "NNB": "2NONCTNLIE0GO",
    "ASID": "7c6fa45e00000192fbaff11000001ff",
    "_fbp": "fb.1.1744628216269.972020173418817331",
    "_fwb": "64cuR6OKRRAkvfQJCWaXQm.1744948363977",
    "landHomeFlashUseYn": "Y",
    "fwb": "64cuR6OKRRAkvfQJCWaXQm.1744948363977",
    "NAC": "JAUGBkQuRFFR",
    "nhn.realestate.article.rlet_type_cd": "A01",
    "nhn.realestate.article.trade_type_cd": "",
    "NACT": "1",
    "SRT30": "1745950084",
    "SRT5": "1745950084",
    "nid_inf": "2007784581",
    "NID_AUT": "oqWl0bCVjiBdZKmddxFIKnNPBh3ZtUtc9bElBGpkHk5DylOgAr7bsmx3rNsZ56Qv",
    "NID_SES": "AAABsPHPUuHdNh50pLJG/8FrcZWbJ1V7htBXmvJm+XVXyOITrH7okTKrOmA5YR5PdpLZfNnw4+Rkf9UHJzyGLb58ZTZLvgbvD7GgAmmJXufJKPPw0kHHhXpMawYWl4vVbUUpVeC58BOdJ2UV/5aKgeahAaRuAonCazTeiIokYds7MbvS1fSKmR/pe+JVSskiPp3bdfcQMZUarWy87PhchVFmCIqJKMNECxMFkHU8DoFFq00y++Ar48MJIFrqF+1XiCkjuEVKEH9m78VhZP9zfosGQJz6/c84nXZU2iILyA6kP9kjTgxFW7WMvTl12vvI3ATbzUq9WOsb9weo3hXGOH8sGd0bPzj6EB/RC2bjQVgoQbFQzm5sBn+cFY+6do9K7RfPCHRadTb+Zlt7kVnaayT1nkonwxzV/SPdkZ2a+rcPgLhY06KvL8tU+lzb4+74b/du/IlAfkn+Qzpk/TES9Adrz01g1Dvz0JTkJ4d4ljP7Oe3x9oFYJesmwqjDFPDgFkNPhOE/wGjXp9iERUOGMxBgt0FHf7zVGq5llatEMDTFcas7iQk+Hp78EzMAWAmH0eaijQ==",
    "BUC": "wC6mHThXTfTeF4kEVmvpeunRhV4jjKfEo2a5un_TQA",
    "REALESTATE": "Wed%20Apr%2029%202025%2003%3A48%3A48%20GMT%2B0900(Korean%20Standard%20Time)",
}


headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ko,en-US;q=0.9,en;q=0.8,lg;q=0.7",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlJFQUxFU1RBVEUiLCJpYXQiOjE3NDU5NTIzMTIsImV4cCI6MTc0NTk2MzExMn0.jzmEpMedwucOxfnfDaVf1qyITZ9mCkhmQu1VI7s2ETQ",  # 실제 값은 이미지에서 복사
    "Referer": "https://new.land.naver.com/complexes?",
    "Sec-Ch-Ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
}



# Function to get data from the API for pages 1 to 10
@st.cache_data
def fetch_all_data():
    all_articles = []
    for page in range(1, 11):
        try:
            # Make the request for the specific page
            url = f'https://new.land.naver.com/api/articles/complex/111515?realEstateType=APT%3AABYG%3AJGC%3APRE&tradeType=A1&tag=%3A%3A%3A%3A%3A%3A%3A%3A&rentPriceMin=0&rentPriceMax=900000000&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000&oldBuildYears&recentlyBuildYears&minHouseHoldCount=300&maxHouseHoldCount&showArticle=false&sameAddressGroup=true&minMaintenanceCost&maxMaintenanceCost&priceType=RETAIL&directions=&page={page}&complexNo=111515&buildingNos=&areaNos=&type=list&order=prc'
            response = requests.get(url, cookies=cookies, headers=headers)

            # Verify response is valid JSON
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articleList", [])
                all_articles.extend(articles)
            else:
                st.warning(f"Failed to retrieve data for page {page}. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
        except ValueError:
            st.error(f"Non-JSON response for page {page}.")

    return all_articles

# Fetch data for all pages
data = fetch_all_data()

# Transform data into a DataFrame if data is available
if data:
    df = pd.DataFrame(data)
    # Select columns to display
    df_display = df[["articleNo", "articleName", "realEstateTypeName", "tradeTypeName", "floorInfo",
                     "dealOrWarrantPrc", "areaName", "direction", "articleConfirmYmd", "articleFeatureDesc",
                     "tagList", "buildingName", "sameAddrMaxPrc", "sameAddrMinPrc", "realtorName"]]

    # Display the table in Streamlit with a clean, readable layout
    st.write("### Real Estate Listings - Pages 1 to 10")
    st.dataframe(df_display)
else:
    st.write("No data available.")


