from bs4 import BeautifulSoup
import requests

# Send a GET request to the webpage
response = requests.get('https://www.babelio.com/livres/Riggs-Miss-Peregrine-et-les-enfants-particuliers/358465')

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Extract the book summary
book_summary = soup.find('div', {'class': 'livre_resume'}).get_text(strip=True)

# Extract the rating information
rating = soup.find('div', {'class': 'grosse_note'}).get_text(strip=True)

# Write the extracted data to the output file
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(f"Book Summary:\n{book_summary}\n\nRating:\n{rating}")
