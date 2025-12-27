import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

type Language = 'python' | 'java';

const pythonCode = `"""
End-to-End UI Tests using Python + Playwright
Run: pip install pytest playwright && playwright install && pytest test_auth.py
"""
import re
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://localhost:5174"


@pytest.fixture(autouse=True)
def setup(page: Page):
    """Clear session before each test."""
    page.goto(BASE_URL)
    # Clear localStorage to reset auth state
    page.evaluate("localStorage.clear()")
    page.reload()


def logout_if_logged_in(page: Page):
    """Logout if currently logged in."""
    if "/home" in page.url or "/about" in page.url:
        page.get_by_role("button", name="Logout").click()
        expect(page).to_have_url(BASE_URL + "/")


def ensure_user_exists(page: Page, username: str, password: str):
    """Create user if they don't exist (for test1 setup)."""
    page.goto(BASE_URL + "/")
    page.get_by_label("Username").fill(username)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Login").click()
    
    # If login fails, user doesn't exist - create them
    if page.locator("text=Invalid username or password").is_visible():
        page.get_by_role("link", name="Create Account").click()
        expect(page).to_have_url(BASE_URL + "/register")
        
        page.get_by_label("Username").fill(username)
        page.get_by_label("Password", exact=True).fill(password)
        page.get_by_label("Confirm Password").fill(password)
        page.get_by_role("button", name="Create Account").click()
        
        expect(page).to_have_url(BASE_URL + "/")
    else:
        # User exists and logged in, logout
        logout_if_logged_in(page)


class TestLoginAdmin:
    """Test 1: Login with seeded admin user."""
    
    def test_admin_login(self, page: Page):
        page.goto(BASE_URL + "/")
        
        page.get_by_label("Username").fill("admin")
        page.get_by_label("Password").fill("admin")
        page.get_by_role("button", name="Login").click()
        
        # Verify redirect to home
        expect(page).to_have_url(BASE_URL + "/home")
        expect(page.locator("text=Welcome, admin")).to_be_visible()
        expect(page.get_by_role("button", name="Logout")).to_be_visible()


class TestForgotPassword:
    """Test 2: Forgot password flow for test1 user."""
    
    def test_forgot_password_flow(self, page: Page):
        # Ensure test1 user exists first
        ensure_user_exists(page, "test1", "test1")
        
        # Go to forgot password
        page.goto(BASE_URL + "/")
        page.get_by_role("link", name="Forgot Password").click()
        expect(page).to_have_url(BASE_URL + "/forgot-password")
        
        # Request temp password
        page.get_by_label("Username").fill("test1")
        page.get_by_role("button", name="Reset Password").click()
        
        # Capture the temp password from the success message
        success_msg = page.locator(".bg-green-100")
        expect(success_msg).to_be_visible()
        
        # Extract temp password using regex
        msg_text = success_msg.inner_text()
        match = re.search(r"Temporary password generated:\\s*([A-Za-z0-9]+)", msg_text)
        assert match, f"Could not find temp password in: {msg_text}"
        temp_password = match.group(1)
        
        # Go back to login
        page.get_by_role("link", name="Back to Login").click()
        expect(page).to_have_url(BASE_URL + "/")
        
        # Login with temp password
        page.get_by_label("Username").fill("test1")
        page.get_by_label("Password").fill(temp_password)
        page.get_by_role("button", name="Login").click()
        
        # Verify successful login
        expect(page).to_have_url(BASE_URL + "/home")
        expect(page.locator("text=Welcome, test1")).to_be_visible()


class TestCreateAccount:
    """Test 3: Create account for test2 and login."""
    
    def test_create_account_and_login(self, page: Page):
        page.goto(BASE_URL + "/")
        
        # Navigate to register
        page.get_by_role("link", name="Create Account").click()
        expect(page).to_have_url(BASE_URL + "/register")
        
        # Fill registration form
        page.get_by_label("Username").fill("test2")
        page.get_by_label("Password", exact=True).fill("test2")
        page.get_by_label("Confirm Password").fill("test2")
        page.get_by_role("button", name="Create Account").click()
        
        # Verify redirect and success message
        expect(page).to_have_url(BASE_URL + "/")
        expect(page.locator("text=Account created")).to_be_visible()
        
        # Login with new account
        page.get_by_label("Username").fill("test2")
        page.get_by_label("Password").fill("test2")
        page.get_by_role("button", name="Login").click()
        
        # Verify successful login
        expect(page).to_have_url(BASE_URL + "/home")
        expect(page.locator("text=Welcome, test2")).to_be_visible()
`;

