import requests
import re
from bs4 import BeautifulSoup
from fpdf import FPDF
import datetime
import socks
import socket
from transformers import pipeline

# --- Configuration ---
# Tor SOCKS5 proxy address
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 9150

USE_NLP_FOR_PII = True

# --- Disclaimer ---
DISCLAIMER = """
[!] LEGAL DISCLAIMER:
This tool is provided for educational and research purposes only. The developer assumes no liability and is not responsible for any misuse or damage caused by this program. The user is solely responsible for their actions and must comply with all applicable laws. Accessing dark web content may be illegal in your jurisdiction. Use at your own risk.
Developed By Tarang Solanki
ID-22IT553
"""

# --- Functions ---

def check_tor_connection():
    """Checks if the connection to the Tor proxy is working."""
    print("[*] Checking Tor SOCKS proxy connection...")
    try:
        original_socket = socket.socket
        socks.set_default_proxy(socks.SOCKS5, PROXY_HOST, PROXY_PORT)
        socket.socket = socks.socksocket
        
        response = requests.get("https://check.torproject.org/api/ip")
        response.raise_for_status()
        
        socket.socket = original_socket
        
        data = response.json()
        if data.get("IsTor"):
            print(f"[+] Tor connection successful! Your Tor IP is: {data.get('IP')}")
            return True, ""
        else:
            print("[-] Connected, but not via Tor.")
            return False, "Connected, but not via Tor."
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to connect to Tor proxy: {e}"
        print(f"[-] {error_msg}")
        print(f"[-] Please ensure Tor is running and the SOCKS5 proxy is available at {PROXY_HOST}:{PROXY_PORT}.")
        return False, error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred during Tor check: {e}"
        print(f"[-] {error_msg}")
        return False, error_msg
    finally:
        socket.socket = original_socket


def scrape_onion_site(url):
    """Scrapes a single .onion site for its text content."""
    print(f"\n[*] Scraping: {url}")
    proxies = {
        'http': f'socks5h://{PROXY_HOST}:{PROXY_PORT}',
        'https': f'socks5h://{PROXY_HOST}:{PROXY_PORT}'
    }
    try:
        response = requests.get(url, proxies=proxies, timeout=60)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        text = soup.get_text(separator=' ', strip=True)
        print(f"[+] Successfully scraped site. Content length: {len(text)} chars.")
        return text
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to scrape {url}. Reason: {e}")
        return None
    except Exception as e:
        print(f"[-] An unexpected error occurred during scraping: {e}")
        return None

def find_leaks_with_regex(text):
    """Uses regex to find potential leaks in a given text."""
    leaks = {
        'emails': [],
        'phones': [],
    }
    
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    leaks['emails'] = list(set(re.findall(email_pattern, text)))
    
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    leaks['phones'] = list(set(re.findall(phone_pattern, text)))

    found_count = sum(len(v) for v in leaks.values())
    if found_count > 0:
        print(f"[+] Found {found_count} potential leak(s) via regex.")

    return leaks

def find_pii_with_nlp(text, nlp_pipeline):
    """Uses a transformer model to find PII like names and organizations."""
    print("[*] Analyzing text with NLP model for PII (names, organizations)...")
    text_to_analyze = text[:2000]
    
    try:
        results = nlp_pipeline(text_to_analyze)
        pii = {'PER': [], 'ORG': [], 'LOC': []}
        for entity in results:
            if entity['entity_group'] in pii:
                pii[entity['entity_group']].append(entity['word'])
        
        for key in pii:
            pii[key] = list(set(pii[key]))

        found_count = sum(len(v) for v in pii.values())
        if found_count > 0:
            print(f"[+] Found {found_count} PII entities via NLP.")

        return pii
    except Exception as e:
        print(f"[-] NLP analysis failed: {e}")
        return {}


