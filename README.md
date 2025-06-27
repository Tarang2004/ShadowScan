Perfect — since your project uses **Flask with a web-based GUI**, here’s an updated, comprehensive **README.md** tailored to your `app.py` setup. This version explains that it’s a web app, how to install, run, and use it, and how the endpoints work.

---

# 🚨 ShadowScan – Dark Web Threat Intelligence Web App

**ShadowScan** is a web-based cybersecurity tool that scans dark web (.onion) sites for potential data leaks and generates professional PDF reports.
It connects to the dark web via Tor, uses regex + AI to find personal data, classifies threat levels, and provides an interactive Flask web interface.

⚠ **For educational and research purposes only. Use responsibly.**

---

## 🌟 Features

✅ Web-based GUI with Flask
✅ Connects securely through Tor SOCKS5 proxy
✅ Scrapes text content from dark web sites
✅ Detects emails, phone numbers, and personal info (names, organizations)
✅ Classifies threat levels (None / Low / Medium)
✅ Generates downloadable PDF reports
✅ REST API endpoints for automation
✅ Includes a legal disclaimer

---

## 📂 Example Use Cases

* Threat intelligence analysts monitoring dark web leaks
* Security researchers exploring PII exposure
* Ethical hacking and cybersecurity education

---

## ⚙️ Requirements

* Python 3.8+
* Tor running locally (default port 9150)
* Your existing `requirements.txt`

Install Python dependencies:

```bash
pip install -r requirements.txt
```

✅ **Install Tor browser or Tor daemon** and make sure it is running:

* Tor browser → Start it, wait until connected
* Or start Tor daemon → `tor`

---

## 🚀 Running the App

After installing dependencies and ensuring Tor is running:

```bash
python app.py
```

You should see something like:

```
 * Running on http://127.0.0.1:5000/
```

Open your browser and go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/) to use the web interface.

---

## 🖥 Web Interface

* Enter `.onion` URLs (one per line) in the form.
* Click **Scan** to start scanning.
* Once finished, download the generated PDF report.

---

## 🛠 API Endpoints

### `GET /`

* Serves the HTML GUI (index page).

### `POST /scan`

* Accepts JSON payload with a list of URLs:

```json
{
  "urls": "http://example1.onion\nhttp://example2.onion"
}
```

* Returns JSON results including findings and report filename.

### `GET /download/<filename>`

* Downloads the generated PDF report.

Example: [http://127.0.0.1:5000/download/ShadowScan\_Report\_YYYYMMDD\_HHMMSS.pdf](http://127.0.0.1:5000/download/ShadowScan_Report_YYYYMMDD_HHMMSS.pdf)

---

## 📌 Configuration

* `scanner.py` handles the scanning logic, Tor configuration, regex + NLP analysis, and PDF generation.
* `app.py` provides the web GUI and REST API.

---

## ⚠ Legal Disclaimer

```
This tool is provided for educational and research purposes only.
The developer assumes no liability for misuse or damages.
The user is responsible for complying with applicable laws.
Accessing dark web content may be illegal in some jurisdictions.
```

---

## 📄 License

MIT License (or your chosen license).

---

## 🙌 Acknowledgments

* [Flask](https://flask.palletsprojects.com/)
* [Tor Project](https://www.torproject.org/)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
* [HuggingFace Transformers](https://huggingface.co/transformers/)
* [dbmdz BERT NER model](https://huggingface.co/dbmdz/bert-large-cased-finetuned-conll03-english)

---

✅ **Ready to get started?** Run `python app.py` and open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser!

---

Would you like help styling your HTML GUI (`index.html`) to make it look more polished?
