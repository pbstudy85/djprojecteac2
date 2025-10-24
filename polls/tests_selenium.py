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
    #credencials
    superuser_username = "isard"
    superuser_password = "pirineus"
    staff_username_test = "staffpol"
    staff_password_test = "staff123"
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # headless per CI/CD
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        cls.selenium = WebDriver(options=chrome_options) 
        cls.selenium.implicitly_wait(10)

        #superusuari
        User.objects.create_superuser(
            cls.superuser_username, 'isard@isardvdi.com', cls.superuser_password
        )
        
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def login_and_assert(self, username, password):
        """Intenta fer login i verifica l'accés a l'Admin Home."""
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/'))
        
        WebDriverWait(self.selenium, 5).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        
        self.selenium.find_element(By.NAME, 'username').send_keys(username)
        self.selenium.find_element(By.NAME, 'password').send_keys(password)
        self.selenium.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
        
        
        WebDriverWait(self.selenium, 5).until(
             EC.presence_of_element_located((By.ID, 'site-name'))
        )
        self.assertIn('Site administration', self.selenium.title, f"Login fallit per a l'usuari {username}.")


    def test_01_create_verify_staff_user(self):
        """Test únic: Login Superuser -> Crea Staff -> Verifica llista -> Prova Login Staff."""
        
        #1: access com a superusuari
        self.login_and_assert(self.superuser_username, self.superuser_password)
        
        #2: creació superusuari amb selenium        
        # Navegar a la pàgina d'afegir usuari
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/auth/user/add/'))
        
        
        self.selenium.find_element(By.NAME, 'username').send_keys(self.staff_username_test)
        self.selenium.find_element(By.NAME, 'password').send_keys(self.staff_password_test)
        self.selenium.find_element(By.NAME, 'password2').send_keys(self.staff_password_test)
        
        
        self.selenium.find_element(By.ID, 'id_is_staff').click()
        
        #premer 'save'
        self.selenium.find_element(By.NAME, '_save').click()

        #3:verificacions
        
        try:
            #cercar nom d'usuari staffpol
            self.selenium.find_element(By.XPATH, f"//a[text()='{self.staff_username_test}']")
        except NoSuchElementException:
            self.fail(f"ERROR: L'usuari Staff '{self.staff_username_test}' NO apareix a la llista d'usuaris.")

       
        
        #logout
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/logout/'))
        
        
        self.login_and_assert(self.staff_username_test, self.staff_password_test)
        
        #logout
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/logout/'))
