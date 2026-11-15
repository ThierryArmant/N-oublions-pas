#!/usr/bin/env python3
"""Préparer des pistes vérifiables, sans attribuer automatiquement une image.

python scripts/recherche_portraits.py inventaire --sortie docs/pistes_portraits.csv
python scripts/recherche_portraits.py images URL > /tmp/candidats_images.json
"""
import argparse
import csv
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def texte(value):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", " ", value))).strip()


def sans_accents(value):
    return ''.join(c for c in unicodedata.normalize('NFD', value)
                   if unicodedata.category(c) != 'Mn')


def inventaire(destination):
    data = json.loads((ROOT / 'data.json').read_text())
    rows = []
    for collection in ('portraits',):
        for p in data[collection]:
            if collection == 'portraits' and not p.get('region'):
                continue
            if p.get('nom') in {'JEANNETTE CASTELLANO', 'CHRISTIANE FAMERY', 'ANDRÉE JULIEN', 'COLETTE LAFFINEUR'}:
                continue  # Identités réservées, également exclues de la vue régionale.
            nom = p.get('nom_affiche') or p.get('nom', '')
            if p.get('photo_data') or p.get('photo_url') or p.get('photo'):
                continue  # Une image associée reste à distinguer d'un portrait vérifié.
            bio = p.get('biographie', {})
            identites = list(dict.fromkeys([nom, p.get('nom', ''), sans_accents(nom)]))
            sources = p.get('sources_biographiques', [])
            domaines = sorted({urlparse(s.get('url', '')).netloc for s in sources} - {''})
            relations = p.get('relations_documentees', [])
            # Les liens de convoi seuls ne prouvent pas une relation personnelle.
            voisins = [r.get('nom', '') for r in relations]
            documents = [d for d in p.get('documents_historiques', []) if d.get('image')]
            matricules = bio.get('matricules', p.get('matricule', ''))
            requetes = [f'"{n}" photographie portrait archives' for n in identites if n]
            if matricules:
                requetes.append(f'"{nom}" {matricules}')
            if voisins:
                requetes.append(f'"{nom}" "{voisins[0]}" photographie')
            for domain in domaines[:3]:
                requetes.append(f'site:{domain} "{nom}"')
            naissance = bio.get('naissance', '')
            rows.append(dict(
                cle=collection + ':' + p.get('nom', ''), nom=nom,
                priorite='1-image-deja-documentee' if documents else
                         '2-relation-documentee' if voisins else '3-identite-et-parcours',
                identites=' | '.join(identites), naissance=naissance,
                matricules=matricules, reseau=p.get('reseau_affiche', ''),
                liens_documentes=' | '.join(voisins), domaines=' | '.join(domaines),
                images_au_verso=' | '.join(d['image'] for d in documents),
                requetes='\n'.join(requetes), statut='a_rechercher',
                resultat='', preuve_identite='', source_image='', credit='',
                controle='Légende nominative + état civil/matricule/parcours ; inspection visuelle ; aucune reconnaissance faciale.'
            ))
    rows.sort(key=lambda r: (r['priorite'], r['cle']))
    with Path(destination).open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ['cle'])
        w.writeheader()
        w.writerows(rows)
    print(json.dumps({'fiches_sans_image_associee': len(rows), 'sortie': str(destination)}, ensure_ascii=False))


class Images(HTMLParser):
    def __init__(self, base, source):
        super().__init__()
        self.base, self.source, self.items = base, source, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag not in ('img', 'source', 'a'):
            return
        candidates = []
        for key in ('data-orig-src', 'data-src', 'data-lazy-src', 'src', 'href'):
            if attrs.get(key):
                candidates.append((key, attrs[key]))
        for key in ('srcset', 'data-srcset'):
            for part in attrs.get(key, '').split(','):
                if part.strip():
                    candidates.append((key, part.strip().split()[0]))
        for attr, url in candidates:
            if url.startswith('data:') or (tag == 'a' and not re.search(r'\.(jpg|jpeg|png|webp)(\?|$)', url, re.I)):
                continue
            url = urljoin(self.base, url)
            if urlparse(url).scheme not in ('http', 'https'):
                continue
            line, col = self.getpos()
            lines = self.source.splitlines(keepends=True)
            offset = sum(map(len, lines[:line-1])) + col
            self.items.append(dict(url=url, attribut=attr, alt=attrs.get('alt', ''),
                                   contexte=texte(self.source[max(0, offset-500):offset+1500]),
                                   statut='candidat_non_attribue'))


def images(url):
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (recherche documentaire)'})
    with urlopen(request, timeout=25) as r:
        source = r.read(8_000_000).decode(r.headers.get_content_charset() or 'utf-8', errors='replace')
        final_url = r.url
    parser = Images(final_url, source)
    parser.feed(source)
    result = list({item['url']: item for item in parser.items}.values())
    print(json.dumps(dict(page=final_url, sha256=hashlib.sha256(source.encode()).hexdigest(),
                          candidats=result, avertissement='Le voisinage HTML ne prouve pas l’identité du sujet.'),
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest='mode', required=True)
    inventory = sub.add_parser('inventaire')
    inventory.add_argument('--sortie', required=True)
    inspect = sub.add_parser('images')
    inspect.add_argument('url')
    args = cli.parse_args()
    inventaire(args.sortie) if args.mode == 'inventaire' else images(args.url)
