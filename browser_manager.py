import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import json
import random

# Initialize driver as None globally
driver = None

# File to save proxy settings
PROXY_SETTINGS_FILE = "proxy_settings.json"

# List of user agents for spoofing
user_agents = [
    # Desktop User Agents
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",

    # iPhone User Agents
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0.0.0 Mobile/15E148 Safari/604.1",

    # Android User Agents
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36 EdgA/131.0.0.0"
]

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

# Function to generate a random spoofed configuration
def generate_spoofed_config(device_profile):
    # Filter user agents based on the selected device profile
    if device_profile == 'Phone':
        # Only use iPhone or Android user agents
        phone_user_agents = [ua for ua in user_agents if "iPhone" in ua or "Android" in ua]
        user_agent = random.choice(phone_user_agents)
    elif device_profile == 'Random':
        # Use any user agent
        user_agent = random.choice(user_agents)
    else:
        # Use desktop user agents
        desktop_user_agents = [ua for ua in user_agents if "Windows" in ua or "Macintosh" in ua]
        user_agent = random.choice(desktop_user_agents)

    spoofed_config = {
        "user_agent": user_agent,
        "language": random.choice([
            "en-US", "en-GB", "fr-FR", "de-DE", "es-ES", "it-IT", "ja-JP", "ko-KR", 
            "zh-CN", "ru-RU", "pt-BR", "ar-SA", "hi-IN", "nl-NL", "sv-SE", "pl-PL", 
            "tr-TR", "da-DK", "fi-FI", "no-NO", "cs-CZ", "el-GR", "he-IL", "hu-HU", 
            "ro-RO", "th-TH", "vi-VN", "id-ID", "ms-MY", "fil-PH"
        ]),
        "timezone": random.choice([
            "America/New_York", "America/Los_Angeles", "America/Chicago", "America/Denver",
            "America/Toronto", "America/Vancouver", "America/Mexico_City", "America/Sao_Paulo",
            "America/Buenos_Aires", "Europe/London", "Europe/Paris", "Europe/Berlin",
            "Europe/Rome", "Europe/Madrid", "Europe/Moscow", "Europe/Istanbul",
            "Asia/Tokyo", "Asia/Shanghai", "Asia/Hong_Kong", "Asia/Singapore",
            "Asia/Dubai", "Asia/Kolkata", "Asia/Seoul", "Asia/Bangkok",
            "Australia/Sydney", "Australia/Melbourne", "Pacific/Auckland", "Africa/Cairo",
            "Africa/Johannesburg", "Atlantic/Reykjavik", "Indian/Maldives", "Pacific/Honolulu"
        ]),
        "hardware_concurrency": random.randint(2, 8),
        "device_memory": random.randint(2, 8),
        "screen_width": random.randint(800, 1920),
        "screen_height": random.randint(600, 1080),
    }
    return spoofed_config

# Function to start the browser with spoofed configuration
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

    # Generate spoofed configuration
    spoofed_config = generate_spoofed_config(device_profile)

    # Apply spoofed user agent
    chrome_options.add_argument(f"--user-agent={spoofed_config['user_agent']}")

    # Device-specific configuration
    if device_profile == 'Phone':
        # Randomly select between iPhone and Android
        phone_type = random.choice(['iPhone', 'Android'])
        if phone_type == 'iPhone':
            # Mobile emulation for iPhone
            mobile_emulation = {
                "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
                "userAgent": spoofed_config["user_agent"]
            }
            chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
            window_width, window_height = 390, 844  # iPhone window size
        else:
            # Mobile emulation for Android
            mobile_emulation = {
                "deviceMetrics": {"width": 360, "height": 800, "pixelRatio": 3.0},
                "userAgent": spoofed_config["user_agent"]
            }
            chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
            window_width, window_height = 360, 800  # Android window size
    elif device_profile == 'Random':
        # Randomly select between iPhone, Android, or Desktop
        random_device = random.choice(['iPhone', 'Android', 'Desktop'])
        if random_device == 'iPhone':
            mobile_emulation = {
                "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
                "userAgent": spoofed_config["user_agent"]
            }
            chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
            window_width, window_height = 390, 844  # iPhone window size
        elif random_device == 'Android':
            mobile_emulation = {
                "deviceMetrics": {"width": 360, "height": 800, "pixelRatio": 3.0},
                "userAgent": spoofed_config["user_agent"]
            }
            chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
            window_width, window_height = 360, 800  # Android window size
        else:
            # Desktop
            window_width, window_height = spoofed_config["screen_width"], spoofed_config["screen_height"]
    else:
        # Desktop
        window_width, window_height = spoofed_config["screen_width"], spoofed_config["screen_height"]

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

        # Set additional spoofed properties via JavaScript
        driver.execute_script(f"""
            // Spoof time zone
            Object.defineProperty(Intl, 'DateTimeFormat', {{get: function(){{return () => {{timeZone: '{spoofed_config["timezone"]}'}};}}}});

            // Spoof screen properties
            Object.defineProperty(screen, 'width', {{get: function() {{ return {spoofed_config["screen_width"]}; }}}});
            Object.defineProperty(screen, 'height', {{get: function() {{ return {spoofed_config["screen_height"]}; }}}});
            Object.defineProperty(screen, 'availWidth', {{get: function() {{ return {spoofed_config["screen_width"]}; }}}});
            Object.defineProperty(screen, 'availHeight', {{get: function() {{ return {spoofed_config["screen_height"]}; }}}});
            Object.defineProperty(screen, 'colorDepth', {{get: function() {{ return 24; }}}});
            Object.defineProperty(screen, 'pixelDepth', {{get: function() {{ return 24; }}}});

            // Spoof hardware properties
            Object.defineProperty(navigator, 'hardwareConcurrency', {{get: function(){{return {spoofed_config["hardware_concurrency"]};}}}});
            Object.defineProperty(navigator, 'deviceMemory', {{get: function(){{return {spoofed_config["device_memory"]};}}}});
        """)

        # Build spoofing summary message
        spoofing_summary = (
            "Browser started with the following spoofed configuration:\n\n"
            f"Device Profile: {device_profile}\n"
            f"User Agent: {spoofed_config['user_agent']}\n"
            f"Language: {spoofed_config['language']}\n"
            f"Time Zone: {spoofed_config['timezone']}\n"
            f"Screen Size: {spoofed_config['screen_width']}x{spoofed_config['screen_height']}\n"
            f"Hardware Concurrency: {spoofed_config['hardware_concurrency']}\n"
            f"Device Memory: {spoofed_config['device_memory']} GB\n"
        )

        # Add proxy information if configured
        if proxy_address and proxy_port and proxy_protocol:
            spoofing_summary += f"Proxy: {proxy_address}:{proxy_port} ({proxy_protocol})"
        else:
            spoofing_summary += "Proxy: None"

        messagebox.showinfo("Spoofing Summary", spoofing_summary)
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
device_var = tk.StringVar(value="Random")  # Set "Random" as the default selected option
device_choices = ['Random', 'Phone', 'Desktop']  # Available options
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