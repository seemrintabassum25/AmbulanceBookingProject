from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from core.models import Ambulance, Booking
import time


class AmbulanceBookingSeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        service = Service(ChromeDriverManager().install())
        cls.selenium = webdriver.Chrome(service=service, options=chrome_options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test ambulance
        self.ambulance = Ambulance.objects.create(
            vehicle_number='TEST001',
            ambulance_type='basic',
            driver_name='Test Driver',
            driver_phone='9876543210',
            status='available'
        )

    def take_screenshot(self, name):
        """Helper to take screenshots"""
        self.selenium.save_screenshot(f'{name}.png')

    def login_user(self, username='testuser', password='testpass123'):
        """Helper method to login a user"""
        self.selenium.get(f'{self.live_server_url}/login/')

        # Wait for login form
        username_field = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        username_field.send_keys(username)

        password_field = self.selenium.find_element(By.NAME, 'password')
        password_field.send_keys(password)

        # Submit form
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()

        # Wait for login to complete
        time.sleep(2)

    def test_user_registration(self):
        """Test that a user can register successfully"""
        self.selenium.get(f'{self.live_server_url}/register/')
        self.take_screenshot('01_registration_page')

        # Fill registration form
        username_field = self.selenium.find_element(By.NAME, 'username')
        username_field.send_keys('newuser456')

        email_field = self.selenium.find_element(By.NAME, 'email')
        email_field.send_keys('newuser456@example.com')

        phone_field = self.selenium.find_element(By.NAME, 'phone_number')
        phone_field.send_keys('1234567890')

        password_field = self.selenium.find_element(By.NAME, 'password1')
        password_field.send_keys('strongpass123')

        confirm_field = self.selenium.find_element(By.NAME, 'password2')
        confirm_field.send_keys('strongpass123')

        self.take_screenshot('02_registration_filled')

        # Submit form
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()

        # Wait for redirect
        time.sleep(3)
        self.take_screenshot('03_after_registration')

        # Check if registration was successful (should redirect to home page)
        current_url = self.selenium.current_url
        page_text = self.selenium.page_source

        # After successful registration, user should see logout or dashboard
        if 'Logout' in page_text or 'Dashboard' in page_text:
            self.assertTrue(True, "Registration successful")
        else:
            # Check for form errors
            if 'error' in page_text.lower() or 'invalid' in page_text.lower():
                self.fail("Registration failed - form validation errors")
            else:
                self.fail(f"Registration failed. Current URL: {current_url}")

    def test_user_login(self):
        """Test that a user can login successfully"""
        # Use the login helper
        self.login_user()
        self.take_screenshot('04_after_login')

        # Check if login was successful
        page_text = self.selenium.page_source
        current_url = self.selenium.current_url

        # After successful login, should see Dashboard or Logout
        if 'Dashboard' in page_text or 'Logout' in page_text:
            self.assertTrue(True, "Login successful")
        else:
            self.take_screenshot('05_login_failed')
            self.fail(f"Login failed. URL: {current_url}. Page contains: {page_text[:500]}")

    def test_book_ambulance(self):
        """Test that a user can book an ambulance"""
        # First login
        self.login_user()
        self.take_screenshot('06_after_login_for_booking')

        # Navigate to book ambulance page
        try:
            book_link = WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, 'Book Ambulance'))
            )
            book_link.click()
        except Exception as e:
            self.take_screenshot('06_book_link_not_found')
            self.fail(f"Could not find Book Ambulance link: {e}")

        # Wait for form to load
        time.sleep(2)
        self.take_screenshot('07_booking_form')

        # Fill booking form - using more reliable methods
        try:
            # Use WebDriverWait for each element
            patient_name = WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.ID, 'id_patient_name'))
            )
            patient_name.clear()
            patient_name.send_keys('John Doe')

            patient_age = self.selenium.find_element(By.ID, 'id_patient_age')
            patient_age.clear()
            patient_age.send_keys('35')

            emergency_details = self.selenium.find_element(By.ID, 'id_emergency_details')
            emergency_details.clear()
            emergency_details.send_keys('Severe chest pain')

            pickup_location = self.selenium.find_element(By.ID, 'id_pickup_location')
            pickup_location.clear()
            pickup_location.send_keys('123 Main Street')

            dropoff_location = self.selenium.find_element(By.ID, 'id_dropoff_location')
            dropoff_location.clear()
            dropoff_location.send_keys('City Hospital')

            self.take_screenshot('08_form_filled')

            # Use JavaScript to click radio button
            basic_radio = self.selenium.find_element(By.ID, 'basic')
            self.selenium.execute_script("arguments[0].scrollIntoView(true);", basic_radio)
            time.sleep(0.5)
            self.selenium.execute_script("arguments[0].click();", basic_radio)

            # Use JavaScript to click submit button
            submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            self.selenium.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(0.5)
            self.selenium.execute_script("arguments[0].click();", submit_button)

            # Wait for booking status page
            time.sleep(3)
            self.take_screenshot('09_after_booking_submit')

            # Verify booking was created
            page_text = self.selenium.page_source
            current_url = self.selenium.current_url

            if 'booking' in current_url.lower() or 'Booking Status' in page_text or 'John Doe' in page_text:
                self.assertTrue(True, "Booking created successfully")
            else:
                self.take_screenshot('10_booking_failed')
                self.fail(f"Booking failed. URL: {current_url}")

        except Exception as e:
            self.take_screenshot('99_error_screenshot')
            self.fail(f"Error during booking: {e}")