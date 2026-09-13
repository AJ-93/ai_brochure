from bs4 import BeautifulSoup
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}
TIMEOUT = 10
CONTENT_LIMIT = 2_000

class WebsiteScraper:
    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()
        self.session.headers.update(HEADERS)

    def get_soup_content(self, url: str) -> BeautifulSoup:
        response = self.session.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")

    def fetch_website_contents(self,url):
        """Return title and contents of website
        Truncates the data to 2000 characters limit"""
        try:
            soup = self.get_soup_content(url)
        except requests.exceptions.RequestException as e:
            print(f"  [skipped] Could not fetch {url}: {e}")
            return ""
        title = soup.title.string if soup.title else "No Title found"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            text = soup.body.get_text(separator="\n", strip=True)
        else:
            text = ""
        return (title + "\n\n" + text)[:2_000]

    def fetch_website_links(self,url):
        """Return list of website links present in the url"""
        soup = self.get_soup_content(url)
        links = [link.get("href") for link in soup.find_all("a")]
        return [link for link in links if link]