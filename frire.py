import os
import random
import math
import json
from supabase import create_client

SUPABASE_URL = "YOUR_URL"
SUPABASE_KEY = "YOUR_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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

                    supabase.table("questions") \
                        .update({"confiance": nouvelle_confiance}) \
                        .eq("question", question_exacte_base) \
                        .execute()

                    print(f"Serveur mis à jour : {nouvelle_confiance}%")
                    return
    except Exception as e:
        print(f"Erreur de synchronisation Cloud : {e}")

def ajouter_a_supabase(question, reponse, categorie):
    try:
        data = {"question": question, "reponse": reponse, "categorie": categorie, "confiance": 50}
        supabase.table("questions").insert(data).execute()
        print(f"Question envoyée au cerveau central !")
    except Exception as e:
        print(f"Erreur lors de l'ajout : {e}")

def nettoyer(texte):
    texte = texte.lower().strip()
    for car in ["é", "è", "ê", "ë"]: texte = texte.replace(car, "e")
    for car in ["à", "â"]: texte = texte.replace(car, "a")
    for car in ["ù", "û"]: texte = texte.replace(car, "u")
    for car in ["ô"]: texte = texte.replace(car, "o")
    for car in ["î", "ï"]: texte = texte.replace(car, "i")
    return texte.replace("'", " ").replace("-", " ")

def score_similarite(reponse_ia, bonne_reponse):
    r1, r2 = set(nettoyer(reponse_ia).split()), set(nettoyer(bonne_reponse).split())
    return len(r1 & r2) / len(r2) if r2 else 0

def ia_repond(question, BASE_DE_DONNEES):
    q_nettoyee = nettoyer(question)
    toutes_questions = [(q, cat) for cat, qs in BASE_DE_DONNEES.items() for q in qs]
    meilleur_score, meilleure_q = 0, None

    for q, cat in toutes_questions:
        score = score_similarite(q_nettoyee, nettoyer(q["question"]))
        if score > meilleur_score:
            meilleur_score, meilleure_q = score, q

    if meilleur_score > 0.3 and meilleure_q:
        return meilleure_q["reponse"], meilleure_q.get("confiance", 50), meilleure_q["question"]
    return None, 0, None

def main():
    print("╔════════════════════════════════════════╗")
    print("║    Frire — IA Française                ║")
    print("╚════════════════════════════════════════╝")

    BASE_DE_DONNEES = charger_base()

    while True:
        print("\n" + "─" * 45)
        print("  [1] Poser une question\n  [2] Quiz\n  [3] Ajouter au Cloud\n  [4] Quitter")
        print("─" * 45)

        choix = input("  → Choix : ").strip()

        if choix == "1":
            question_user = input("\n Ta question : ").strip()
            if not question_user: continue

            reponse, confiance, q_exacte = ia_repond(question_user, BASE_DE_DONNEES)

            if reponse:
                print(f" L'IA : « {reponse} » (Fiabilité: {confiance}%)")
                feedback = input(" Est-ce correct ? (o/n) : ").lower()
                ia_apprend(q_exacte, feedback == "o", BASE_DE_DONNEES)
            else:
                print(" L'IA ne sait pas.")

        elif choix == "3":
            q = input("\n Question : ").strip()
            r = input(" Réponse  : ").strip()
            cat = input(" Catégorie [1] Sc [2] Mat [3] Cul : ")
            cat_map = {"1": "sciences", "2": "maths", "3": "culture"}
            if q and r:
                ajouter_a_supabase(q, r, cat_map.get(cat, "culture"))
                BASE_DE_DONNEES = charger_base()

        elif choix == "4":
            break

if __name__ == "__main__":
    main()