def classify_threat(regex_leaks, nlp_leaks=None):
    """Classifies the threat level based on the leaks found."""
    has_regex_leaks = any(regex_leaks.values())
    has_nlp_leaks = nlp_leaks and any(nlp_leaks.values())

    if not has_regex_leaks and not has_nlp_leaks:
        return "None"

    if nlp_leaks and nlp_leaks.get('PER'):
        return "Medium"

    if has_regex_leaks:
        return "Low"
        
    return "Info"

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'ShadowScan Dark Web Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Report Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, body)
        self.ln()

def generate_pdf_report(findings):
    """Generates a PDF report and returns its file path."""
    if not findings:
        print("[*] No findings to report. PDF will not be generated.")
        return None

    print("\n[*] Generating PDF report...")
    pdf = PDF()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 20, 'ShadowScan Intelligence Report', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 5, DISCLAIMER)
    pdf.ln(10)

    pdf.chapter_title('Scan Summary')
    summary = f"Scan completed, finding potential leaks across {len(findings)} sites."
    pdf.chapter_body(summary)

    for find in findings:
        pdf.add_page()
        pdf.chapter_title(f"Source: {find['url']}")
        
        meta_body = (
            f"Timestamp: {find['timestamp']}\n"
            f"Threat Level: {find['threat']}"
        )
        pdf.chapter_body(meta_body)
        
        if any(find['regex_leaks'].values()):
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 10, "Found via Regex:", 0, 1, 'L')
            for leak_type, items in find['regex_leaks'].items():
                if items:
                    body = f"- {leak_type.capitalize()}: {', '.join(items)}"
                    pdf.chapter_body(body)

        if find.get('nlp_leaks') and any(find['nlp_leaks'].values()):
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 10, "Found via AI/NLP (PII):", 0, 1, 'L')
            for pii_type, items in find['nlp_leaks'].items():
                if items:
                    pii_map = {'PER': 'Persons', 'ORG': 'Organizations', 'LOC': 'Locations'}
                    body = f"- {pii_map.get(pii_type, pii_type)}: {', '.join(items)}"
                    pdf.chapter_body(body)

    report_name = f"ShadowScan_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(report_name)
    print(f"[+] Report successfully generated: {report_name}")
    return report_name

def run_scan(target_urls_string):
    """Main function to run the ShadowScan tool, returns findings."""
    tor_ok, tor_error = check_tor_connection()
    if not tor_ok:
        return {"error": f"Tor connection failed: {tor_error}"}

    nlp_pipeline_instance = None
    if USE_NLP_FOR_PII:
        try:
            print("[*] Initializing NLP model for PII detection...")
            nlp_pipeline_instance = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", grouped_entities=True)
            print("[+] NLP model loaded successfully.")
        except Exception as e:
            print(f"[-] Could not load NLP model. Error: {e}")
            return {"error": f"Could not initialize NLP model: {e}"}

    target_urls = [url.strip() for url in target_urls_string.splitlines() if url.strip()]
    if not target_urls:
        return {"error": "No target URLs provided."}

    all_findings = []
    print(f"\n[*] Starting scan of {len(target_urls)} target site(s)...")
    for url in target_urls:
        scraped_text = scrape_onion_site(url)
        if scraped_text:
            regex_leaks = find_leaks_with_regex(scraped_text)
            nlp_leaks = {}
            
            if USE_NLP_FOR_PII and nlp_pipeline_instance:
                nlp_leaks = find_pii_with_nlp(scraped_text, nlp_pipeline_instance)
                
            threat_level = classify_threat(regex_leaks, nlp_leaks)
            
            if threat_level != "None":
                print(f"    -> Threat Level: {threat_level}")
                all_findings.append({
                    'url': url,
                    'regex_leaks': regex_leaks,
                    'nlp_leaks': nlp_leaks,
                    'threat': threat_level,
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

    report_path = generate_pdf_report(all_findings)

    print("\n[*] ShadowScan scan finished.")
    return {"findings": all_findings, "report_path": report_path} 