# AsyncCrawler/CrawlerStats.py
import json
import time
from collections import Counter

class CrawlerStats:
    def __init__(self):
        self.start_time = time.time()
        self.total_pages = 0
        self.status_codes = Counter()
        self.errors = 0
        self.domains = Counter()

    def update(self, url, status_code):
        self.total_pages += 1
        self.status_codes[status_code] += 1
        from urllib.parse import urlparse
        self.domains[urlparse(url).netloc] += 1

    def get_report(self):
        duration = time.time() - self.start_time
        return {
            "duration_sec": round(duration, 2),
            "total_pages": self.total_pages,
            "rps": round(self.total_pages / duration, 2) if duration > 0 else 0,
            "status_distribution": dict(self.status_codes),
            "top_domains": dict(self.domains.most_common(5))
        }

    def export_to_json(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.get_report(), f, indent=4)

    def export_to_html(self, filename):
        report = self.get_report()
        html = f"""
        <html><body style='font-family: sans-serif;'>
            <h1>Crawler Report</h1>
            <p>Pages: {report['total_pages']}</p>
            <p>RPS: {report['rps']}</p>
            <h3>Status Codes</h3>
            <ul>{"".join(f"<li>{k}: {v}</li>" for k, v in report['status_distribution'].items())}</ul>
        </body></html>
        """
        with open(filename, 'w') as f:
            f.write(html)