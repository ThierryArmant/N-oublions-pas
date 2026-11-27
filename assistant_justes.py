import hmac
import json
import os
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
SITE = "https://thierryarmant.github.io/N-oublions-pas/"
API = "https://albert.api.etalab.gouv.fr/v1/chat/completions"
STOP = set("un une le la les des du de d et en a au aux est etait sont qui quel quelle quels quelles dans pour que qu je cherche trouve juste justes parmi nations".split())


def tokens(text):
    plain = unicodedata.normalize("NFD", text.lower())
    return set(re.findall(r"[a-z0-9]+", "".join(c for c in plain if not unicodedata.combining(c)))) - STOP


def dossier_url(number):
    return "https://yadvashem-france.org/dossier/nom/" + quote(number.lower()) + "/"


@lru_cache(maxsize=1)
def notices():
    page = (HERE / "index.html").read_text(encoding="utf-8")
    national = json.loads((HERE / "justes-france.json").read_text(encoding="utf-8"))["personnes"]
    regional = {}
    for match in re.finditer(r"const dossiers(?:Vaucluse|BouchesDuRhone) = (\{[^\n]+\});", page):
        regional.update(json.loads(match[1]))
    for match in re.finditer(r"'([0-9]+[A-Za-z]?)':\s*\{\s*periode:'([^']*)',\s*geste:'([^']*)',\s*aide:'([^']*)',\s*histoire:'([^']*)'", page):
        number, period, action, people, story = match.groups()
        regional.setdefault(number.upper(), [period, action, people, story])
    entries = {}
    for row in national:
        slug, name, given, alias, number, city, area, *_ = row
        label = f"{given} {name}".strip()
        entries[slug] = dict(label=label, place=", ".join(filter(None, [city, area])),
                             facts=" · ".join(regional.get(number.upper(), [])[:4]),
                             source=dossier_url(number), terms=alias)
    cases = json.loads(re.search(r"const sauvetages = (\[[^\n]+\]);", page)[1])
    for case_id, city, year, numbers, people, story, persons, *source in cases:
        for name, given in persons:
            label = f"{given} {name}"
            key = next((k for k, row in entries.items() if tokens(row["label"]) == tokens(label)
                        and city in row["place"]), "local-" + label)
            number = numbers.split()[0] if numbers else ""
            entries[key] = dict(label=label, place=city + ", Vaucluse",
                                facts=f"{story} Personnes aidées : {people}. " + (
                                    f"Reconnaissance par Yad Vashem : {year}." if year else "Sauvetage documenté, reconnaissance non établie."),
                                source=source[0] if source else dossier_url(number), terms="")
    for key, entry in entries.items():
        if key == "landi-giuseppe":
            entry["facts"] += " Giuseppe Landi était agent de la SNCF (cheminot)."
            entry["terms"] += " cheminot cheminots ferroviaire railway sncf"
    return list(entries.values())


def rechercher(question, limit=6):
    query = tokens(question)
    results = []
    for item in notices():
        name = tokens(item["label"])
        place = tokens(item["place"])
        facts = tokens(item["facts"] + " " + item["terms"])
        score = 5 * len(query & name) + 2 * len(query & place) + 4 * len(query & facts)
        if score and item["facts"] and (query & (name | facts) or query <= place):
            results.append((score, item))
    results.sort(key=lambda row: -row[0])
    return [item for _, item in results[:limit]]


def albert(question, results, key, model):
    context = [
        {"reference": index, **{field: item[field] for field in ("label", "place", "facts")}}
        for index, item in enumerate(results, start=1)
    ]
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": (
                "Tu es un assistant de recherche historique de N’oublions pas !. "
                "Réponds en français uniquement à partir des faits fournis. "
                "Cite leurs numéros entre crochets, par exemple [1]. "
                "Distingue les Justes reconnus des autres sauveteurs. "
                "Si les faits ne suffisent pas, indique-le. N’invente ni source ni détail. "
                "Ne présente jamais une recherche comme exhaustive."
            )},
            {"role": "user", "content": json.dumps({"question": question, "notices": context}, ensure_ascii=False)}
        ],
        "max_tokens": 350
    }).encode()
    request = Request(API, body, {"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    with urlopen(request, timeout=20) as response:
        return json.load(response)["choices"][0]["message"]["content"].strip()


def main():
    import streamlit as st

    st.set_page_config(page_title="Recherche historique · N’oublions pas !")
    st.title("Rechercher dans les dossiers des Justes")
    st.caption("Recherche dans les fiches documentées de N’oublions pas !")
    access = os.environ.get("ASSISTANT_ACCESS_CODE") or st.secrets.get("ASSISTANT_ACCESS_CODE", "")
    if not access:
        st.info("La recherche assistée est en attente de configuration.")
        return
    if not st.session_state.get("assistant_autorise"):
        with st.form("acces"):
            value = st.text_input("Code d’accès", type="password")
            submitted = st.form_submit_button("Ouvrir l’assistant")
        if submitted:
            if hmac.compare_digest(value.encode(), access.encode()):
                st.session_state["assistant_autorise"] = True
                st.rerun()
            st.warning("Code d’accès incorrect.")
        return
    with st.form("question"):
        question = st.text_input("Votre question", placeholder="Quel Juste était cheminot dans le Vaucluse ?", max_chars=300)
        submitted = st.form_submit_button("Rechercher")
    if not submitted or not question.strip():
        return
    results = rechercher(question)
    if not results:
        st.info("Les fiches documentées ne permettent pas de répondre à cette question.")
        return
    key = os.environ.get("ALBERT_API_KEY") or st.secrets.get("ALBERT_API_KEY", "")
    model = os.environ.get("ALBERT_MODEL") or st.secrets.get("ALBERT_MODEL", "")
    if key and model:
        try:
            st.write(albert(question, results, key, model))
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError, IndexError):
            st.info("Albert est momentanément indisponible. Vous pouvez consulter les extraits ci-dessous.")
    else:
        st.info("La rédaction avec Albert est en attente de configuration. Voici les extraits pertinents.")
    st.subheader("Dossiers consultés")
    for index, item in enumerate(results, start=1):
        st.markdown(f"**[{index}] {item['label']}** · {item['place']}")
        st.write(item["facts"])
        link = SITE + "?vue=justes&sauvetage=" + quote(item["label"]) + "#justes"
        st.markdown(f"[Ouvrir la fiche]({link}) · [Consulter la source]({item['source']})")


if __name__ == "__main__":
    main()
