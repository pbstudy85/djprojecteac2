# polls/tests_selenium.py

from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.chrome.webdriver import WebDriver 
from selenium.webdriver.chrome.options import Options      
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class StaffCreationAndVerificationTest(LiveServerTestCase):
    # credencials
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
        chrome_options.binary_location = "/usr/bin/google-chrome"  # GitHub Actions usa Chrome

        cls.selenium = WebDriver(options=chrome_options)
        cls.wait = WebDriverWait(cls.selenium, 10)

        User.objects.create_superuser(
            cls.superuser_username, 'isard@isardvdi.com', cls.superuser_password
        )
        
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def login_and_assert(self, username, password):
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        
        self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
        self.selenium.find_element(By.NAME, 'username').send_keys(username)
        self.selenium.find_element(By.NAME, 'password').send_keys(password)
        self.selenium.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

        # Assegurar canvis carregats
        self.wait.until(EC.presence_of_element_located((By.ID, 'content')))
        self.assertIn('Site administration', self.selenium.title)

    def test_01_create_verify_staff_user(self):
        # 1️⃣ Login com a admin
        self.login_and_assert(self.superuser_username, self.superuser_password)

        # 2️⃣ Crear l'usuari
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/add/")
        self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
        self.selenium.find_element(By.NAME, 'username').send_keys(self.staff_username_test)
        self.selenium.find_element(By.ID, 'id_is_staff').click()
        self.selenium.find_element(By.NAME, '_save').click()

        # Obrim l'usuari creat
        self.wait.until(EC.url_contains("/auth/user/"))
        self.selenium.find_element(By.LINK_TEXT, self.staff_username_test).click()

        # 3️⃣ Assignar contrasenya (via "change password")
        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "change password"))).click()
        self.wait.until(EC.presence_of_element_located((By.NAME, 'password1'))).send_keys(self.staff_password_test)
        self.selenium.find_element(By.NAME, 'password2').send_keys(self.staff_password_test)
        self.selenium.find_element(By.NAME, '_save').click()

        # 4️⃣ Logout admin
        self.selenium.get(f"{self.live_server_url}/admin/logout/")

        # 5️⃣ Login com a staff
        self.login_and_assert(self.staff_username_test, self.staff_password_test)

        # Final: logout
        self.selenium.get(f"{self.live_server_url}/admin/logout/")
