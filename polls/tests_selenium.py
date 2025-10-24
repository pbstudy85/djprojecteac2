# polls/tests_selenium.py

from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class StaffCreationAndVerificationTest(LiveServerTestCase):
    superuser_username = "isard"
    superuser_password = "pirineus"
    staff_username_test = "staffpol"
    staff_password_test = "staff123"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = "/usr/bin/chromium-browser"

        cls.selenium = WebDriver(options=chrome_options)
        cls.wait = WebDriverWait(cls.selenium, 10)

        User.objects.create_superuser(
            cls.superuser_username, 'isard@isardvdi.com', cls.superuser_password
        )

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def login(self, username, password):
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
        self.selenium.find_element(By.NAME, 'username').send_keys(username)
        self.selenium.find_element(By.NAME, 'password').send_keys(password)
        self.selenium.find_element(By.CSS_SELECTOR, 'input[type=\"submit\"]').click()
        self.wait.until(EC.presence_of_element_located((By.ID, 'content')))

    def test_01_create_verify_staff_user(self):
        # Login admin
        self.login(self.superuser_username, self.superuser_password)

        # Crear usuari
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/add/")
        self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
        self.selenium.find_element(By.NAME, 'username').send_keys(self.staff_username_test)
        self.selenium.find_element(By.NAME, '_save').click()

        # Obrim usuari creat
        self.wait.until(
            EC.presence_of_element_located((By.LINK_TEXT, self.staff_username_test))
        ).click()

        # ✅ Obrir TAB permissions abans de clicar checkbox
        permissions_tab = self.wait.until(
            EC.presence_of_element_located((By.ID, "permissions"))
        )
        permissions_tab.click()

        # ✅ Ara sí: marcar staff
        staff_checkbox = self.wait.until(
            EC.presence_of_element_located((By.ID, "id_is_staff"))
        )
        staff_checkbox.click()
        self.selenium.find_element(By.NAME, '_save').click()

        # Assignar contrasenya
        self.wait.until(
            EC.presence_of_element_located((By.LINK_TEXT, "change password"))
        ).click()
        self.wait.until(
            EC.presence_of_element_located((By.NAME, 'password1'))
        ).send_keys(self.staff_password_test)
        self.selenium.find_element(By.NAME, 'password2').send_keys(self.staff_password_test)
        self.selenium.find_element(By.NAME, '_save').click()

        # Logout admin
        self.selenium.get(f"{self.live_server_url}/admin/logout/")

        # Login nou staff
        self.login(self.staff_username_test, self.staff_password_test)

        # Logout final
        self.selenium.get(f"{self.live_server_url}/admin/logout/")
