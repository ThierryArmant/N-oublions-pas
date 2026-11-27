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
            url = entries[key]["source"] if key in entries else dossier_url(numbers.split()[0]) if numbers else ""
            if not url:
                url = source[0] if source else SITE
            entries[key] = dict(label=label, place=city + ", Vaucluse",
                                facts=f"{story} Personnes aidées : {people}. " + (
                                    f"Reconnaissance par Yad Vashem : {year}." if year else "Sauvetage documenté, reconnaissance non établie."),
                                source=url, terms="")
    for key, entry in entries.items():
        if key == "landi-giuseppe":
            entry["facts"] += " Giuseppe Landi était agent de la SNCF (cheminot)."
            entry["terms"] += " cheminot cheminots ferroviaire railway sncf"
    return list(entries.values())


def rechercher(question, limit=6):
    query = tokens(question)
    results = []
    for item in notices():
        if not item["facts"]:
            continue
        name = tokens(item["label"])
        place = tokens(item["place"])
        facts = tokens(item["facts"] + " " + item["terms"])
        matches = query & (name | place | facts)
        strong = query & (name | facts)
        if not matches or (not strong and matches != query):
            continue
        exact_name = len(name) >= 2 and name <= query
        score = 6 * len(query & name) + 3 * len(query & place) + 4 * len(query & facts)
        results.append((exact_name, len(matches), score, item))
    results.sort(key=lambda row: row[:3], reverse=True)
    if not results:
        return []
    # A single-word coincidence should not dilute a clearly better match.
    best_exact, best_coverage = results[0][:2]
    selected = [
        item for exact, coverage, _, item in results
        if (not best_exact or exact) and coverage >= max(1, best_coverage - 1)
        and (best_coverage < 2 or coverage >= 2)
    ]
    return selected[:limit]


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

    from streamlit.errors import StreamlitSecretNotFoundError

    def setting(name):
        value = os.environ.get(name)
        if value:
            return value
        try:
            return st.secrets.get(name, "")
        except StreamlitSecretNotFoundError:
            return ""

    st.set_page_config(page_title="Mémo · N’oublions pas !", layout="wide")
    integre = st.query_params.get("memo") == "accueil"
    if integre:
        st.markdown("""<style>
        [data-testid="stAppViewContainer"], [data-testid="stApp"] {background:#eaf1f7}
        [data-testid="stMainBlockContainer"] {padding:.15rem .2rem 1rem;max-width:none}
        [data-testid="stForm"] {border:0;padding:0}
        [data-testid="stTextInput"] input {background:#fff;color:#163754}
        [data-testid="stFormSubmitButton"] button {background:#163754;color:#fff;border:0;font-weight:650}
        [data-testid="stForm"] [data-testid="stHorizontalBlock"] {flex-wrap:wrap;gap:.5rem}
        [data-testid="stForm"] [data-testid="stColumn"]:first-child {flex:1 1 12rem;width:auto}
        [data-testid="stForm"] [data-testid="stColumn"]:last-child {flex:0 0 auto;width:auto}
        @media(max-width:700px) {
            [data-testid="stHorizontalBlock"] {flex-wrap:wrap}
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {flex:1 1 100%;width:100%;min-width:0}
        }
        </style>""", unsafe_allow_html=True)
    else:
        st.title("Mémo · N’oublions pas !")
        st.caption("Recherche dans les fiches documentées des Justes")
    panneau_question, panneau_reponse = st.columns([2, 3], gap="medium")
    with panneau_question, st.form("question", border=False):
        champ, bouton = st.columns([5, 1])
        with champ:
            question = st.text_input(
                "Votre question",
                placeholder="Posez votre question…",
                max_chars=300,
                label_visibility="collapsed",
            )
        with bouton:
            submitted = st.form_submit_button("Rechercher", use_container_width=True)
    active = submitted and bool(question.strip())
    if integre:
        from streamlit.components.v1 import html

        html(
            f"""<script>
            window.top.postMessage(
                {{type: 'memo-affichage', active: {json.dumps(active)}}},
                'https://thierryarmant.github.io'
            );
            </script>""",
            height=0,
        )
    if not active:
        return
    with panneau_reponse:
        with st.spinner("Un instant, je cherche dans les archives…"):
            results = rechercher(question)
            if not results:
                st.info("Les fiches documentées ne permettent pas de répondre à cette question.")
                return
            key = setting("ALBERT_API_KEY")
            model = setting("ALBERT_MODEL")
            if key and model:
                try:
                    st.write(albert(question, results, key, model))
                except (HTTPError, URLError, TimeoutError, ValueError, KeyError, IndexError):
                    st.info("Albert est momentanément indisponible. Vous pouvez consulter les extraits ci-dessous.")
            else:
                st.info("La rédaction avec Albert est en attente de configuration. Voici les extraits pertinents.")
        st.subheader("Fiches en rapport avec la réponse")
        for item in results:
            link = SITE + "?vue=justes&sauvetage=" + quote(item["label"]) + "&ouvrir=1#justes"
            st.link_button(f"Ouvrir la fiche de {item['label']}", link)
        with st.expander("Dossiers consultés"):
            for index, item in enumerate(results, start=1):
                st.markdown(f"**[{index}] {item['label']}** · {item['place']}")
                st.write(item["facts"])
                st.markdown(f"[Consulter la source]({item['source']})")


if __name__ == "__main__":
    main()
