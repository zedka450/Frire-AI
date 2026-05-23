# frirapi (Frire AI API)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

`frirapi` (also known as Pancakapi) is a lightweight, trilingual (English, French, Spanish) Python module designed to query, train, and manage a synchronized cloud-based knowledge database powered by **Supabase**. It also includes built-in fallback web-scraping via DuckDuckGo Search when local data isn't enough.

Originally built for the **Frire AI** ecosystem, this package allows any Python developer to integrate the AI's core brain directly into their own applications, bots, scripts, or web backends.

---

## Features

* **Cloud Sync:** Instantly fetches and synchronizes structured Q&A data from a Supabase central brain.
* **Smart Matching:** Uses tokenization, string cleaning, and `SequenceMatcher` string similarity algorithms to find the best local answer.
* **Autonomous Learning:** Real-time feedback loop that dynamically adjusts the confidence/reliability scores of answers in the cloud database.
* **Web Fallback:** Automatically scrapes trusted web sources (Wikipedia, Larousse, Britannica, etc.) if local knowledge confidence is low.
* **Trilingual Translation:** Automatically handles incoming queries and returns localized answers in English, French, or Spanish using `deep-translator`.
* **Adaptive Response Styles:** Choose between `courte` (short), `normale` (normal), or `detaillee` (detailed) outputs.
* **Hot-Reload Auto-Updater:** Update the package to the latest version at runtime without restarting your script.

---

## Installation

Install the package and its requirements using your favorite package manager:

```bash
pip install frirapi 
uv pip install firapi
poetry add frirapi@latest
```
and more package manager...

---

## Quick Start Guide
Here is how you can fetch the database and start chatting with the AI core:

```python
import frirapi

# 1. Initialize and load the central brain from the Cloud
print("Loading database...")
brain_database = frirapi.charger_base()

# 2. Define a question and preferred settings
user_question = "What is an Hantavirus?"
response_style = "normale"  # Options: "short", "normal", "detailed"
language = "en"             # Options: "en", "fr", "es"

# 3. Query the AI
response, confidence, exact_match = frirapi.ia_repond(
    question=user_question, 
    BASE_DE_DONNEES=brain_database, 
    style_actuel=response_style, 
    langue_ia=language
)

# 4. Format and print the final result
if response:
    final_output = frirapi.varier_reponse(response, response_style, user_question)
    print(f"AI Response: {final_output}")
    print(f"Confidence Score: {confidence}%")
    print(f"Source/Match: {exact_match}")
else:
    print("The AI does not know the answer.")
```

---

## Database Interaction & Learning Loop
#### 1. Training the AI (Confidence adjustment)
If the AI answered a question using an existing database entry (exact_match), you can supply a feedback loop to let it learn and save the new weight directly to Supabase:

```python
# Assuming the user validated the response:
is_correct = True  # Set to False if the answer was wrong

if exact_match and not exact_match.startswith("[WEB]"):
    frirapi.ia_apprend(exact_match, is_correct, brain_database)
```

#### 2. Manually adding knowledge to the Cloud
You can contribute directly to the global brain by pushing a new question, answer, and category ("sciences", "maths", or "culture"):

```python
frirapi.ajouter_a_supabase(
    question="What is 2+2?", 
    reponse="4", 
    categorie="maths"
)
```

---

## Hot-Reload Auto-Updater (State)
frirapi comes with an built-in runtime module updater. If you want to make sure your scripts are always using the latest release without manual re-deployments or application restarts, you can call the State.UpdateModule method:

```python
import frirapi

# Update package at runtime using your preferred package environment
# Supported modes: "pip", "uv", "poetry", "conda", "git"
frirapi = frirapi.State.UpdateModule(mode="uv")
# The module is now updated and reloaded into memory!
```

---

## License
This project is licensed under the GNU General Public License v3.0 (GPL-3.0). See the LICENSE file for more details.

## Contact & Support
Creator: ZedKa450

Discord: zedka450

E-mail: zedka.le.vrai.pro@gmail.com

GitHub Repository: https://github.com/zedka450/Frire-AI