const javaCode = `/**
 * End-to-End UI Tests using Java + Selenium + JUnit 5
 * 
 * pom.xml dependencies:
 * <dependencies>
 *     <dependency>
 *         <groupId>org.seleniumhq.selenium</groupId>
 *         <artifactId>selenium-java</artifactId>
 *         <version>4.16.1</version>
 *     </dependency>
 *     <dependency>
 *         <groupId>org.junit.jupiter</groupId>
 *         <artifactId>junit-jupiter</artifactId>
 *         <version>5.10.1</version>
 *         <scope>test</scope>
 *     </dependency>
 *     <dependency>
 *         <groupId>io.github.bonigarcia</groupId>
 *         <artifactId>webdrivermanager</artifactId>
 *         <version>5.6.2</version>
 *         <scope>test</scope>
 *     </dependency>
 * </dependencies>
 * 
 * Run: mvn test
 */
package com.example.tests;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.junit.jupiter.api.*;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static org.junit.jupiter.api.Assertions.*;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class AuthTests {

    private static WebDriver driver;
    private static WebDriverWait wait;
    private static final String BASE_URL = "http://localhost:5174";

    @BeforeAll
    static void setupClass() {
        WebDriverManager.chromedriver().setup();
    }

    @BeforeEach
    void setup() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        
        // Clear localStorage
        driver.get(BASE_URL);
        ((JavascriptExecutor) driver).executeScript("localStorage.clear()");
        driver.navigate().refresh();
    }

    @AfterEach
    void teardown() {
        if (driver != null) {
            driver.quit();
        }
    }

    private WebElement findByLabel(String labelText) {
        WebElement label = driver.findElement(
            By.xpath("//label[contains(text(),'" + labelText + "')]")
        );
        String forId = label.getAttribute("for");
        return driver.findElement(By.id(forId));
    }

    private WebElement findButton(String text) {
        return wait.until(ExpectedConditions.elementToBeClickable(
            By.xpath("//button[contains(text(),'" + text + "')]")
        ));
    }

    private WebElement findLink(String text) {
        return wait.until(ExpectedConditions.elementToBeClickable(
            By.xpath("//a[contains(text(),'" + text + "')]")
        ));
    }

    private void logoutIfLoggedIn() {
        try {
            if (driver.getCurrentUrl().contains("/home") || 
                driver.getCurrentUrl().contains("/about")) {
                findButton("Logout").click();
                wait.until(ExpectedConditions.urlToBe(BASE_URL + "/"));
            }
        } catch (Exception ignored) {}
    }

    private void ensureUserExists(String username, String password) {
        driver.get(BASE_URL + "/");
        
        findByLabel("Username").sendKeys(username);
        findByLabel("Password").sendKeys(password);
        findButton("Login").click();
        
        try {
            Thread.sleep(500);
        } catch (InterruptedException ignored) {}
        
        // Check if login failed (user doesn't exist)
        try {
            WebElement error = driver.findElement(
                By.xpath("//*[contains(text(),'Invalid username or password')]")
            );
            if (error.isDisplayed()) {
                // Create the user
                findLink("Create Account").click();
                wait.until(ExpectedConditions.urlContains("/register"));
                
                findByLabel("Username").sendKeys(username);
                driver.findElement(By.id("password")).sendKeys(password);
                findByLabel("Confirm Password").sendKeys(password);
                findButton("Create Account").click();
                
                wait.until(ExpectedConditions.urlToBe(BASE_URL + "/"));
            }
        } catch (NoSuchElementException e) {
            // Login succeeded, user exists - logout
            logoutIfLoggedIn();
        }
    }

    @Test
    @Order(1)
    @DisplayName("Test 1: Login with seeded admin user")
    void testAdminLogin() {
        driver.get(BASE_URL + "/");
        
        findByLabel("Username").sendKeys("admin");
        findByLabel("Password").sendKeys("admin");
        findButton("Login").click();
        
        // Verify redirect to home
        wait.until(ExpectedConditions.urlToBe(BASE_URL + "/home"));
        
        WebElement welcome = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.xpath("//*[contains(text(),'Welcome, admin')]")
        ));
        assertTrue(welcome.isDisplayed());
        
        assertTrue(findButton("Logout").isDisplayed());
    }

    @Test
    @Order(2)
    @DisplayName("Test 2: Forgot password flow for test1")
    void testForgotPasswordFlow() {
        // Ensure test1 exists
        ensureUserExists("test1", "test1");
        
        // Go to forgot password
        driver.get(BASE_URL + "/");
        findLink("Forgot Password").click();
        wait.until(ExpectedConditions.urlContains("/forgot-password"));
        
        // Request temp password
        findByLabel("Username").sendKeys("test1");
        findButton("Reset Password").click();
        
        // Wait for success message and extract temp password
        WebElement successMsg = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.cssSelector(".bg-green-100")
        ));
        
        String msgText = successMsg.getText();
        Pattern pattern = Pattern.compile("Temporary password generated:\\\\s*([A-Za-z0-9]+)");
        Matcher matcher = pattern.matcher(msgText);
        assertTrue(matcher.find(), "Could not find temp password in: " + msgText);
        String tempPassword = matcher.group(1);
        
        // Go back to login
        findLink("Back to Login").click();
        wait.until(ExpectedConditions.urlToBe(BASE_URL + "/"));
        
        // Login with temp password
        findByLabel("Username").sendKeys("test1");
        findByLabel("Password").sendKeys(tempPassword);
        findButton("Login").click();
        
        // Verify successful login
        wait.until(ExpectedConditions.urlToBe(BASE_URL + "/home"));
        
        WebElement welcome = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.xpath("//*[contains(text(),'Welcome, test1')]")
        ));
        assertTrue(welcome.isDisplayed());
    }

    @Test
    @Order(3)
    @DisplayName("Test 3: Create account for test2 and login")
    void testCreateAccountAndLogin() {
        driver.get(BASE_URL + "/");
        
        // Navigate to register
        findLink("Create Account").click();
        wait.until(ExpectedConditions.urlContains("/register"));
        
        // Fill registration form
        findByLabel("Username").sendKeys("test2");
        driver.findElement(By.id("password")).sendKeys("test2");
        findByLabel("Confirm Password").sendKeys("test2");
        findButton("Create Account").click();
        
        // Verify redirect and success message
        wait.until(ExpectedConditions.urlToBe(BASE_URL + "/"));
        
        WebElement successMsg = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.xpath("//*[contains(text(),'Account created')]")
        ));
        assertTrue(successMsg.isDisplayed());
        
        // Login with new account
        findByLabel("Username").sendKeys("test2");
        findByLabel("Password").sendKeys("test2");
        findButton("Login").click();
        
        // Verify successful login
        wait.until(ExpectedConditions.urlToBe(BASE_URL + "/home"));
        
        WebElement welcome = wait.until(ExpectedConditions.visibilityOfElementLocated(
            By.xpath("//*[contains(text(),'Welcome, test2')]")
        ));
        assertTrue(welcome.isDisplayed());
    }
}
`;

