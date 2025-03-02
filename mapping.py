import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import undetected_chromedriver as uc
import selenium
from requests import options
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


def scroll_to_bottom(driver, pause_time=3):
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(10):
        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def configure_chrome_options():
    # ---------------------------
    # Set up Chrome options
    # ---------------------------
    prefs = {"download.default_directory": "/path/to/download", "safebrowsing.enabled": True}
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    return chrome_options


def extract_data(options, place, place_id, checkin_date, checkout_date, hotel_names):
    # Initialize the WebDriver
    # driver = webdriver.Chrome(options=options)
    driver = uc.Chrome(use_subprocess=True)

    # ---------------------------
    # Open MakeMyTrip Hotels page
    # ---------------------------

    driver.get(f"https://www.makemytrip.com/hotels/hotel-listing/?checkin={checkin_date}&city={place_id}&checkout={checkout_date}&roomStayQualifier=2e0e&locusId={place_id}&country=IN&locusType=city&searchText={place}&regionNearByExp=3&rsc=1e2e0e")
    driver.implicitly_wait(10)
    time.sleep(3)

    # Example: Click on a blank area to close any login/sign-up popups that appear.
    # try:
    #     body = driver.find_element(By.TAG_NAME, "body")
    #     body.click()
    # except Exception as e:
    #     print("No popup to dismiss:", e)

    scroll_to_bottom(driver=driver)

    # hotel page
    hotel_links = []
    hotel_container = driver.find_element(By.ID, "hotelListingContainer")
    n = 0
    while True:
        try:
            hotel_element = hotel_container.find_element(By.ID, f"Listing_hotel_{n}")
        except:
            print(f"No. of hotels found: {n + 1}")
            break
        hotel_name = hotel_element.find_element(By.ID, "hlistpg_hotel_name").text
        print(hotel_name)
        if hotel_name.strip().lower() in hotel_names:
            print(f"{hotel_name} found in the list Hotel Names!")
            hotel_link = hotel_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            hotel_links.append((hotel_name, hotel_link))
            if len(hotel_links) == len(hotel_names):
                break
        n += 1
        time.sleep(1)

    # Room details for each hotel
    details = []
    for h_name, h_link in hotel_links:
        print(h_name)
        driver.get(h_link)
        time.sleep(5)

        scroll_to_bottom(driver=driver)

        room_section = driver.find_element(By.ID, "roomSection")
        m = 0
        while True:
            try:
                print(f"Number of room: {m}")
                rooms_ = room_section.find_element(By.ID, f"room{m}")
            except:
                break
            r_name_wrap = rooms_.find_element(By.CLASS_NAME, "rmSelect__card--leftDtlNew")
            r_name = r_name_wrap.find_element(By.TAG_NAME, "h2").text
            type_ = rooms_.find_elements(By.CLASS_NAME, "rmSelect__card--rowDtlNew.rmSelect__card--rowNew")
            for typ in type_:
                left_box = typ.find_element(By.CLASS_NAME, "rmSelect__card--rowLeftDtlNew")
                text_type = left_box.find_element(By.TAG_NAME, "h5").text
                if 'breakfast only' in text_type.lower():
                    price_parent = typ.find_element(By.CLASS_NAME, "rmSelect__card--rowRightDtlNew")
                    price_wrapper = price_parent.find_element(By.CLASS_NAME, "rmPayable__newDtl--left").text
                    details.append((h_name, r_name, price_wrapper))
                    print((h_name, r_name, price_wrapper))
                    time.sleep(2)

    # ---------------------------
    # Clean-up: close the browser
    # ---------------------------
    driver.close()

    return details


def body(price_list):
    text = ''
    for hotel, room, price in price_list:
        text += f"Hotel: {hotel.upper()}\nRoom Type: {room}, Price: {price}\n"

    return text


def main():

    options = configure_chrome_options()

    srinagar_prices = extract_data(options,place='Srinagar',place_id='CTSXR',checkin_date='04292025',
                                   checkout_date='04302025',hotel_names=['rah bagh by the orchard',
                                                                         'four points by sheraton srinagar',
                                                                         'sukoon houseboat'])
    email_body = body(price_list=srinagar_prices)

    # ---------------------------
    # User inputs
    # ---------------------------
    receiver_email = ''
    sender_email = ""
    sender_password = ""
    subject = "MMT PRICE ALERT"

    send_email(receiver_email=receiver_email,subject=subject,body=email_body,
               sender_email=sender_email, sender_password=sender_password)

    # # ---------------------------
    # # Check if any of the retrieved prices is below threshold and send alert email
    # # ---------------------------
    # if not prices:
    #     print("No listings found for the hotel name provided.")
    # else:
    #     lowest_price = min(prices)
    #     print(f"Lowest price found for '{hotel_name}' is: ₹{lowest_price:.2f}")
    #     if lowest_price < threshold_price:
    #         subject = f"Price Alert: {hotel_name} is now ₹{lowest_price:.2f}"
    #         body = (f"Good news!\n\n"
    #                 f"The price for {hotel_name} has dropped to ₹{lowest_price:.2f},\n"
    #                 f"which is below your threshold of ₹{threshold_price:.2f}.\n\n"
    #                 "Visit MakeMyTrip for booking details.")
    #         send_email(receiver_email, subject, body, sender_email, sender_password)
    #     else:
    #         print("Price is above threshold; no email alert sent.")


if __name__ == '__main__':
    main()

