import requests
import streamlit as st
import lxml.html
import pandas as pd
import urllib.parse
import time

# Streamlit app title
st.title("FMSCA Carrier Search")

# Add a textbox for user input
search_term = st.text_input("Enter a search term:")

def extract_additional_carrier_info(carrier_link):
    """
    Extract additional information from carrier page using the working xpath.
    """
    try:
        time.sleep(0.1)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(carrier_link, headers=headers)
        
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code}"
        
        tree = lxml.html.fromstring(response.content)
        elements = tree.xpath("//table//tr[17]/td[1]")
        
        if elements:
            return elements[0].text_content().strip()
        return "Data not found"
        
    except requests.exceptions.RequestException as e:
        return f"Network Error: {str(e)}"
    except Exception as e:
        return f"Error: {type(e).__name__}"

def extract_table_with_lxml(searchstring):
    # URL-encode the search string
    encoded_searchstring = urllib.parse.quote(f'*{searchstring.upper()}*')
    
    # Construct the URL with the encoded search string
    url = f'https://safer.fmcsa.dot.gov/keywordx.asp?searchstring={encoded_searchstring}&SEARCHTYPE='
    
    # Send a request to the webpage
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    
    # Parse the HTML using lxml
    tree = lxml.html.fromstring(response.content)
    
    # Select the third table (index 2)
    table = tree.xpath('//table')[2]
    
    # Data extraction
    headers = ['CARRIER/DBA NAME', 'LOCATION', 'CARRIER_LINK', 'POWER_UNITS']
    data = []
    
    rows = table.xpath('.//tr')
    total_rows = len(rows) - 1  # Subtract 1 for header row
    
    for index, row in enumerate(rows[1:], 1):  # Skip header row
        cells = row.xpath('.//td|.//th')
        cell_texts = [cell.text_content().strip() for cell in cells]
        
        # Extract carrier link
        carrier_link_elem = cells[0].xpath('.//a')
        if carrier_link_elem:
            carrier_link = carrier_link_elem[0].get('href')
            # Construct full URL if it's a relative link
            if carrier_link and not carrier_link.startswith('http'):
                carrier_link = f'https://safer.fmcsa.dot.gov/{carrier_link}'
            
            # Extract additional info from the carrier's page
            power_units = extract_additional_carrier_info(carrier_link)
            
            # Ensure we have at least two elements before adding to data
            if len(cell_texts) >= 2:
                data.append([cell_texts[0], cell_texts[1], carrier_link, power_units])
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=headers)
    return df

def main():
    # Button to trigger the action
    if st.button("Submit"):
        # Validate input
        if not search_term:
            st.warning("Please enter a search term.")
            return
        
        # Process the search term
        with st.spinner("Fetching carrier information..."):
            try:
                df = extract_table_with_lxml(search_term)
                st.success(f"Found {len(df)} carriers!")

                # Show the DataFrame in the app
                st.dataframe(df)

                # Add a download button for the DataFrame
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"{search_term.replace(' ', '_')}_carriers.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Run the main program
if __name__ == "__main__":
    main()
