#!/usr/bin/env python3
"""
Creator: ZedKa450
Frire API (frirapi), or Pancake API (pancakapi)
First published version date: 23/05/2026
This project is licensed under the GNU General Public License v3.0 (GPL-3.0)
Contact: zedka450 on Discord or zedka.le.vrai.pro@gmail.com by e-mail
"""

from supabase import create_client
from ddgs import DDGS 
import re
from deep_translator import GoogleTranslator
from difflib import SequenceMatcher


SUPABASE_URL = "https://givazljlcyrcvmkstvgz.supabase.co"
SUPABASE_KEY = "sb_publishable_IXeKK1bSStuQ8PjEYFZwQw_z4P_ZCCC"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

from .__update__ import State

def charger_base():
    try:
        print("Synchronization with Supabase...")
        response = supabase.table("questions").select("*").execute()
        data = response.data
        base = {"sciences": [], "maths": [], "culture": []}
        for item in data:
            cat = item.get('categorie', 'culture')
            if cat in base:
                base[cat].append({
                    "question": item['question'],
                    "reponse": item['reponse'],
                    "confiance": item.get('confiance', 50)
                })
        print(f"{len(data)} questions charged from the Cloud!")
        return base
    except Exception as e:
        print(f"Error connecting to the server: {e}")
        return {"sciences": [], "maths": [], "culture": []}

def ia_apprend(correct, BASE_DE_DONNEES):
    try:
        for cat, questions in BASE_DE_DONNEES.items():
            for q in questions:
                if q["question"] == BASE_DE_DONNEES.get("last_question"):
                    ancienne_confiance = q.get('confiance', 50)
                    nouvelle_confiance = min(ancienne_confiance + 10, 100) if correct else max(ancienne_confiance - 15, 0)
                    q['confiance'] = nouvelle_confiance
                    supabase.table("questions").update({"confiance": nouvelle_confiance}).eq("question", BASE_DE_DONNEES.get("last_question")).execute()
                    print(f"Cloud server synchronized and updated: {nouvelle_confiance}%")
                    return
    except Exception as e:
        print(f"Error during Cloud synchronization: {e}")

def ajouter_a_supabase(question, reponse, categorie):
    try:
        data = {"question": question, "reponse": reponse, "categorie": categorie, "confiance": 50}
        supabase.table("questions").insert(data).execute()
        print("Question successfully sent to the central brain!")
    except Exception as e:
        print(f"Error during data insertion: {e}")

def nettoyer(texte):
    texte = texte.lower().strip()
    remplacements = {"é": "e", "è": "e", "ê": "e", "ë": "e", "à": "a", "â": "a", "ù": "u", "û": "u", "ô": "o", "î": "i", "ï": "i"}
    for car, rep in remplacements.items():
        texte = texte.replace(car, rep)
    return texte.replace("'", " ").replace("-", " ")

def mots_proches(mot1, mot2):
    return SequenceMatcher(None, mot1, mot2).ratio()

def score_similarite(phrase_user, phrase_bdd):
    mots_user = nettoyer(phrase_user).split()
    mots_bdd = nettoyer(phrase_bdd).split()
    if not mots_user or not mots_bdd: return 0
    mots_trouves = 0
    for m_bdd in mots_bdd:
        for m_user in mots_user:
            if m_bdd == m_user or mots_proches(m_user, m_bdd) > 0.7:
                mots_trouves += 1
                break 
    total_mots_uniques = len(set(mots_user) | set(mots_bdd))
    return mots_trouves / total_mots_uniques if total_mots_uniques else 0

def extraire_sujet(question):
    q = nettoyer(question).rstrip("? .!\n")
    if q.startswith("est ce que"): q = q.replace("est ce que", "").strip()
    patterns = [("de quelle", "est "), ("de quel", "est "), ("quel", "est "), ("quelle", "est "), ("qui", "est "), ("où", "est "), ("qu est ce que", "est ")]
    for debut, separateur in patterns:
        if debut in q and separateur in q:
            partie = q.split(separateur, 1)[1].strip()
            if partie: return partie.capitalize()
    if "est" in q:
        sujet = q.split("est", 1)[0].strip()
        if sujet and sujet not in ["c", "qu"]: return sujet.capitalize()
    return None

