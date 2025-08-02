#!/usr/bin/env python3
"""
Fixed Actuary List Scraper with Improved Data Extraction
"""

import time
import re
import requests
import json
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

profile_path = "C:\\Users\\Stranger\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1"

class ActuaryJobScraper:
    def __init__(self, api_endpoint="http://localhost:5000/jobs", headless=True):
        self.base_url = "https://www.actuarylist.com"
        self.jobs_url = f"{self.base_url}"
        self.api_endpoint = api_endpoint
        self.headless = headless
        self.driver = None
    
    def setup_driver(self):
        """Initialize Undetected Chrome WebDriver"""
        options = uc.ChromeOptions()

        # Use user profile if needed (optional, can comment out if not needed)
        if profile_path:
            options.add_argument(f"--user-data-dir={profile_path}")

        # Additional stealth options
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36')

        CHROME_VERSION = 138
        try:
            self.driver = uc.Chrome(options=options, version_main=CHROME_VERSION)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(30)
            print("✅ Undetected Chrome driver initialized")
        except Exception as e:
            print(f"❌ Failed to start Chrome driver: {e}")
            self.driver = None
    
    def parse_date(self, date_text):
        """Convert relative dates to actual datetime objects"""
        if not date_text:
            return datetime.now().date()
        
        date_text = date_text.lower().strip()
        today = datetime.now()
        
        if "today" in date_text or "0 day" in date_text:
            return today.date()
        elif "yesterday" in date_text or "1 day ago" in date_text:
            return (today - timedelta(days=1)).date()
        elif "days ago" in date_text or "day ago" in date_text:
            match = re.search(r'(\d+)', date_text)
            if match:
                days = int(match.group(1))
                return (today - timedelta(days=days)).date()
        elif "week" in date_text:
            match = re.search(r'(\d+)', date_text)
            weeks = int(match.group(1)) if match else 1
            return (today - timedelta(weeks=weeks)).date()
        elif "month" in date_text:
            match = re.search(r'(\d+)', date_text)
            months = int(match.group(1)) if match else 1
            return (today - timedelta(days=months * 30)).date()
        
        return today.date()
    
    def extract_job_type(self, job_text):
        """Determine job type from text content"""
        job_text = job_text.lower()
        
        if any(word in job_text for word in ["intern", "internship"]):
            return "Internship"
        elif any(word in job_text for word in ["part-time", "part time", "contract"]):
            return "Part-Time"
        elif "temporary" in job_text or "temp" in job_text:
            return "Contract"
        else:
            return "Full-Time"  # Default
    
    def extract_tags(self, job_element):
        """Extract tags/keywords from job listing"""
        tags = []
        
        # Look for tag elements with various selectors
        tag_selectors = [
            ".tag", ".badge", ".label", ".chip", ".skill",
            "[class*='tag']", "[class*='badge']", "[class*='skill']",
            ".category", ".keyword", ".requirement"
        ]
        
        for selector in tag_selectors:
            try:
                elements = job_element.select(selector)
                for elem in elements:
                    tag = elem.get_text().strip()
                    if tag and 2 < len(tag) < 30 and tag not in tags:
                        tags.append(tag)
            except:
                continue
        
        # Extract common actuarial keywords from text
        keywords = [
            "Life", "Health", "P&C", "Property", "Casualty",
            "Python", "R", "SQL", "Excel", "VBA", "SAS",
            "Pricing", "Reserving", "Valuation", "Risk Management",
            "ASA", "FSA", "Fellow", "Associate", "Analyst",
            "ACAS", "FCAS", "Actuarial", "Insurance", "Reinsurance"
        ]
        
        job_text = job_element.get_text().upper()
        for keyword in keywords:
            if keyword.upper() in job_text and keyword not in tags:
                tags.append(keyword)
        
        return list(set(tags))[:8]  # Remove duplicates, limit to 8
    
    def post_job_to_api(self, job_data):
        """Post single job to your API endpoint with scraper marker and ISO date string"""
        try:
            # Ensure tags is always a list before joining
            tags = job_data["tags"]
            if not isinstance(tags, list):
                # Try to convert to list if it's a string (split by comma, strip whitespace)
                tags = [t.strip() for t in str(tags).split(",") if t.strip()]
            payload = {
                "title": job_data["title"],
                "company": job_data["company"],
                "location": job_data["location"],
                "posting_date": job_data["posting_date"].isoformat() if hasattr(job_data["posting_date"], 'isoformat') else str(job_data["posting_date"]),
                "job_url": job_data["job_url"],
                "job_type": job_data["job_type"],
                "tags": ",".join(tags),
                "from_scraper": True  # Mark this as coming from the scraper
            }
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "ActuaryJobScraper/1.0",
                "X-From-Scraper": "true"
            }
            print(f"[DEBUG] Posting payload: {json.dumps(payload, indent=2)}")
            response = requests.post(
                self.api_endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            print(f"[DEBUG] API Response Status: {response.status_code}")
            print(f"[DEBUG] API Response Headers: {dict(response.headers)}")
            if response.status_code in [200, 201]:
                return {"success": True, "message": "Job posted successfully"}
            else:
                print(f"[DEBUG] API Response Body: {response.text[:500]}")
                return {"success": False, "error": f"API returned {response.status_code}: {response.text[:200]}"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    def extract_job_data(self, job_element):
        """FIXED: Extract data from a single job element with improved selectors"""
        
        print(f"[DEBUG] Processing job element: {job_element.get('class', 'no-class')}")
        
        # Extract title - FIXED selector logic
        title = ""
        title_elem = job_element.select_one("p.Job_job-card__position__ic1rc")
        if title_elem:
            # Clone the element to avoid modifying the original
            title_elem_copy = BeautifulSoup(str(title_elem), 'html.parser')
            # Remove the 'Featured' pin if present
            pin_elem = title_elem_copy.select_one("p.Job_job-card__pin__N5sZd")
            if pin_elem:
                pin_elem.extract()
            title = title_elem_copy.get_text(strip=True)
        
        print(f"[DEBUG] Extracted title: '{title}'")

        # Extract company - FIXED
        company = ""
        company_elem = job_element.select_one("p.Job_job-card__company__7T9qY")
        if company_elem:
            company = company_elem.get_text(strip=True)
        
        print(f"[DEBUG] Extracted company: '{company}'")

        # Extract location(s) - FIXED
        location = ""
        location_elems = job_element.select("div.Job_job-card__locations__x1exr a.Job_job-card__location__bq7jX")
        if location_elems:
            locations = []
            for loc in location_elems:
                loc_text = loc.get_text(strip=True)
                # Skip salary and other non-location items
                if not loc_text.startswith("💰") and not loc_text.startswith("🇺🇸"):
                    locations.append(loc_text)
            location = ", ".join(locations) if locations else "Remote/Not specified"
        
        print(f"[DEBUG] Extracted location: '{location}'")

        # Extract posting date - try multiple approaches
        posting_date = ""
        date_elem = job_element.select_one("span.Job_job-card__posted-on__NCZaJ")
        if date_elem:
            posting_date = date_elem.get_text(strip=True)
        else:
            # Try other common date selectors
            date_selectors = [
                ".date", ".posted-date", ".job-date", 
                "time", ".publish-date", ".date-column",
                "[class*='date']", "[class*='posted']"
            ]
            for selector in date_selectors:
                elem = job_element.select_one(selector)
                if elem and elem.get_text().strip():
                    posting_date = elem.get_text().strip()
                    break

        # Extract job URL - FIXED
        job_url = ""
        link_elem = job_element.select_one("a.Job_job-page-link__a5I5g")
        if link_elem:
            href = link_elem.get('href', '')
            if href:
                job_url = href if href.startswith('http') else f"{self.base_url}{href}"

        # Extract additional data
        job_text = job_element.get_text() if job_element else ""
        job_type = self.extract_job_type(job_text)
        tags = self.extract_tags(job_element)
        parsed_date = self.parse_date(posting_date)

        result = {
            'title': title,
            'company': company,
            'location': location or "Remote/Not specified",
            'posting_date': parsed_date.isoformat() if hasattr(parsed_date, 'isoformat') else str(parsed_date),
            'job_url': job_url,
            'job_type': job_type,
            'tags': tags
        }
        
        print(f"[DEBUG] Final extracted data: {json.dumps(result, indent=2)}")
        return result

    def scrape_and_post_jobs(self, max_jobs=100):
        """Main function: scrape jobs and post to API, with pagination support"""
        posted_count = 0
        failed_count = 0
        jobs_scraped = 0

        print(f"[DEBUG] Calling setup_driver (headless={self.headless})...")
        self.setup_driver()
        print(f"[DEBUG] setup_driver finished. Driver: {self.driver}")

        if not self.driver:
            print("❌ Chrome driver was not initialized. Check previous error messages and try HEADLESS=False or update CHROME_VERSION.")
            return {"posted": 0, "failed": 0, "error": "Chrome driver not initialized"}

        try:
            print(f"🌐 Loading {self.jobs_url}...")
            self.driver.get(self.jobs_url)
            time.sleep(5)  # Wait for page load

            # Handle cookie consent
            try:
                cookie_selectors = [
                    "button[class*='cookie']",
                    "button[class*='consent']",
                    "button[class*='accept']",
                    "#cookie-accept",
                    ".cookie-accept"
                ]
                for selector in cookie_selectors:
                    try:
                        cookie_btn = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        cookie_btn.click()
                        print("✅ Cookie consent handled")
                        time.sleep(2)
                        break
                    except TimeoutException:
                        continue
            except Exception as e:
                print("ℹ️ No cookie consent popup found")

            # Pagination loop
            while jobs_scraped < max_jobs:
                print("🔍 Parsing job listings...")
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                # Use the correct selector based on your debug output
                job_elements = soup.select("div.Job_job-card__YgDAV")
                
                if not job_elements:
                    # Fallback selectors
                    selectors = [
                        "div[class*='job-']",
                        ".job-listing",
                        ".job-item",
                        ".job-card",
                        ".job"
                    ]
                    for selector in selectors:
                        elements = soup.select(selector)
                        if len(elements) >= 5:
                            job_elements = elements
                            print(f"✅ Found {len(elements)} job elements using fallback: {selector}")
                            break
                else:
                    print(f"✅ Found {len(job_elements)} job elements using primary selector")

                if not job_elements:
                    print("❌ No job elements found. Website structure may have changed.")
                    break

                print(f"📋 Processing up to {min(len(job_elements), max_jobs - jobs_scraped)} jobs on this page...")
                
                for i, job_elem in enumerate(job_elements):
                    if jobs_scraped >= max_jobs:
                        break
                        
                    print(f"\n--- Processing Job {jobs_scraped + 1} ---")
                    
                    try:
                        job_data = self.extract_job_data(job_elem)
                        
                        # Better validation
                        if job_data and job_data.get('title') and job_data.get('company'):
                            print(f"📝 Valid job found: {job_data['title']} at {job_data['company']}")
                            result = self.post_job_to_api(job_data)
                            if result["success"]:
                                posted_count += 1
                                print(f"✅ Posted job {posted_count}: {job_data['title']}")
                            else:
                                failed_count += 1
                                print(f"❌ Failed to post: {result['error']}")
                        else:
                            print(f"⚠️ Skipped job {jobs_scraped+1}: Missing title '{job_data.get('title', 'N/A')}' or company '{job_data.get('company', 'N/A')}'")
                            
                    except Exception as e:
                        failed_count += 1
                        print(f"❌ Error processing job {jobs_scraped+1}: {e}")
                        continue
                        
                    jobs_scraped += 1
                    time.sleep(0.5)

                # Try to click the next page button
                try:
                    next_btn = None
                    next_selectors = [
                        "a[rel='next']",
                        "button[aria-label='Next']",
                        ".pagination-next",
                        "button.next",
                        "a.next",
                        "li.next > a",
                        "li[aria-label='Next'] a"
                    ]
                    for selector in next_selectors:
                        try:
                            next_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if next_btn and next_btn.is_enabled():
                                break
                        except Exception:
                            continue
                    if next_btn and next_btn.is_enabled():
                        self.driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                        time.sleep(1)
                        next_btn.click()
                        print("➡️ Clicked next page button")
                        time.sleep(4)
                    else:
                        print("🚫 No next page button found or enabled. Stopping pagination.")
                        break
                except Exception as e:
                    print(f"⚠️ Pagination error: {e}")
                    break

            print(f"\n🎉 Scraping completed!")
            print(f"✅ Successfully posted: {posted_count} jobs")
            print(f"❌ Failed: {failed_count} jobs")

        except Exception as e:
            print(f"💥 Critical error during scraping: {e}")
            return {"posted": posted_count, "failed": failed_count, "error": str(e)}

        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Browser closed")

        return {"posted": posted_count, "failed": failed_count}

def scrape_and_post_actuary_jobs(max_jobs=100, headless=True, api_endpoint="http://localhost:5000/jobs"):
    """
    Main function to scrape jobs and post to your API
    
    Args:
        max_jobs: Maximum number of jobs to scrape
        headless: Run browser in headless mode
        api_endpoint: Your API endpoint
    
    Returns:
        Dictionary with results: {"posted": int, "failed": int}
    """
    scraper = ActuaryJobScraper(api_endpoint=api_endpoint, headless=headless)
    return scraper.scrape_and_post_jobs(max_jobs)

# Example usage
if __name__ == "__main__":
    print("🚀 Starting FIXED Actuary List Job Scraper")
    print("=" * 50)
    
    # Configuration
    API_ENDPOINT = "http://localhost:5000/jobs"
    MAX_JOBS = 5  # Start with even smaller number for testing
    HEADLESS = False  # Set to False for debugging the API issue
    
    print(f"📡 API Endpoint: {API_ENDPOINT}")
    print(f"🎯 Max Jobs: {MAX_JOBS}")
    print(f"👁️ Headless: {HEADLESS}")
    print()
    
    # Test API endpoint first
    try:
        # Test if the base endpoint is working
        base_endpoint = API_ENDPOINT.replace('/jobs', '/')
        response = requests.get(base_endpoint, timeout=5)
        print(f"✅ Base API endpoint ({base_endpoint}) is reachable - Status: {response.status_code}")
        
        # Test POST to /jobs endpoint with sample data
        test_payload = {
            "title": "Test Job",
            "company": "Test Company",
            "location": "Test Location",
            "posting_date": "2025-01-01",
            "job_url": "https://example.com",
            "job_type": "Full-Time",
            "tags": ["test"]
        }
        
        print("🧪 Testing API endpoint with sample data...")
        test_response = requests.post(API_ENDPOINT, json=test_payload, timeout=5)
        print(f"📡 API Test Response Status: {test_response.status_code}")
        print(f"📡 API Test Response: {test_response.text[:200]}")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to API endpoint {API_ENDPOINT}")
        print("   Make sure your Flask/FastAPI server is running on localhost:5000")
    except Exception as e:
        print(f"⚠️ Warning: API test failed: {e}")
    
    print("\n" + "="*50)
    
    # Run scraper
    result = scrape_and_post_actuary_jobs(
        max_jobs=MAX_JOBS,
        headless=HEADLESS,
        api_endpoint=API_ENDPOINT
    )
    
    print(f"\n🏁 Final Results:")
    print(f"✅ Jobs posted to API: {result['posted']}")
    print(f"❌ Failed jobs: {result['failed']}")
    
    if result.get('error'):
        print(f"💥 Error: {result['error']}")