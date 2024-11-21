import requests
import streamlit as st
import lxml.html
import pandas as pd
import urllib.parse

# Streamlit app title
st.title("FMCSA Carrier Search")

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