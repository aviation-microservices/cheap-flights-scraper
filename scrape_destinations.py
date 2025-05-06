import undetected_chromedriver as webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

def save_to_csv(data, filename):
    """Saves list of lists to a CSV file."""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["City", "Date", "Price"])  # Header row
        writer.writerows(data)


def scrape_destinations():
    # URL to scrape
    URL = "https://www.swiss.com/pl/en/homepage"

    options1 = webdriver.ChromeOptions()
    driver1 = webdriver.Chrome(options=options1)

    wait = WebDriverWait(driver1, 20)

    trips = []

    try:
        driver1.get(URL)
        time.sleep(1)  # Wait for JavaScript to render the content

        # Wait for the cookie button to appear and click it
        allow_cookies_button = wait.until(EC.element_to_be_clickable((By.ID, "cm-acceptAll")))
        allow_cookies_button.click()
        print("Clicked Allow Cookies.")

        # Wait for and click the "trip type" dropdown (e.g., round trip)
        trip_type_button = WebDriverWait(driver1, 10).until(
            EC.element_to_be_clickable((By.ID, "fareteaser-triptype"))
        )
        trip_type_button.click()

        # Wait for and select the "one-way" option — update this XPath/CSS selector
        one_way_option = WebDriverWait(driver1, 10).until(
            EC.element_to_be_clickable((By.ID, "fareteaser-triptype-item-0"))
        )
        one_way_option.click()

        # Wait for and click the "origin" dropdown
        origin_button = WebDriverWait(driver1, 10).until(
            EC.element_to_be_clickable((By.ID, "fareteaser-origins"))
        )
        origin_button.click()

        # Wait for and select the "one-way" option — update this XPath/CSS selector
        gdansk_option = WebDriverWait(driver1, 10).until(
            EC.element_to_be_clickable((By.ID, "fareteaser-origins-item-1"))
        )
        gdansk_option.click()

        # Scroll to offers section
        driver1.execute_script("window.scrollTo(0, 2000)")

        time.sleep(2)  # Wait for the offers to load

        for i in range(3):
            count = 0
            destinations = driver1.find_elements(By.CLASS_NAME, "fareteaser-recommendation-destination")

            # leave only the non-empty destinations
            destinations = [d for d in destinations if d.text.strip() != ""]
            print("Found destinations:", len(destinations))
            print("Destinations:", [d.text for d in destinations])
            #leave only the first 3
            destinations = destinations[:(len(destinations) - 1)]
            # List to store the results

            for destination in destinations:
                # Find the flight offer element (e.g., Zurich)
                city = destination.text
                link = driver1.find_element(By.ID, f"{city.replace(" ", "")}-destination")

                # Open in a new tab using Ctrl + Click
                actions = ActionChains(driver1)
                actions.key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()

                # Optionally, switch to the new tab
                driver1.switch_to.window(driver1.window_handles[-1])

                time.sleep(2)

                #scroll
                driver1.execute_script("window.scrollTo(0, 1700)")

                # Wait for the calendar to load
                time.sleep(5)

                # Get days and prices
                days = driver1.find_elements(By.CLASS_NAME, "calendar-day-item-wrapper")
                month = "May"
                for day in days:
                    try:
                        price = day.find_element(By.CLASS_NAME, "calendar-day-item-price").text
                        date = day.find_element(By.CLASS_NAME, "calendar-day-item").text  # e.g., 'Saturday 03 May 2025'
                        print(f"Date: {date}, Price: {price}")
                        if date == "1":
                            month = "June"
                        full_date = f"{date} {month} 2025"
                        trips.append([city, full_date, price])
                    except Exception as e:
                        continue
                driver1.switch_to.window(driver1.window_handles[0])
                time.sleep(5)
                driver1.execute_script("window.scrollTo(0, 2000)")
                time.sleep(2)

            if i < 2:
                # Click the "Next slide" button to go to the next set of destinations
                # Wait for the "Next slide" button to be clickable
                next_button = WebDriverWait(driver1, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.swiper-button-next[aria-label="Next slide"]'))
                )

                # Click the button
                next_button.click()
                print("Right arrow button clicked.")
                time.sleep(2)

        save_to_csv(trips, "swiss_destinations.csv")
        print("Data saved to swiss_destinations.csv")

    finally:
        driver1.quit()  # Close first driver


if __name__ == "__main__":
    scrape_destinations()
