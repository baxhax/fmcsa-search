import requests
import streamlit as st
import lxml.html
import pandas as pd
import urllib.parse

# GitHub link
st.markdown("""
<a href="https://github.com/baxhax/fmcsa-search" target="_blank" style="color: white; text-decoration: none;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <svg style="width:24px;height:24px; fill: white;" viewBox="0 0 24 24">
            <path d="M12.5.75C6.146.75 1 5.896 1 12.25c0 5.089 3.292 9.387 7.863 10.91.575.101.79-.244.79-.546 0-.273-.014-1.178-.014-2.142-2.889.532-3.636-.704-3.866-1.35-.13-.331-.69-1.352-1.18-1.625-.402-.216-.977-.748-.014-.762.906-.014 1.553.834 1.769 1.179 1.035 1.74 2.688 1.25 3.349.948.1-.747.402-1.25.733-1.538-2.559-.287-5.232-1.279-5.232-5.678 0-1.25.445-2.285 1.178-3.09-.115-.288-.517-1.467.115-3.048 0 0 .963-.302 3.163 1.179.92-.259 1.897-.388 2.875-.388.977 0 1.955.13 2.875.388 2.2-1.495 3.162-1.179 3.162-1.179.633 1.581.23 2.76.115 3.048.733.805 1.179 1.825 1.179 3.09 0 4.413-2.688 5.39-5.247 5.678.417.36.776 1.05.776 2.128 0 1.538-.014 2.774-.014 3.162 0 .302.216.662.79.547C20.709 21.637 24 17.324 24 12.25 24 5.896 18.854.75 12.5.75Z" />
        </svg>
        <span>View on GitHub</span>
    </div>
</a>
""", unsafe_allow_html=True)

# Streamlit app title
st.title("FMCSA Carrier Search", anchor=False, help=None)

# Add a textbox for user input
search_term = st.text_input("Enter a search term:")

# Submit button in the first column
submit_button = st.button("Submit")

# Use st.cache_data for carrier info function
@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
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
@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
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
            if index % 5 == 0:  # Update every 5 rows
                progress_text.text(f"Processing carrier {index + 5} of {total_rows}")
                progress_bar.progress(index / total_rows)
            
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
    if submit_button:  # Changed from st.button to use the column button
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