import time
import smtplib
import platform
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import undetected_chromedriver as uc
from datetime import datetime
from selenium.webdriver.common.by import By
if platform.system() != 'Windows':
    from xvfbwrapper import Xvfb


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

    while True:
        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def configure_chrome_options():
    chrome_options = uc.ChromeOptions()

    # Essential options for Docker
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    if platform.system() != 'Windows':
        # Options specific for Docker/Linux with Xvfb
        chrome_options.add_argument('--display=:99')
        chrome_options.add_argument('--disable-gpu')

    # Common options for both environments
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    return chrome_options


def extract_data(driver, place, place_id, checkin_date, checkout_date, hotel_names):

    # ---------------------------
    # Open MakeMyTrip Hotels page
    # ---------------------------

    driver.get(f"https://www.makemytrip.com/hotels/hotel-listing/?checkin={checkin_date}&city={place_id}&checkout={checkout_date}&roomStayQualifier=2e0e&locusId={place_id}&country=IN&locusType=city&searchText={place}&regionNearByExp=3&rsc=1e2e0e")
    time.sleep(3)

    # Example: Click on a blank area to close any login/sign-up popups that appear.
    # try:
    #     body = driver.find_element(By.TAG_NAME, "body")
    #     body.click()
    # except Exception as e:
    #     print("No popup to dismiss:", e)

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
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Room details for each hotel
    details = []
    for h_name, h_link in hotel_links:
        print(h_name)
        driver.get(h_link)
        time.sleep(5)

        # scroll_to_bottom(driver=driver)

        room_section = driver.find_element(By.ID, "roomSection")
        m = 0
        while True:
            try:
                print(f"Number of room: { m+ 1}")
                rooms_ = room_section.find_element(By.ID, f"room{m}")
            except:
                break
            r_name_wrap = rooms_.find_element(By.CLASS_NAME, "rmSelect__card--leftDtlNew")
            r_name = r_name_wrap.find_element(By.TAG_NAME, "h2").text
            if any(sub in r_name.lower() for sub in ['junior suite', 'suite room', 'royal suite', 'luxury first floor']):
                type_ = rooms_.find_elements(By.CLASS_NAME, "rmSelect__card--rowDtlNew.rmSelect__card--rowNew")
                for typ in type_:
                    left_box = typ.find_element(By.CLASS_NAME, "rmSelect__card--rowLeftDtlNew")
                    text_type = left_box.find_element(By.TAG_NAME, "h5").text
                    if 'breakfast' in text_type.lower():
                        price_parent = typ.find_element(By.CLASS_NAME, "rmSelect__card--rowRightDtlNew")
                        price_wrapper = price_parent.find_element(By.CLASS_NAME, "rmPayable__newDtl--left").text
                        prices = price_wrapper.replace("\n", ";")
                        details.append((h_name, r_name, text_type, prices))
                        print((h_name, r_name, text_type, prices))
                        time.sleep(2)
            m+=1

    return details


def email_body(price_list):
    text = ''
    for hotel, room, type_, price in price_list:
        if hotel.upper() not in text:
            text += f"\nHOTEL: {hotel.upper()}"
        text += f"\n{room}: {type_}, PRICE: {price}"

    return text


def run_scraper():

    driver = uc.Chrome(options=configure_chrome_options(), use_subprocess=True) # Initialize the WebDriver
    # driver = uc.Chrome(use_subprocess=True)
    driver.implicitly_wait(10)

    try:
        srinagar_prices = extract_data(driver=driver,place='Srinagar',place_id='CTSXR',checkin_date='04292025',
                                       checkout_date='04302025',hotel_names=['rah bagh by the orchard',
                                                                             'four points by sheraton srinagar',
                                                                             'sukoon houseboat'])
        email_text_1 = email_body(price_list=srinagar_prices)
    except Exception as e:
        print(f"RUN FAILED for SRINAGAR, ERROR: {e}")
        email_text_1 = f"RUN FAILED for SRINAGAR 29.04, ERROR: {e}"

    time.sleep(2)
    try:
        srinagar_prices_2 = extract_data(driver=driver,place='Srinagar',place_id='CTSXR',checkin_date='05012025',
                                       checkout_date='05022025',hotel_names=['rah bagh by the orchard',
                                                                             'four points by sheraton srinagar',
                                                                             'sukoon houseboat'])
        email_text_2 = email_body(price_list=srinagar_prices_2)
    except Exception as e:
        print(f"RUN FAILED for SRINAGAR, ERROR: {e}")
        email_text_2 = f"RUN FAILED for SRINAGAR 01.05, ERROR: {e}"

    time.sleep(2)
    try:
        gulmarg_prices = extract_data(driver=driver,place='Gulmarg',place_id='CTXGU',checkin_date='04262025',
                                       checkout_date='04272025',hotel_names=['green rooms resort gulmarg'])
        email_text_3 = email_body(price_list=gulmarg_prices)
    except Exception as e:
        print(f"RUN FAILED for GULMARG, ERROR: {e}")
        email_text_3 = f"RUN FAILED for GULMARG, ERROR: {e}"
    # ---------------------------
    # Clean-up: close the browser
    # ---------------------------

    driver.close()

    email_text = (
            f'{"-" * 50}29.04.2025{"-" * 50}\n' + email_text_1 + f'\n{"-" * 50}01.05.2025{"-" * 50}\n' + email_text_2 +
            f'\n{"-" * 50}26.04.2025{"-" * 50}\n' + email_text_3)

    return email_text


def main():
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    print("Time of Run:", formatted_datetime)

    # Use Xvfb only in Docker (Linux)
    if platform.system() != 'Windows':
        with Xvfb(width=1920, height=1080, colordepth=24):
            email_text = run_scraper()
    else:
        # On Windows, run without Xvfb
        email_text = run_scraper()

        # ---------------------------
        # User inputs
        # ---------------------------


        subject = f"MMT PRICE ALERT {formatted_datetime}"

        send_email(receiver_email=receiver_email, subject=subject, body=email_text,
                   sender_email=sender_email, sender_password=sender_password)


if __name__ == '__main__':
    main()

