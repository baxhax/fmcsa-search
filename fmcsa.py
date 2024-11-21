import requests
import streamlit as st
import lxml.html
import pandas as pd
import urllib.parse

# Streamlit app title and GitHub link
st.title("FMCSA Carrier Search")

# Add GitHub link with icon in the sidebar
st.sidebar.markdown("""
<a href="https://github.com/baxhax/fmcsa-search" target="_blank">
    <div style="display: flex; align-items: center; gap: 5px; padding: 8px; border-radius: 5px; background-color: #f0f2f6;">
        <svg style="width:24px;height:24px" viewBox="0 0 24 24">
            <path fill="currentColor" d="M12,2A10,10 0 0,0 2,12C2,16.42 4.87,20.17 8.84,21.5C9.34,21.58 9.5,21.27 9.5,21C9.5,20.77 9.5,20.14 9.5,19.31C6.73,19.91 6.14,17.97 6.14,17.97C5.68,16.81 5.03,16.5 5.03,16.5C4.12,15.88 5.1,15.9 5.1,15.9C6.1,15.97 6.63,16.93 6.63,16.93C7.5,18.45 8.97,18 9.54,17.76C9.63,17.11 9.89,16.67 10.17,16.42C7.95,16.17 5.62,15.31 5.62,11.5C5.62,10.39 6,9.5 6.65,8.79C6.55,8.54 6.2,7.5 6.75,6.15C6.75,6.15 7.59,5.88 9.5,7.17C10.29,6.95 11.15,6.84 12,6.84C12.85,6.84 13.71,6.95 14.5,7.17C16.41,5.88 17.25,6.15 17.25,6.15C17.8,7.5 17.45,8.54 17.35,8.79C18,9.5 18.38,10.39 18.38,11.5C18.38,15.32 16.04,16.16 13.81,16.41C14.17,16.72 14.5,17.33 14.5,18.26C14.5,19.6 14.5,20.68 14.5,21C14.5,21.27 14.66,21.59 15.17,21.5C19.14,20.16 22,16.42 22,12A10,10 0 0,0 12,2Z" />
        </svg>
        <span>View on GitHub</span>
    </div>
</a>
""", unsafe_allow_html=True)

# Add a textbox for user input
search_term = st.text_input("Enter a search term:")

# Use st.cache_data for carrier info function
@st.cache_data(ttl=3600)  # Cache for 1 hour
def extract_additional_carrier_info(carrier_link):
    """
    Extract additional information from carrier page using the working xpath.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(carrier_link, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code}"
        
        tree = lxml.html.fromstring(response.content)
        elements = tree.xpath("//table//tr[17]/td[1]")
        
        return elements[0].text_content().strip() if elements else "Data not found"
        
    except requests.exceptions.Timeout:
        return "Timeout Error"
    except requests.exceptions.RequestException:
        return "Network Error"
    except Exception as e:
        return f"Error: {type(e).__name__}"

# Use st.cache_data for the main table extraction
@st.cache_data(ttl=3600)  # Cache for 1 hour
def extract_table_with_lxml(searchstring):
    # URL-encode the search string
    encoded_searchstring = urllib.parse.quote(f'*{searchstring.upper()}*')
    url = f'https://safer.fmcsa.dot.gov/keywordx.asp?searchstring={encoded_searchstring}&SEARCHTYPE='
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tree = lxml.html.fromstring(response.content)
        table = tree.xpath('//table')[2]
        
        headers = ['CARRIER/DBA NAME', 'LOCATION', 'CARRIER_LINK', 'POWER_UNITS']
        data = []
        
        rows = table.xpath('.//tr')[1:]  # Skip header row
        total_rows = len(rows)
        
        # Create progress containers outside the loop
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        for index, row in enumerate(rows):
            # Update progress text and bar
            progress_text.text(f"Processing carrier {index + 1} of {total_rows}")
            progress_bar.progress((index + 1) / total_rows)
            
            cells = row.xpath('.//td|.//th')
            cell_texts = [cell.text_content().strip() for cell in cells]
            
            carrier_link_elem = cells[0].xpath('.//a')
            if carrier_link_elem and len(cell_texts) >= 2:
                carrier_link = carrier_link_elem[0].get('href')
                if carrier_link and not carrier_link.startswith('http'):
                    carrier_link = f'https://safer.fmcsa.dot.gov/{carrier_link}'
                
                power_units = extract_additional_carrier_info(carrier_link)
                data.append([cell_texts[0], cell_texts[1], carrier_link, power_units])
        
        # Clear the progress indicators when done
        progress_text.empty()
        progress_bar.empty()
        
        return pd.DataFrame(data, columns=headers)
        
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame(columns=headers)

def main():
    if st.button("Submit"):
        if not search_term:
            st.warning("Please enter a search term.")
            return
        
        with st.spinner("Initializing search..."):
            try:
                df = extract_table_with_lxml(search_term)
                
                if not df.empty:
                    st.success(f"Found {len(df)} carriers!")
                    st.dataframe(df)
                    
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"{search_term.replace(' ', '_')}_carriers.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No results found.")
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()