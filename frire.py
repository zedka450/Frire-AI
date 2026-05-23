"""!/usr/bin/env python3
Creator: ZedKa450
Frire AI, or Pancake AI
First published version date: 05/05/26
This project is licensed under the GNU General Public License v3.0 (GPL-3.0)
Contact: zedka450 on Discord or zedka.le.vrai.pro@gmail.com by e-mail"""

import os
import json
from supabase import create_client
from ddgs import DDGS 
import re
from deep_translator import GoogleTranslator
from difflib import SequenceMatcher
import locale
import speech_recognition as sr
import pyttsx3

try:
    langue_systeme = locale.getlocale()[0] or locale.getdefaultlocale()[0]
    langue_ia = langue_systeme.split('_')[0] if langue_systeme else "fr"
except Exception:
    langue_ia = "fr"

LEXIQUE = {
    "fr": {
        "titre": "Frire IA", "menu1": "  [1] Poser une question", "menu2": "  [2] Choisir le style de réponse",
        "menu3": "  [3] Ajouter au Cloud", "menu4": "  [4] Paramètres Audio", "menu5": "  [5] Quitter", 
        "style_actuel": "Style actuel", "choix": "  → Choix : ",
        "ta_question": "\n Ta question : ", "correct": " Est-ce correct ? (o/n) : ", "inconnu": " L'IA ne sait pas, même après recherche web.",
        "select_style": "\n Sélectionne un style :", "style_c": "  [1] Courte", "style_n": "  [2] Normale", "style_d": "  [3] Détaillée",
        "style_choisi": " Style choisi : ", "question_cl": "\n Question : ", "reponse_cl": " Réponse  : ", "cat_cl": " Catégorie [1] Sc [2] Mat [3] Cul : ",
        "config_titre": "\n--- CONFIGURATION AUDIO ---", "statut_tts": "TTS (Synthèse vocale)", "statut_sr": "Reconnaissance vocale",
        "demande_tts": "Activer le TTS ? (o/n) : ", "demande_sr": "Activer la reconnaissance vocale ? (o/n) : ",
        "confirm_tts": "TTS activé: les réponses de l'IA seront lues à haute voix.",
        "confirm_sr": "Reconnaissance vocale activée: tu pourras poser tes questions à l'oral.",
        "audio_ok": "Paramètres appliqués avec succès !", "actif": "Activé", "desactif": "Désactivé"
    },
    "en": {
        "titre": "Frire AI", "menu1": "  [1] Ask a question", "menu2": "  [2] Choose response style",
        "menu3": "  [3] Add to Cloud", "menu4": "  [4] Audio Settings", "menu5": "  [5] Quit", 
        "style_actuel": "Current style", "choix": "  → Choice: ",
        "ta_question": "\n Your question: ", "correct": " Is this correct? (y/n): ", "inconnu": " The AI doesn't know, even after web search.",
        "select_style": "\n Select a style:", "style_c": "  [1] Short", "style_n": "  [2] Normal", "style_d": "  [3] Detailed",
        "style_choisi": " Chosen style: ", "question_cl": "\n Question: ", "reponse_cl": " Answer: ", "cat_cl": " Category [1] Sc [2] Math [3] Cult: ",
        "config_titre": "\n--- AUDIO CONFIGURATION ---", "statut_tts": "TTS (Text-to-Speech)", "statut_sr": "Speech Recognition",
        "demande_tts": "Enable TTS? (y/n): ", "demande_sr": "Enable speech recognition? (y/n): ",
        "confirm_tts": "TTS enabled: AI responses will be read out loud.",
        "confirm_sr": "Speech recognition enabled: you can ask your questions verbally.",
        "audio_ok": "Settings applied successfully!", "actif": "Enabled", "desactif": "Disabled"
    },
    "es": {
        "titre": "Frire IA ", "menu1": "  [1] Hacer una pregunta", "menu2": "  [2] Elegir estilo de respuesta",
        "menu3": "  [3] Añadir a la nube", "menu4": "  [4] Ajustes de Audio", "menu5": "  [5] Salir", 
        "style_actuel": "Estilo actual", "choix": "  → Elección: ",
        "ta_question": "\n Tu pregunta: ", "correct": " ¿Es correcto? (s/n): ", "inconnu": " La IA no lo sabe, incluso después de buscar en la web.",
        "select_style": "\n Selecciona un estilo:", "style_c": "  [1] Corta", "style_n": "  [2] Normal", "style_d": "  [3] Detallada",
        "style_choisi": " Estilo elegido: ", "question_cl": "\n Pregunta: ", "reponse_cl": " Respuesta: ", "cat_cl": " Categoría [1] Ci [2] Mat [3] Cult: ",
        "config_titre": "\n--- CONFIGURACIÓN DE AUDIO ---", "statut_tts": "TTS (Síntesis de voz)", "statut_sr": "Reconocimiento de voz",
        "demande_tts": "¿Activar TTS? (s/n): ", "demande_sr": "¿Activar reconocimiento de voz? (s/n): ",
        "confirm_tts": "TTS activado: las respuestas de la IA se leerán en voz alta.",
        "confirm_sr": "Reconocimiento de voz activado: podrás hacer tus preguntas oralmente.",
        "audio_ok": "¡Ajustes aplicados con éxito!", "actif": "Activado", "desactif": "Desactivado"
    }
}
txt = LEXIQUE.get(langue_ia, LEXIQUE["en"])

