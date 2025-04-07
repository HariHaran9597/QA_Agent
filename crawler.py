import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import List, Tuple

class Crawler:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.visited = set()
        self.pages = []  # Stores tuples of (url, html_content)

    def is_valid_url(self, url: str) -> bool:
        parsed_url = urlparse(url)
        parsed_url = parsed_url._replace(fragment="")
        base_domain = urlparse(self.base_url).netloc
        return parsed_url.netloc == base_domain and parsed_url.geturl() not in self.visited
    
    def fetch(self, url: str) -> str:
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
         }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"⚠️ Failed to fetch {url}: {str(e)}")
            return None

    def extract_links(self, html: str) -> List[str]:
        """Extract all internal links from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for link in soup.find_all("a", href=True):
            full_url = urljoin(self.base_url, link["href"])
            if self.is_valid_url(full_url) and full_url not in self.visited:
                links.append(full_url)
        return links

    def crawl(self, url: str = None) -> None:
        """Recursively crawl the website starting from the base URL."""
        url = url or self.base_url
        if url in self.visited:
            return
        self.visited.add(url)
        
        html = self.fetch(url)
        if html:
            self.pages.append((url, html))
            links = self.extract_links(html)
            for link in links:
                self.crawl(link)

if __name__ == "__main__":
    crawler = Crawler("https://help.slack.com")
    crawler.crawl()
    print(f"Crawled {len(crawler.pages)} pages.")
    print("Sample page:", crawler.pages[0][0])  # Print first URL