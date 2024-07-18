from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import winsound
import threading
from cryptography.fernet import Fernet
from getpass import getpass
from os import path
from twilio.rest import Client

def twilioinit():
    
    account_sid = 'ACf876cf856fe176bb7b88cbe9de12d58c'
    auth_token = '20d043c96bea27cba233b4bb44373e04'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
    from_='+18556703139',
    body='Alert: A new ticket with a number higher than the original input has been detected. https://on.spiceworks.com/tickets/open/1?sort=id-desc',
    to='+16158157432'
    )
    print(message.sid)

def decrypt_credentials(key):
    cipher_suite = Fernet(key)
    with open("credentials.txt", "rb") as file:
        lines = file.readlines()
        decrypted_password = cipher_suite.decrypt(lines[0].strip()).decode()
    return decrypted_password

def get_credentials_from_user():
    password = getpass("Enter your password: ")
    time.sleep(0.2)
    return password

username = 'david.ewing@thistlefarms.org'

# Generate key
key = Fernet.generate_key()
original_ticket_number = None
# Encrypt credentials and store them in a file (run this only once)
password = get_credentials_from_user()

def play_alert_sound():
    # Specify the path to your default sound file or use a default Windows sound
    sound_file2 = "newticket.wav"
    winsound.PlaySound(sound_file2, winsound.SND_FILENAME)


def login_and_scan_tickets(username, password):


    # Initialize Chrome WebDriver
    driver = webdriver.Chrome()

    # Open the webpage
    driver.get("https://accounts.spiceworks.com/sign_in?policy=hosted_help_desk&success=https://on.spiceworks.com")
    time.sleep(5)

    # Find the email, password fields, and login button
    email_field = driver.find_element(By.NAME, 'email')
    password_field = driver.find_element(By.NAME, 'password')
    login_button = driver.find_element(By.XPATH, '//*[@id="login-inpage"]/div/div[1]/div/div[2]/form/div[5]/button')

    # Enter credentials
    email_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()

    #if driver.find_element(By.XPATH, '//*[@id="login-inpage"]/div/div[1]/div/div[2]/form/div[1]/div'):  
    #    print('Warning, email or password is incorrect.')
    #    exit()

    #TO-DO: Need to add an error catch that loops back to the start of the script if the email/password combination is incorrect and outputs to terminal that it's wrong.

    # Wait for page to load
    time.sleep(4.5)  # Adjust sleep time as needed

     # Get the original ticket number input from the user
    original_ticket_number = int(input("Enter the ticket number we are currently on: "))
    

    # Scan for new tickets in the queue
    while True:
        try:
            ticket_id_element = driver.find_element(By.CSS_SELECTOR, 'td.tw-p-2')
            ticket_id_text = ticket_id_element.text.strip()  # Remove leading/trailing whitespaces
            
            # Convert text to an integer if possible
            try:
                ticket_id = int(ticket_id_text)
                
                if ticket_id > original_ticket_number:
                    print("Alert: A new ticket with a number higher than the original input ({}) has been detected.".format(original_ticket_number))
                    play_alert_sound()
                    original_ticket_number += 1
                    twilioinit()


                else:
                    print("Alert: No new tickets, checking again...")

            except ValueError:
                print("Invalid ticket ID. Make sure the ticket ID is displayed as a number.")

        except NoSuchElementException:
            print("Ticket element not found.")

        # Sleep for a while
        driver.refresh()
        time.sleep(5)

    # Close the WebDriver
    driver.quit()


if __name__ == "__main__":
    login_and_scan_tickets(username, password)
