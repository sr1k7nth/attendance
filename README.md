# 🚀 **Attendance Tracker – Automated Attendance Scraper**

A lightweight, fast, desktop-ready attendance viewer that logs into JSSATEB's portal, scrapes your attendance using Playwright + Chrome, and displays it through a local Flask web interface.

This app runs as a **standalone .exe** - no Python required for end users.

---

## 📸 Features

* **Login with Student Credentials**
*  **Automated scraping via Playwright (Chrome)**
*  **Detailed Attendance Summary Table**
*  **Absent periods detection**
*  **Target-based calculations (75% & 85%)**
*  **Custom percentage calculator**
*  **Auto-update check** (checks GitHub releases)
*  **Packaged into a single .exe file using PyInstaller**
*  **TailwindCSS UI**

---

## 🛠️ Tech Stack


### **Backend**

* Python
* Flask
* Playwright
* BeautifulSoup (BS4)

### **Frontend**

* HTML
* TailwindCSS
* JavaScript

### **Build**

* PyInstaller (single executable)

---

# Installation (For Developers)

### **1. Install dependencies**

```
pip install -r requirements.txt
```

### **2. Install Playwright & browsers**

```
playwright install
```

> The app automatically finds the installed **Google Chrome** on Windows.

### **3. Run development server**

```
python app.py
```

App will open automatically in your browser at:

```
http://127.0.0.1:5000
```

---

# Build the .EXE File

```
pyinstaller --name attendance-app ^
  --add-data "templates;templates" ^
  --onefile ^
  --icon=catto.ico ^
  app.py
```

Resulting `.exe` will be inside:

```
dist/attendance-app.exe
```

---

# Credentials Safety

User credentials are:

* Used **only locally**
* Never stored
* Never sent to any server other than your portal
* Session memory resets when browser/app closes

---

# Support

If this project helped you, consider giving the repo a **star** on GitHub.
