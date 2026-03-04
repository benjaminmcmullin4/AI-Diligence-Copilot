"""Website text extraction using BeautifulSoup."""

import requests
from bs4 import BeautifulSoup


def extract_website_text(url: str, timeout: int = 15) -> str:
    """Fetch a URL and return cleaned body text."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "TraverseBot/1.0"})
        resp.raise_for_status()
    except requests.RequestException as exc:
        return f"[Could not fetch website: {exc}]"

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    # Truncate to ~8k chars to stay within useful context
    if len(text) > 8000:
        text = text[:8000] + "\n[...truncated]"
    return text