SUPABASE_URL = "https://givazljlcyrcvmkstvgz.supabase.co"
SUPABASE_KEY = "sb_publishable_IXeKK1bSStuQ8PjEYFZwQw_z4P_ZCCC"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ttss = False
srs = False

def charger_base():
    try:
        print("Synchronisation avec Supabase...")
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
        print(f"{len(data)} questions chargées depuis le Cloud !")
        return base
    except Exception as e:
        print(f"Erreur de connexion au serveur : {e}")
        return {"sciences": [], "maths": [], "culture": []}

def ia_apprend(question_exacte_base, correct, BASE_DE_DONNEES):
    try:
        for cat, questions in BASE_DE_DONNEES.items():
            for q in questions:
                if q["question"] == question_exacte_base:
                    ancienne_confiance = q.get('confiance', 50)
                    nouvelle_confiance = min(ancienne_confiance + 10, 100) if correct else max(ancienne_confiance - 15, 0)
                    q['confiance'] = nouvelle_confiance
                    supabase.table("questions").update({"confiance": nouvelle_confiance}).eq("question", question_exacte_base).execute()
                    print(f"Serveur mis à jour : {nouvelle_confiance}%")
                    return
    except Exception as e:
        print(f"Erreur de synchronisation Cloud : {e}")

def ajouter_a_supabase(question, reponse, categorie):
    try:
        data = {"question": question, "reponse": reponse, "categorie": categorie, "confiance": 50}
        supabase.table("questions").insert(data).execute()
        print("Question envoyée au cerveau central !")
    except Exception as e:
        print(f"Erreur lors de l'ajout : {e}")

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
    if style == "courte": return reponse_courte(question, reponse)
    if style == "detaillee": return reponse_detaillee(question, reponse)
    return reponse if reponse.endswith(".") else f"{reponse}."

def extraire_phrases(texte, nb_phrases):
    phrases = re.split(r'(?<=[.!?]) +', texte.strip())
    return " ".join(phrases[:nb_phrases])

def chercher_web(question, style="normale"):
    try:
        print(" Recherche en cours sur des sources vérifiées...")
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

                if style == "courte": texte_final = extraire_phrases(texte_brut, 1)
                elif style == "detaillee": texte_final = extraire_phrases(texte_brut, 5) 
                else: texte_final = extraire_phrases(texte_brut, 2)

                return texte_final, f"Source: {nom_site}"
    except Exception as e:
        print(f"Erreur recherche web : {e}")
    return None, None

