from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import logging

# Setup logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def scrape_jobs():
    logging.info("Starting Selenium job scraping")

    # Setup headless browser
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://vacancymail.co.zw/jobs/")
    time.sleep(3)

    jobs = []

    try:
        job_cards = driver.find_elements(By.CSS_SELECTOR, "a.job-listing")
        logging.info(f"Found {len(job_cards)} job card(s)")

        for card in job_cards[:10]:
            try:
                title = card.find_element(By.CSS_SELECTOR, "h3.job-listing-title").text.strip()
                link = card.get_attribute("href")

                try:
                    company = card.find_element(By.CSS_SELECTOR, "h4.job-listing-company").text.strip()
                except:
                    company = "N/A"

                try:
                    description = card.find_element(By.CSS_SELECTOR, "p.job-listing-text").text.strip()
                except:
                    description = "N/A"

                try:
                    footer_items = card.find_elements(By.CSS_SELECTOR, ".job-listing-footer li")
                    location = footer_items[0].text.strip() if len(footer_items) > 0 else "N/A"
                    expiry = "N/A"
                    for item in footer_items:
                        if "Expires" in item.text:
                            expiry = item.text.replace("Expires", "").strip()
                            break
                except:
                    location = "N/A"
                    expiry = "N/A"

                jobs.append({
                    "Title": title,
                    "Company": company,
                    "Location": location,
                    "Expiry Date": expiry,
                    "Description": description,
                    "URL": link
                })

            except Exception as e:
                logging.warning(f"Error extracting job: {e}")
                continue

        df = pd.DataFrame(jobs)
        df.to_csv("scraped_data.csv", index=False)
        logging.info(f"Scraping complete, {len(df)} jobs saved to scraped_data.csv")

    except Exception as e:
        logging.error(f"Selenium scraping failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_jobs()