export function TestGeneratorPage() {
  const [language, setLanguage] = useState<Language>('python');
  const [copied, setCopied] = useState(false);
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const getCode = () => {
    return language === 'python' ? pythonCode : javaCode;
  };

  const getInstructions = () => {
    if (language === 'python') {
      return {
        title: 'Python + Playwright',
        steps: [
          'pip install pytest playwright',
          'playwright install',
          'Save the code as test_auth.py',
          'pytest test_auth.py -v',
        ],
      };
    }
    return {
      title: 'Java + Selenium + JUnit 5',
      steps: [
        'Create a Maven project with the dependencies in the code comments',
        'Save the code as src/test/java/com/example/tests/AuthTests.java',
        'mvn test',
      ],
    };
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(getCode());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const instructions = getInstructions();

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center space-x-8">
              <span className="text-xl font-semibold text-gray-800">
                Auth Demo
              </span>
              <div className="flex space-x-4">
                <Link
                  to="/home"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Home
                </Link>
                <Link
                  to="/about"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  About Us
                </Link>
                <Link
                  to="/test-generator"
                  className="text-blue-600 hover:text-blue-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Test Generator
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Logged in as: {currentUser}
              </span>
              <button
                onClick={handleLogout}
                type="button"
                className="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors text-sm"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">
            Test Code Generator
          </h1>
          <p className="text-gray-600 mb-6">
            Generate end-to-end test automation code for this authentication app.
            Select your preferred language below.
          </p>

          {/* Language Selector */}
          <div className="mb-6">
            <label
              htmlFor="language"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Select Language
            </label>
            <select
              id="language"
              value={language}
              onChange={(e) => setLanguage(e.target.value as Language)}
              className="w-full max-w-xs px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="python">Python (Playwright + pytest)</option>
              <option value="java">Java (Selenium + JUnit 5)</option>
            </select>
          </div>

          {/* Instructions */}
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
            <h3 className="font-semibold text-blue-800 mb-2">
              {instructions.title} - Setup Instructions
            </h3>
            <ol className="list-decimal list-inside text-blue-700 space-y-1">
              {instructions.steps.map((step, index) => (
                <li key={index} className="font-mono text-sm">
                  {step}
                </li>
              ))}
            </ol>
          </div>

          {/* Copy Button */}
          <div className="mb-4">
            <button
              onClick={handleCopy}
              type="button"
              className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              {copied ? '✓ Copied!' : 'Copy Code'}
            </button>
          </div>

          {/* Code Display */}
          <div className="relative">
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-md overflow-x-auto text-sm max-h-[600px] overflow-y-auto">
              <code>{getCode()}</code>
            </pre>
          </div>
        </div>

        {/* Test Cases Summary */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">
            Test Cases Included
          </h2>
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-md">
              <h3 className="font-semibold text-gray-800">
                Test 1: Admin Login
              </h3>
              <p className="text-gray-600 text-sm">
                Login with seeded credentials (admin/admin) → Verify redirect to
                /home and welcome message.
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-md">
              <h3 className="font-semibold text-gray-800">
                Test 2: Forgot Password (test1)
              </h3>
              <p className="text-gray-600 text-sm">
                Generate temp password for test1 → Capture temp password → Login
                with temp password → Verify success.
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-md">
              <h3 className="font-semibold text-gray-800">
                Test 3: Create Account (test2)
              </h3>
              <p className="text-gray-600 text-sm">
                Register test2/test2/test2 → Verify account created message →
                Login with new credentials → Verify success.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
