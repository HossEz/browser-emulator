import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import json

# Initialize driver as None globally
driver = None

# File to save proxy settings
PROXY_SETTINGS_FILE = "proxy_settings.json"

# Function to save proxy settings
def save_proxy_settings():
    proxy_settings = {
        "address": proxy_address_var.get(),
        "port": proxy_port_var.get(),
        "protocol": proxy_protocol_var.get()
    }
    with open(PROXY_SETTINGS_FILE, "w") as f:
        json.dump(proxy_settings, f)
    messagebox.showinfo("Info", "Proxy settings saved!")

# Function to load proxy settings
def load_proxy_settings():
    if os.path.exists(PROXY_SETTINGS_FILE):
        with open(PROXY_SETTINGS_FILE, "r") as f:
            proxy_settings = json.load(f)
        proxy_address_var.set(proxy_settings.get("address", ""))
        proxy_port_var.set(proxy_settings.get("port", ""))
        proxy_protocol_var.set(proxy_settings.get("protocol", "http"))

def start_browser():
    global driver  # Use the global driver variable

    device_profile = device_var.get()
    proxy_address = proxy_address_var.get()
    proxy_port = proxy_port_var.get()
    proxy_protocol = proxy_protocol_var.get()

    chrome_options = Options()
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-features=WebRtcHideLocalIpsWithMdns")
    chrome_options.add_argument("--remote-debugging-port=0")

    # Disable WebGL and Canvas fingerprinting
    chrome_options.add_argument("--disable-webgl")
    chrome_options.add_argument("--disable-3d-apis")
    chrome_options.add_argument("--disable-reading-from-canvas")

    # Disable Automation Controllers
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Device-specific configuration
    if device_profile == 'iPhone':
        # Mobile emulation for iPhone
        mobile_emulation = {
            "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        window_width, window_height = 390, 844  # iPhone window size
    elif device_profile == 'Desktop':
        # Regular Chrome on Desktop
        window_width, window_height = 1200, 800  # Default window size for Desktop

    # Proxy configuration
    if proxy_address and proxy_port and proxy_protocol:
        proxy = f"{proxy_protocol}://{proxy_address}:{proxy_port}"
        chrome_options.add_argument(f'--proxy-server={proxy}')

    try:
        # Start the browser
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_window_size(window_width, window_height)  # Set window size based on device
        driver.get("https://myip.wtf/")

        # Set navigator properties via JavaScript to further spoof the browser identity
        if device_profile == 'iPhone':
            driver.execute_script("""
                // Spoof User-Agent and other navigator properties
                Object.defineProperty(navigator, 'userAgent', {get: function(){return 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';}});
                Object.defineProperty(navigator, 'platform', {get: function(){return 'iPhone';}});
                Object.defineProperty(navigator, 'vendor', {get: function(){return 'Apple Computer, Inc.';}});
                Object.defineProperty(navigator, 'maxTouchPoints', {get: function(){return 5;}});
                Object.defineProperty(navigator, 'hardwareConcurrency', {get: function(){return 6;}});
                Object.defineProperty(navigator, 'deviceMemory', {get: function(){return 4;}});
                Object.defineProperty(navigator, 'webdriver', {get: function(){return false;}}); // Disable webdriver flag
                Object.defineProperty(navigator, 'languages', {get: function(){return ['en-US', 'en'];}});
                Object.defineProperty(navigator, 'plugins', {get: function(){return [];}});

                // Redefine the screen size to match the emulated device
                Object.defineProperty(screen, 'width', {get: function() { return 390; }});
                Object.defineProperty(screen, 'height', {get: function() { return 844; }});
                Object.defineProperty(screen, 'availWidth', {get: function() { return 390; }});
                Object.defineProperty(screen, 'availHeight', {get: function() { return 844; }});
                Object.defineProperty(screen, 'colorDepth', {get: function() { return 24; }});
                Object.defineProperty(screen, 'pixelDepth', {get: function() { return 24; }});

                // Redefine the window size
                Object.defineProperty(window, 'innerWidth', {get: function() { return 390; }});
                Object.defineProperty(window, 'innerHeight', {get: function() { return 844; }});
                Object.defineProperty(window, 'outerWidth', {get: function() { return 390; }});
                Object.defineProperty(window, 'outerHeight', {get: function() { return 844; }});
            """)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start browser: {str(e)}")
        driver = None  # Reset driver if browser fails to start

def close_browser():
    global driver
    if driver is not None:
        driver.quit()
        driver = None  # Reset driver after closing
    else:
        messagebox.showinfo("Info", "No browser is currently open.")

# GUI Setup
app = tk.Tk()
app.title('Browser Emulator')

# Dropdown for device selection
device_var = tk.StringVar(value="iPhone")  # Set "iPhone" as the default selected option
device_choices = ['iPhone', 'Desktop']  # Available options
device_dropdown = ttk.Combobox(app, textvariable=device_var, values=device_choices, state="readonly")
device_dropdown.grid(column=0, row=0, padx=10, pady=10)

# Proxy configuration fields
proxy_address_var = tk.StringVar()
proxy_port_var = tk.StringVar()
proxy_protocol_var = tk.StringVar(value="http")  # Default protocol

ttk.Label(app, text="Proxy Address:").grid(column=0, row=1, padx=10, pady=5)
ttk.Entry(app, textvariable=proxy_address_var).grid(column=1, row=1, padx=10, pady=5)

ttk.Label(app, text="Proxy Port:").grid(column=0, row=2, padx=10, pady=5)
ttk.Entry(app, textvariable=proxy_port_var).grid(column=1, row=2, padx=10, pady=5)

ttk.Label(app, text="Proxy Protocol:").grid(column=0, row=3, padx=10, pady=5)
ttk.Combobox(app, textvariable=proxy_protocol_var, values=["http", "https", "socks5"]).grid(column=1, row=3, padx=10, pady=5)

# Buttons
start_button = ttk.Button(app, text='Start Browser', command=start_browser)
start_button.grid(column=0, row=4, padx=10, pady=10)
close_button = ttk.Button(app, text='Close Browser', command=close_browser)
close_button.grid(column=1, row=4, padx=10, pady=10)

# Save and Load Proxy Settings
save_button = ttk.Button(app, text='Save Proxy', command=save_proxy_settings)
save_button.grid(column=1, row=0, padx=10, pady=10)

# Load proxy settings when the app starts
load_proxy_settings()

app.mainloop()