# FMCSA Carrier Search Tool

A Streamlit web application that allows users to search and extract carrier information from the Federal Motor Carrier Safety Administration (FMCSA) database. Made especially for Dillon!

## Live Application

Access the tool directly at: https://fmcsa-search-baxhax.streamlit.app/

## Features

- Search for carriers using keywords
- Extract detailed carrier information including:
  - Carrier/DBA Name
  - Location
  - Direct link to carrier's FMCSA profile
  - Number of power units
- Export results to CSV
- Progress tracking for search operations
- Caching system for improved performance

## Usage

1. Visit https://fmcsa-search-baxhax.streamlit.app/
2. Enter a search term in the text box
3. Click "Submit" to initiate the search
4. Wait for the results to load
5. View the results in the interactive table
6. Download results as CSV using the "Download CSV" button

## Technical Details

The application performs the following operations:
1. Queries the FMCSA database using the provided search term
2. Extracts basic carrier information from the search results
3. Fetches additional details from individual carrier pages
4. Compiles all information into a structured DataFrame
5. Caches results for improved performance

## Caching

- Search results are cached for 1 hour using Streamlit's caching system
- Cached results help improve performance for repeated searches
- Cache is automatically invalidated after the TTL (Time To Live) expires

## Error Handling

The application includes error handling for:
- Network timeouts
- Invalid search terms
- Empty results
- HTTP errors
- General exceptions

## Limitations

- The tool is subject to FMCSA website's availability and response times
- Large searches may take longer to complete
- Results are limited to publicly available FMCSA data

## Tips for Optimal Use

- Use specific search terms for faster results
- Allow searches to complete fully before starting new ones
- For large datasets, use the CSV export feature
- Clear your browser cache if experiencing issues

## Local Development

If you want to run the application locally or contribute to its development:

### Requirements

```
streamlit
requests
lxml
pandas
```

### Installation

1. Clone this repository or download the script
2. Install the required packages:
```bash
pip install -r requirements.txt
```

### Running Locally

1. Navigate to the script directory
2. Run the Streamlit app:
```bash
streamlit run fmcsa.py
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License

Copyright (c) 2024 baxhax

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.