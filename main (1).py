
import sys
import time
import random
import re
import threading
import hashlib
import os
import tempfile
import shutil
import io
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException


# Load environment variables from .env file
print("Loading environment variables...")
load_dotenv()

# Get token and owner ID from environment variables
token = os.getenv(MTU1MTM2NTE3MDAxMjYyNzA2NA.GsKoWr.hxqPvThnMLlzY76kr8yZ54MuNvLTzzG0ge8juE)
owner_id = os.getenv(1196709164928479282)

print(f"DISCORD_TOKEN found: {'Yes' if token else 'No'}")
print(f"BOT_OWNER_ID found: {'Yes' if owner_id else 'No'}")

if not token:
    raise ValueError("No DISCORD_TOKEN found in .env file")
if not owner_id:
    raise ValueError("No BOT_OWNER_ID found in .env file")

try:
    owner_id = int(owner_id)
except ValueError:
    raise ValueError("BOT_OWNER_ID must be a valid integer")

HEADLESS_MODE = False

class Emojis:
    """
    Centralized emoji configuration.
    These are set up for animated emojis.
    IMPORTANT: You must replace '000000000000000000' with the actual ID of your uploaded emojis.
    To find an emoji ID, type \:emoji_name: in Discord.
    """
    LOADING = "<a:loading:1453736067105685674>"
    SUCCESS = "<a:success:1453735593577283657>"
    ERROR = "<a:error:1453735727140700269>"
    WARNING = "<a:warning:1453735851048702125>"
    
    LOCK = "<a:lock:1453733428662112277>"
    KEY = "<a:keys:1453736096549699737>"
    EMAIL = "📧"
    CLOCK = "⏰"
    TIMER = "⏲️"
    SEARCH = "<a:search:1453763435769888893>"
    EDIT = "<a:edit:1453763723733897354>"
    CHAT = "<a:CHAT:1453763876993634488>"
    LIGHTNING = "<a:lightning_l:1453764092295905321>"
    PIN = "<a:pin:1453762565586030769>"
    CHART = "<a:chart~1:1453768256849580267>"
    SIREN = "<a:alert:1453762780195848357>"
    QUESTION = "❓"
    STOP = "🛑"
    PARTY = "🎉"
    LINK = "🔗"
    PHONE = "📞"
    SOS = "🆘"
    EYES = "👀"
    KEYBOARD = "⌨️"
    HOURGLASS = "⏳"
    BAN = "🚫"
    NUM1 = "1️⃣"
    NUM2 = "<a:2b:1453767835057786931>"
    NUM3 = "<:3b:1453770889718923475>"