def reponse_courte(question, reponse):
    mots = reponse.split()
    sujet = extraire_sujet(question)
    if sujet and len(mots) <= 3 and not reponse.endswith("."): return f"{sujet} est {reponse}."
    if len(mots) <= 10: return reponse.capitalize() if reponse and reponse[0].islower() else reponse
    return "{}...".format(" ".join(mots[:10]).rstrip(" ,.;:"))

def reponse_detaillee(question, reponse):
    sujet = extraire_sujet(question)
    base = f"{sujet} est {reponse}." if (sujet and len(reponse.split()) <= 3 and not reponse.endswith(".")) else (reponse if reponse.endswith(".") else f"{reponse}.")
    if "couleur" in nettoyer(question): return f"{base} La couleur peut changer selon la lumière et l'heure de la journée."
    if "pourquoi" in nettoyer(question) or "comment" in nettoyer(question): return f"{base} C'est une bonne question qui mérite une explanation."
    return f"{base}"

def varier_reponse(reponse, style, question):
    if style == "short": return reponse_courte(question, reponse)
    if style == "detailed": return reponse_detaillee(question, reponse)
    return reponse if reponse.endswith(".") else f"{reponse}."

def extraire_phrases(texte, nb_phrases):
    phrases = re.split(r'(?<=[.!?]) +', texte.strip())
    return " ".join(phrases[:nb_phrases])

def chercher_web(question, style="normal", langue_ia="en"):
    try:
        print(" Web search in progress on verified sources...")
        sites_fiables = ["wikipedia.org", "larousse.fr", "futura-sciences.com", "lemonde.fr", "britannica.com"]
        query_sites = " OR ".join([f"site:{s}" for s in sites_fiables])
        requete_complete = f"({query_sites}) {question}"

        with DDGS() as ddgs:
            reg = "us-en" if langue_ia == "en" else f"{langue_ia}-{langue_ia.upper()}"
            results = [r for r in ddgs.text(requete_complete, region=reg, max_results=2)]
            
            if results and 'body' in results[0]:
                texte_brut = results[0]['body']
                texte_brut = re.sub(r'^(il y a \d+ (jours|heures|mois)|[^-\n]*ago)\s*[-·]\s*', '', texte_brut, flags=re.IGNORECASE)
                source_url = results[0]['href']
                nom_site = source_url.split('/')[2].replace("www.", "")

                if langue_ia != "fr":
                    try:
                        texte_brut = GoogleTranslator(source='auto', target=langue_ia).translate(texte_brut)
                    except Exception: pass

                if style == "short": texte_final = extraire_phrases(texte_brut, 1)
                elif style == "detailed": texte_final = extraire_phrases(texte_brut, 5)
                else: texte_final = extraire_phrases(texte_brut, 2)

                return texte_final, f"Source: {nom_site}"
    except Exception as e:
        print(f"Error during web search: {e}")
    return None, None

def ia_repond(question, BASE_DE_DONNEES, style_actuel="normal", langue_ia="en"):
    q_nettoyee = nettoyer(question)
    toutes_questions = [(q, cat) for cat, qs in BASE_DE_DONNEES.items() for q in qs]
    meilleur_score, meilleure_q = 0, None

    for q, cat in toutes_questions:
        score = score_similarite(q_nettoyee, q["question"])
        if score > meilleur_score: meilleur_score, meilleure_q = score, q

    if meilleur_score > 0.25 and meilleure_q:
        reponse_brute = meilleure_q["reponse"]
        if langue_ia != "fr":
            try: reponse_brute = GoogleTranslator(source='fr', target=langue_ia).translate(reponse_brute)
            except Exception: pass
        return reponse_brute, meilleure_q.get("confiance", 50), meilleure_q["question"]
    
    reponse_internet, source = chercher_web(question, style=style_actuel, langue_ia=langue_ia)
    if reponse_internet:
        return reponse_internet, 100, f"[WEB] {source}"

    return None, 0, None