def ia_repond(question, BASE_DE_DONNEES, style_actuel="normale"):
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
    
    reponse_internet, source = chercher_web(question, style=style_actuel)
    if reponse_internet:
        return reponse_internet, 100, f"[WEB] {source}"

    return None, 0, None

def faire_parler(texte):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 165) 
        engine.say(texte)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error : {e}")

def ecouter_micro():
    global langue_ia
    recog = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n Écoute en cours... Parle maintenant.")
        recog.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recog.listen(source, timeout=5)
            texte_audio = recog.recognize_google(audio, language=f"{langue_ia}-{langue_ia.upper()}")
            print(f" Vous avez dit : « {texte_audio} »")
            return texte_audio
        except sr.UnknownValueError:
            print(" Impossible de comprendre l'audio.")
            return None
        except sr.RequestError:
            print(" Erreur de connexion au service vocal.")
            return None
        except Exception:
            print(" Temps d'écoute dépassé ou micro indisponible.")
            return None

def main():
    global ttss, srs 
    print("╔════════════════════════════════════════╗")
    print(f"║    {txt['titre'].center(34)}  ║")
    print("╚════════════════════════════════════════╝")

    BASE_DE_DONNEES = charger_base()
    style_reponse = "normale"

    while True:
        print("\n" + "─" * 45)
        print(f"{txt['menu1']}   [{txt['style_actuel']}: {style_reponse}]")
        print(txt['menu2'])
        print(txt['menu3'])
        print(f"  {txt['menu4']} [TTS: {'ON' if ttss else 'OFF'} | Mic: {'ON' if srs else 'OFF'}]")
        print(txt['menu5'])
        print("─" * 45)

        choix = input(txt['choix']).strip()

        if choix == "1":
            question_user = ecouter_micro() if srs else input(txt['ta_question']).strip()
            if not question_user: continue

            reponse, confiance, q_exacte = ia_repond(question_user, BASE_DE_DONNEES, style_reponse)

            if reponse:
                reponse_affichee = varier_reponse(reponse, style_reponse, question_user)
                print(f" L'IA : « {reponse_affichee} » (Fiabilité: {confiance}%)")
                
                if q_exacte and not q_exacte.startswith("[WEB]"):
                    feedback = input(txt['correct']).lower()
                    ia_apprend(q_exacte, feedback in ["o", "y", "s"], BASE_DE_DONNEES)
            else:
                reponse_affichee = txt['inconnu']
                print(reponse_affichee)
            
            if ttss and reponse_affichee:
                faire_parler(reponse_affichee)

        elif choix == "2":
            print(txt['select_style'])
            print(f"{txt['style_c']}\n{txt['style_n']}\n{txt['style_d']}")
            style = input("  → ").strip()
            style_map = {"1": "courte", "2": "normale", "3": "detaillee"}
            style_reponse = style_map.get(style, style_reponse)
            print(f"{txt['style_choisi']}{style_reponse}")

        elif choix == "3":
            q = input(txt['question_cl']).strip()
            r = input(txt['reponse_cl']).strip()
            cat = input(txt['cat_cl'])
            cat_map = {"1": "sciences", "2": "maths", "3": "culture"}
            if q and r:
                ajouter_a_supabase(q, r, cat_map.get(cat, "culture"))
                BASE_DE_DONNEES = charger_base()

        elif choix == "4":
            print(txt['config_titre'])
            print(f"{txt['statut_tts']} : {txt['actif'] if ttss else txt['desactif']}")
            print(f"{txt['statut_sr']} : {txt['actif'] if srs else txt['desactif']}\n")
            
            activate_tts = input(txt['demande_tts']).lower()
            if activate_tts in ["o", "y", "s"]:
                print(txt['confirm_tts'])
                ttss = True
            else:
                ttss = False
            
            activate_sr = input(txt['demande_sr']).lower()
            if activate_sr in ["o", "y", "s"]:
                print(txt['confirm_sr'])
                srs = True
            else:
                srs = False
            
            print(txt['audio_ok'])

        elif choix == "5":
            break

if __name__ == "__main__":
    main()
