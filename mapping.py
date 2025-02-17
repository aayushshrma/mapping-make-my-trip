import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def send_email(receiver_email, subject, body, sender_email, sender_password):
    """
    Sends an email alert via SMTP.
    """
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    email_text = message.as_string()

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # upgrade the connection to secure
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, email_text)
        server.quit()
        print("Email alert sent successfully!")
    except Exception as e:
        print("Error sending email:", e)


def main():
    # ---------------------------
    # 1. Get user inputs
    # ---------------------------
    place = input("Enter place: ")
    checkin_date = input("Enter check-in date (e.g. Thu Oct 12 2023): ")
    checkout_date = input("Enter check-out date (e.g. Sat Oct 14 2023): ")
    num_rooms = int(input("Enter number of rooms: "))
    num_adults = int(input("Enter number of adults: "))
    hotel_name = input("Enter hotel name to search: ")
    threshold_price = float(input("Enter price threshold: "))
    receiver_email = input("Enter your email address to receive alert: ")
    sender_email = "youremail@example.com"
    sender_password = "yourpassword"
    # ---------------------------
    # 2. Set up Chrome options and initialize the webdriver
    # ---------------------------
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless")

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    # ---------------------------
    # 3. Open MakeMyTrip Hotels page
    # ---------------------------
    driver.get("https://www.makemytrip.com/hotels/")
    time.sleep(5)
    # Example: Click on a blank area to close any login/sign-up popups that appear.
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        body.click()
    except Exception as e:
        print("No popup to dismiss:", e)
    # ---------------------------
    # 4. Fill in the search form
    # ---------------------------

    # 4a. Enter the place/city
    try:
        city_input = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//label[@for='city']/following-sibling::input")
        ))
        city_input.clear()
        city_input.send_keys(place)
        time.sleep(2)

        city_option = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//li[contains(text(),'{place}')]")
        ))
        city_option.click()
    except Exception as e:
        print("Error setting city/place:", e)

    # 4b. Set check-in and check-out dates
    try:
        # Click on check-in field to open the calendar widget:
        checkin_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[@for='checkin']")))
        checkin_field.click()
        time.sleep(2)
        # Select check-in date (XPath here assumes the date appears in the aria-label attribute)
        checkin_elem = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[@aria-label='{checkin_date}']")
        ))
        checkin_elem.click()

        # Select check-out date
        checkout_elem = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[@aria-label='{checkout_date}']")
        ))
        checkout_elem.click()
    except Exception as e:
        print("Error setting dates:", e)

    # 4c. Set number of rooms and adults
    try:
        occupancy_field = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//label[contains(text(),'Rooms & Guests')]")
        ))
        occupancy_field.click()
        time.sleep(2)

        room_plus_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(),'Rooms')]/following-sibling::span[contains(@class, 'plus')]")
        ))
        for i in range(num_rooms - 1):
            room_plus_btn.click()
            time.sleep(1)

        # Increase number of adults. Assume default is 1 adult and that an adult section exists.
        adult_plus_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(),'Adults')]/following-sibling::span[contains(@class, 'plus')]")
        ))
        for i in range(num_adults - 1):  # if 1 adult already set.
            adult_plus_btn.click()
            time.sleep(1)

        # Click on the Apply / Done button for guests.
        apply_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[text()='APPLY']")
        ))
        apply_button.click()
    except Exception as e:
        print("Error setting occupancy (rooms & guests):", e)

    # 4d. Click the Search button
    try:
        search_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[text()='Search']")
        ))
        search_button.click()
    except Exception as e:
        print("Error clicking search button:", e)
    # ---------------------------
    # 5. Parse the search results for the specific hotel and obtain price details
    # ---------------------------
    # Allow time for the search results page to load.
    time.sleep(10)

    prices = []
    try:
        # Locate hotel listings.
        hotel_cards = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//div[contains(@class,'listingRowOuter')]")
        ))

        for card in hotel_cards:
            try:
                title_elem = card.find_element(By.XPATH, ".//p[contains(@class,'latoBlack')]")
                hotel_title = title_elem.text

                if hotel_name.lower() in hotel_title.lower():
                    # Assuming the price element holds text like "₹12,345"
                    price_elem = card.find_element(By.XPATH, ".//p[contains(@class,'actualPrice')]")
                    price_text = price_elem.text.strip()
                    price_numeric = float(price_text.replace("₹", "").replace(",", ""))
                    prices.append(price_numeric)
            except Exception as inner_e:
                continue
    except Exception as e:
        print("Error reading hotel listings:", e)
    # ---------------------------
    # 6. Check if any of the retrieved prices is below threshold and send alert email
    # ---------------------------
    if not prices:
        print("No listings found for the hotel name provided.")
    else:
        lowest_price = min(prices)
        print(f"Lowest price found for '{hotel_name}' is: ₹{lowest_price:.2f}")
        if lowest_price < threshold_price:
            subject = f"Price Alert: {hotel_name} is now ₹{lowest_price:.2f}"
            body = (f"Good news!\n\n"
                    f"The price for {hotel_name} has dropped to ₹{lowest_price:.2f},\n"
                    f"which is below your threshold of ₹{threshold_price:.2f}.\n\n"
                    "Visit MakeMyTrip for booking details.")
            send_email(receiver_email, subject, body, sender_email, sender_password)
        else:
            print("Price is above threshold; no email alert sent.")

    # ---------------------------
    # 7. Clean-up: close the browser
    # ---------------------------
    driver.close()


if __name__ == '__main__':
    main()