class CPUIntensiveProcessor:
    """CPU intensive operations to maximize CPU usage and minimize GPU usage"""

    @staticmethod
    def hash_operations(data, iterations=10000):
        """Perform CPU-intensive hashing operations"""
        result = data
        for _ in range(iterations):
            result = hashlib.sha256(result.encode()).hexdigest()
        return result

    @staticmethod
    def text_processing(text, iterations=1000):
        """CPU-intensive text processing operations"""
        processed = text
        for i in range(iterations):
            processed = ''.join(reversed(processed))
            processed = processed.upper() if i % 2 == 0 else processed.lower()
            processed = processed.replace('a', '1').replace('1', 'a')
            processed = processed[:len(processed) // 2] + processed[len(processed) // 2:]
        return processed

    @staticmethod
    def mathematical_operations(base_num=12345, iterations=10000):
        """CPU-intensive mathematical calculations (optimized for speed)"""
        result = base_num
        for _ in range(iterations):
            result = (result * 7) % 1000000
            result = result ** 2 % 999999
            result = int(result ** 0.5)
        return result


class SimpleSignal:
    def __init__(self):
        self._handlers = []

    def connect(self, handler):
        self._handlers.append(handler)

    def emit(self, *args):
        for handler in self._handlers:
            try:
                handler(*args)
            except Exception as e:
                print(f"Error in signal handler: {e}")

class ScraperWorker:
    def __init__(self, account_email, account_password, headless=False):
        self.account_email = account_email
        self.account_password = account_password
        self.headless = headless
        self.first_name = "Not Available"
        self.last_name = "Not Available"
        self.dob = "Not Available"
        self.country = "Not Available"
        self.postal = ""
        self.alt_email = "Recovery_Not_Attempted"
        self.cpu_processor = CPUIntensiveProcessor()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.driver = None
        self.temp_profile_dir = None

        self.collected_emails = []
        self.collected_subjects = []

        self.target_emails = [
            "abdullahahmad123456789@gmail.com",
            "khurshidiahmad22@outlook.com",
            "skylergamer180@gmail.com",
        ]

        self._retry_response = None
        
        # Initialize signals
        self.log_signal = SimpleSignal()
        self.initial_setup_completed_signal = SimpleSignal()
        self.full_process_completed_signal = SimpleSignal()
        self.intermediate_result_signal = SimpleSignal()
        self.progress_update_signal = SimpleSignal()
        self.captcha_image_signal = SimpleSignal()
        self.ask_retry_signal = SimpleSignal()
        self.retry_decision_signal = SimpleSignal()
        self.retry_decision_signal.connect(self._set_retry_response)

        self.random_subjects = [
            "Quick Question",
            "Checking In",
            "Regarding Your Account",
            "Important Update",
            "Hello from Bot",
        ]
        self.random_messages = [
            "Hope you are having a great day!",
            "Just wanted to touch base regarding something.",
            "Please disregard if this is not relevant.",
            "This is an automated message.",
            "Wishing you all the best.",
        ]

        # Optional synchronous callbacks that can be provided by the
        # Discord layer. They are expected to block until the user replies
        # in DM (e.g. with a CAPTCHA solution or a verification code), then
        # return the text to type into the page. When not set, the flow
        # simply skips those interactive steps.
        self.captcha_solver = None
        self.code_solver = None
        self.confirmation_callback = None

    def _set_retry_response(self, response: bool):
        self._retry_response = response

    def close_browser(self):
        """Closes the browser and cleans up the temporary profile directory."""
        self.log_signal.emit("Closing browser...")
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.log_signal.emit(f"Error quitting driver: {e}")
            self.driver = None
        if self.temp_profile_dir and os.path.exists(self.temp_profile_dir):
            try:
                shutil.rmtree(self.temp_profile_dir, ignore_errors=True)
                self.log_signal.emit("Temporary profile directory cleaned.")
            except Exception as cleanup_error:
                self.log_signal.emit(f"Cleanup warning: {cleanup_error}")
        self.executor.shutdown(wait=True)

    def cpu_intensive_delay(self, min_s=1.0, max_s=2.5):
        """Minimal delay for stability."""
        time.sleep(random.uniform(0.1, 0.3))

    def _human_like_type(self, element, text, min_char_delay=0.04, max_char_delay=0.12):
        """Types text instantly."""
        if not self.driver or element is None:
            return
        try:
            element.send_keys(text)
        except Exception as e:
            self.log_signal.emit(f"Typing error: {e}")

    def _initialize_driver(self):
        """Initializes the Selenium WebDriver with stealth options."""
        self.progress_update_signal.emit(5, "Initializing browser...")
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        ]
        random_user_agent = random.choice(user_agents)

        self.temp_profile_dir = tempfile.mkdtemp()
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={random_user_agent}")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--user-data-dir={self.temp_profile_dir}")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--incognito")
        options.add_argument("--disable-notifications")

        width = random.randint(1024, 1440)
        height = random.randint(700, 900)
        options.add_argument(f"--window-size={width},{height}")

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            self.log_signal.emit(f"ChromeDriverManager failed, falling back: {e}")
            self.driver = webdriver.Chrome(options=options)

        driver = self.driver
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
              Object.defineProperty(navigator, 'webdriver', {
                 get: () => undefined
              });
              window.chrome = { runtime: {} };
              Object.defineProperty(navigator, 'plugins', {
                 get: () => [1, 2, 3, 4, 5],
              });
              Object.defineProperty(navigator, 'languages', {
                 get: () => ['en-US', 'en'],
              });
           """
            },
        )
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Corporation",
            renderer="Intel UHD Graphics",
            fix_hairline=True,
        )
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self.log_signal.emit("WebDriver initialized.")
        self.progress_update_signal.emit(10, "Browser initialized.")

    def _perform_login_check(self):
        """Attempts auto login (email + password), then waits for confirmation.

        If auto login fails for any reason, it falls back to manual login while
        still waiting for the account.microsoft.com redirect.
        """
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")

        driver = self.driver
        driver.get("https://login.live.com/")

        self.log_signal.emit(
            f"Login debug: account_email={repr(self.account_email)}, "
            f"has_password={bool(self.account_password)}"
        )

        auto_login_used = False

        if self.account_email and self.account_password:
            self.progress_update_signal.emit(15, "Auto login in progress...")
            try:
                # --- Email step ---
                email_locators = [
                    (By.NAME, "loginfmt"),
                    (By.ID, "i0116"),
                    (By.CSS_SELECTOR, "input[type='email']"),
                    (By.CSS_SELECTOR, "input[type='text']"),
                ]

                email_box = None
                last_err = None
                for how, value in email_locators:
                    try:
                        self.log_signal.emit(f"Trying email locator: {how}={value}")
                        # Be tolerant here: just wait for presence, then scroll
                        # into view and click via JS/mouse.
                        email_box = WebDriverWait(driver, 12).until(
                            EC.presence_of_element_located((how, value))
                        )
                        try:
                            driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center'});",
                                email_box,
                            )
                        except Exception:
                            pass
                        try:
                            ActionChains(driver).move_to_element(email_box).click().perform()
                        except Exception:
                            try:
                                driver.execute_script("arguments[0].click();", email_box)
                            except Exception:
                                pass
                        break
                    except Exception as e:
                        last_err = e
                        continue

                # Fallback: try JS querySelector directly if still not found/clicked
                if email_box is None:
                    try:
                        self.log_signal.emit(
                            "Email: falling back to JS querySelector lookup for login field."
                        )
                        email_box = driver.execute_script(
                            "return document.querySelector('input[name=\"loginfmt\"], #i0116, input[type=\"email\"], input[type=\"text\"]');"
                        )
                    except Exception:
                        email_box = None

                if email_box is None:
                    self.log_signal.emit(
                        f"Could not find email field with any locator or JS fallback; last error: {last_err}"
                    )
                    raise last_err or RuntimeError("Email field not found")

                try:
                    email_box.clear()
                except Exception:
                    pass
                self._human_like_type(email_box, self.account_email)
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                self.log_signal.emit("Typed email and submitted.")
                time.sleep(0.2)

                # --- Password step with helper flows ---
                end = time.time() + 60
                password_typed = False
                password_locators = [
                    (By.NAME, "passwd"),
                    (By.ID, "i0118"),
                    (By.CSS_SELECTOR, "input[type='password']"),
                ]

                while time.time() < end and not password_typed:
                    # A) Try to get out of the verify-email screen via "Other ways to sign in".
                    try:
                        other_ways_locators = [
                            # Known Microsoft ID on some variants
                            (By.ID, "idA_PWD_SwitchToCredPicker"),
                            # Exact span role="button" from your HTML
                            (
                                By.XPATH,
                                "//span[@role='button' and normalize-space(text())='Other ways to sign in']",
                            ),
                            # Any clickable element containing the text as a fallback
                            (
                                By.XPATH,
                                "//*[self::a or self::button or self::div or self::span][contains(normalize-space(.), 'Other ways to sign in')]",
                            ),
                        ]
                        for how_o, val_o in other_ways_locators:
                            try:
                                self.log_signal.emit(
                                    f"Checking for 'Other ways to sign in' link: {how_o}={val_o}"
                                )
                                other_ways_el = WebDriverWait(driver, 6).until(
                                    EC.element_to_be_clickable((how_o, val_o))
                                )
                                driver.execute_script(
                                    "arguments[0].scrollIntoView({block: 'center'});",
                                    other_ways_el,
                                )
                                # Move mouse over it then JS-click for reliability
                                try:
                                    ActionChains(driver).move_to_element(other_ways_el).click().perform()
                                except Exception:
                                    driver.execute_script("arguments[0].click();", other_ways_el)
                                self.log_signal.emit(
                                    "Clicked 'Other ways to sign in' on verify screen."
                                )
                                break
                            except Exception:
                                continue
                    except Exception:
                        pass

                    # B) On "Sign in another way", pick "Use your password".
                    try:
                        use_pwd_locators = [
                            # Exact span role="button" from your HTML
                            (
                                By.XPATH,
                                "//span[@role='button' and normalize-space(text())='Use your password']",
                            ),
                            # Any clickable element containing the text as a fallback
                            (
                                By.XPATH,
                                "//*[self::div or self::button or self::span or self::a][contains(normalize-space(.), 'Use your password')]",
                            ),
                        ]
                        for how_u, val_u in use_pwd_locators:
                            try:
                                self.log_signal.emit(
                                    f"Checking for 'Use your password' option: {how_u}={val_u}"
                                )
                                # Some variants render the label span inside a
                                # non-button container that Selenium doesn't
                                # consider "clickable". Just wait for it to be
                                # present/visible, then scroll and JS-click.
                                use_pwd_el = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((how_u, val_u))
                                )
                                driver.execute_script(
                                    "arguments[0].scrollIntoView({block: 'center'});",
                                    use_pwd_el,
                                )
                                # Prefer a real mouse click on the container if
                                # possible, otherwise JS-click the element
                                try:
                                    ActionChains(driver).move_to_element(use_pwd_el).click().perform()
          