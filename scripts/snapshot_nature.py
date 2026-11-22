from playwright.sync_api import sync_playwright
import urllib.request

def remove_cookies_and_inline_css(page):
    # Remove cookies
    page.evaluate('''() => {
        const elements = document.querySelectorAll('.osano-cm-window, [id*=cookie], [class*=cookie], #cc-window, .cc-window, .app-consent-banner');
        elements.forEach(e => e.remove());
    }''')
    
    # Get all stylesheet hrefs
    styles = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(link => link.href);
    }''')
    
    css_content = ''
    for href in styles:
        if not href or href.startswith('data:'):
            continue
        try:
            print('Fetching CSS:', href)
            req = urllib.request.Request(href, headers={'User-Agent': 'Mozilla/5.0'})
            css = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
            css_content += css + '\\n'
        except Exception as e:
            print('Failed to fetch', href, e)
            
    # Inject all CSS
    page.evaluate('''(_css) => {
        const style = document.createElement('style');
        style.textContent = _css;
        document.head.appendChild(style);
        
        // Remove the old links
        document.querySelectorAll('link[rel="stylesheet"]').forEach(link => link.remove());
    }''', css_content)

def snapshot_pages():
    listing_url = 'https://www.nature.com/naturecareers/jobs'
    detail_url = 'https://www.nature.com/naturecareers/job/12859405/full-professorship-w3-for-biochemistry-f-m-d-/?LinkSource=PremiumListing'
    
    listing_path = r'data/raw_snapshots/jobs/naturecareers_listing/page.html'
    detail_path = r'data/raw_snapshots/jobs/naturecareers_detail/page.html'
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Snapshot Listing
        page = browser.new_page()
        print(f"Navigating to {listing_url}...")
        page.goto(listing_url, wait_until='networkidle', timeout=60000)
        
        try:
            page.wait_for_selector('ul.l-listings', timeout=10000)
        except:
            print("Could not find ul.l-listings, continuing anyway...")
            
        remove_cookies_and_inline_css(page)
            
        html = page.content()
        with open(listing_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Saved listing snapshot to {listing_path}")
        
        # Snapshot Detail
        print(f"Navigating to {detail_url}...")
        page.goto(detail_url, wait_until='networkidle', timeout=60000)
        
        try:
            page.wait_for_selector('h1', timeout=10000)
        except:
            print("Could not find h1, continuing anyway...")
            
        remove_cookies_and_inline_css(page)
            
        html = page.content()
        with open(detail_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Saved detail snapshot to {detail_path}")
        
        browser.close()

if __name__ == '__main__':
    snapshot_pages()
