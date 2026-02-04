"""
DNB (Deutsche Nationalbibliothek) API Client
Uses the SRU (Search/Retrieve via URL) protocol to fetch book metadata
Documentation: https://www.dnb.de/EN/Professionell/Metadatendienste/Datenbezug/SRU/sru_node.html
"""

import requests
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class DNBClient:
    """Client for Deutsche Nationalbibliothek SRU API"""

    BASE_URL = "https://services.dnb.de/sru/dnb"
    NAMESPACES = {
        'srw': 'http://www.loc.gov/zing/srw/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dcterms': 'http://purl.org/dc/terms/',
        'marcxml': 'http://www.loc.gov/MARC21/slim',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'YourMediaCollection/1.0'
        })

    def search_books(
        self,
        query: str,
        max_records: int = 10,
        start_record: int = 1
    ) -> List[Dict]:
        """
        Search for books in DNB catalog

        Args:
            query: Search query (e.g., "tit=Python Programming" or "isbn=9783836244299")
            max_records: Maximum number of records to retrieve (default: 10, max: 100)
            start_record: Starting record number for pagination (default: 1)

        Query examples:
            - Search by title: "tit=Python Programming"
            - Search by author: "atr=Martin Fowler"
            - Search by ISBN: "isbn=9783836244299"
            - Search by keyword: "java programming"

        Returns:
            List of book metadata dictionaries
        """
        params = {
            'version': '1.1',
            'operation': 'searchRetrieve',
            'query': query,
            'recordSchema': 'MARC21-xml',
            'maximumRecords': min(max_records, 100),
            'startRecord': start_record,
        }

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()

            return self._parse_search_response(response.text)

        except requests.RequestException as e:
            logger.error(f"DNB API request failed: {e}")
            return []

    def get_by_dnb_id(self, dnb_id: str) -> Optional[Dict]:
        """
        Fetch a specific book by DNB ID

        Args:
            dnb_id: DNB identifier (e.g., "123456789")

        Returns:
            Book metadata dictionary or None if not found
        """
        query = f'num={dnb_id}'
        results = self.search_books(query, max_records=1)
        return results[0] if results else None

    def get_by_isbn(self, isbn: str) -> Optional[Dict]:
        """
        Fetch a specific book by ISBN

        Args:
            isbn: ISBN-10 or ISBN-13

        Returns:
            Book metadata dictionary or None if not found
        """
        # Remove hyphens from ISBN
        isbn_clean = isbn.replace('-', '').replace(' ', '')
        query = f'isbn={isbn_clean}'
        results = self.search_books(query, max_records=1)
        return results[0] if results else None

    def _parse_search_response(self, xml_text: str) -> List[Dict]:
        """Parse SRU XML response and extract book metadata"""
        books = []

        try:
            root = ET.fromstring(xml_text)

            # Find all record elements
            records = root.findall('.//srw:record', self.NAMESPACES)

            for record in records:
                book_data = self._parse_marc_record(record)
                if book_data:
                    books.append(book_data)

        except ET.ParseError as e:
            logger.error(f"Failed to parse DNB response: {e}")

        return books

    def _parse_marc_record(self, record) -> Optional[Dict]:
        """Parse a single MARC21 record"""
        try:
            # Find the MARC record
            marc_record = record.find('.//marcxml:record', self.NAMESPACES)
            if marc_record is None:
                return None

            book_data = {
                'dnb_id': '',
                'isbn': '',
                'title': '',
                'subtitle': '',
                'authors': [],
                'publishers': [],
                'publication_year': None,
                'language': '',
                'categories': [],
                'description': '',
                'page_count': None,
                'dnb_raw_data': {},
            }

            # Extract control number (DNB ID)
            control_number = marc_record.find('.//marcxml:controlfield[@tag="001"]', self.NAMESPACES)
            if control_number is not None and control_number.text:
                book_data['dnb_id'] = control_number.text.strip()

            # Parse all datafields
            datafields = marc_record.findall('.//marcxml:datafield', self.NAMESPACES)

            for field in datafields:
                tag = field.get('tag')

                # ISBN (024 or 020)
                if tag in ['020', '024']:
                    isbn_field = field.find('.//marcxml:subfield[@code="a"]', self.NAMESPACES)
                    if isbn_field is not None and isbn_field.text:
                        isbn = isbn_field.text.strip().split()[0]  # Take first part before spaces
                        if isbn and not book_data['isbn']:
                            book_data['isbn'] = isbn

                # Language (041)
                elif tag == '041':
                    lang_field = field.find('.//marcxml:subfield[@code="a"]', self.NAMESPACES)
                    if lang_field is not None and lang_field.text:
                        book_data['language'] = lang_field.text.strip()

                # Authors (100, 700)
                elif tag in ['100', '700']:
                    author_field = field.find('.//marcxml:subfield[@code="a"]', self.NAMESPACES)
                    if author_field is not None and author_field.text:
                        author = author_field.text.strip()
                        if author and author not in book_data['authors']:
                            book_data['authors'].append(author)

                # Title (245)
                elif tag == '245':
                    title_field = field.find('.//marcxml:subfield[@code="a"]', self.NAMESPACES)
                    if title_field is not None and title_field.text:
                        book_data['title'] = title_field.text.strip().rstrip('/')

                    subtitle_field = field.find('.//marcxml:subfield[@code="b"]', self.NAMESPACES)
                    if subtitle_field is not None and subtitle_field.text:
                        book_data['subtitle'] = subtitle_field.text.strip().rstrip('/')

                # Publisher and year (264)
                elif tag == '264':
                    publisher_field = field.find('.//marcxml:subfield[@code="b"]', self.NAMESPACES)
                    if publisher_field is not None and publisher_field.text:
                        publisher = publisher_field.text.strip()
                        if publisher and publisher not in book_data['publishers']:
                            book_data['publishers'].append(publisher)

                    year_field = field.find('.//marcxml:subfield[@code="c"]', self.NAMESPACES)
                    if year_field is not None and year_field.text:
                        year_text = year_field.text.strip()
                        # Extract first 4-digit year
                        import re
                        year_match = re.search(r'\d{4}', year_text)
                        if year_match and not book_data['publication_year']:
                            book_data['publication_year'] = int(year_match.group())

                # Physical description (300) - page count
                elif tag == '300':
                    pages_field = field.find('.//marcxml:subfield[@code="a"]', self.NAMESPACES)
                    if pages_field is not None and pages_field.text:
                        pages_text = pages_field.text.strip()
                        # Extract page count
                        import re
                        pages_match = re.search(r'(\d+)\s*[Ss]', pages_text)
                        if pages_match and not book_data['page_count']:
                            book_data['page_count'] = int(pages_match.group(1))

                # Subject/Categories (650, 689)
                elif tag in ['650', '689']:
                    subject_field = field.find('.//marcxml:subfield[@code="a"]', self.NAMESPACES)
                    if subject_field is not None and subject_field.text:
                        subject = subject_field.text.strip()
                        if subject and subject not in book_data['categories']:
                            book_data['categories'].append(subject)

                # Description (520)
                elif tag == '520':
                    desc_field = field.find('.//marcxml:subfield[@code="a"]', self.NAMESPACES)
                    if desc_field is not None and desc_field.text:
                        book_data['description'] = desc_field.text.strip()

            # Only return if we have title, DNB ID, ISBN, and page count
            if book_data['title'] and book_data['dnb_id'] and book_data['isbn'] and book_data['page_count']:
                return book_data

            return None

        except Exception as e:
            logger.error(f"Failed to parse MARC record: {e}")
            return None


def test_dnb_client():
    """Test function to demonstrate DNB API usage"""
    client = DNBClient()

    print("Testing DNB API Client\n")

    # Test 1: Search by title
    print("1. Searching for 'Python Programming'...")
    results = client.search_books('tit=Python', max_records=3)
    print(f"Found {len(results)} results")
    for book in results:
        print(f"  - {book['title']} by {', '.join(book['authors'])}")
    print()

    # Test 2: Search by ISBN
    print("2. Searching by ISBN...")
    book = client.get_by_isbn('978-3-446-45873-1')
    if book:
        print(f"  Found: {book['title']}")
    else:
        print("  Not found")
    print()

    # Test 3: General keyword search
    print("3. Keyword search for 'django'...")
    results = client.search_books('django', max_records=5)
    print(f"Found {len(results)} results")
    for book in results:
        print(f"  - {book['title']} ({book.get('publication_year', 'N/A')})")


if __name__ == '__main__':
    test_dnb_client()
