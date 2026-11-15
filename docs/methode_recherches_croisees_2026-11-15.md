# Recherche par identités, relations et documents — méthode et résultats du 15 novembre 2026

## Pourquoi changer de méthode
Une recherche « prénom nom photo » laisse de côté les noms de naissance, les albums collectifs, les légendes non indexées, les ouvrages étrangers et les photographies disponibles uniquement dans les dossiers d’un proche. Une absence de résultat ne prouve pas l’absence de portrait.

## Méthode réutilisable
1. **Construire la carte d’identité documentaire** : noms de naissance/d’épouse, variantes, pseudonymes, date et commune, matricules par camp, réseau, dates d’arrestation. Conserver les divergences.
2. **Partir des relations attestées** : famille, compagnes d’évasion, témoins nommés. Examiner leurs albums, témoignages et fonds. L’appartenance à un convoi n’établit pas une amitié.
3. **Lire autour de la personne recherchée** : sommaires, crédits photographiques, légendes, index et pages voisines d’un document consacré à une autre personne. Chercher aussi dans les langues des pays d’origine et des lieux de captivité.
4. **Distinguer trois travaux** : découverte d’une image nouvelle ; récupération d’une image cassée ; mise en valeur d’une image déjà identifiée au verso. Ne pas les additionner comme nouveaux portraits.
5. **Examiner la technique des pages** : images différées (data-orig-src, data-src), srcset, liens vers originaux. Rejeter logos, silhouettes et images décoratives. Une image voisine d’un nom n’est pas automatiquement celle de cette personne.
6. **Valider avant intégration** : légende nominative, concordance avec état civil ou matricule/parcours, inspection visuelle, crédit et source précis. Aucune identification par ressemblance faciale. Un dessin ou une liste n’est pas une photographie.
7. **Tracer le résultat** : document consulté, extrait indexé seulement, dossier signalé, image inaccessible, homonyme écarté, divergence non résolue. Une nouvelle piste doit orienter la recherche suivante au lieu de reproduire la requête précédente.

## Outil ajouté
`scripts/recherche_portraits.py` :
- inventaire des fiches régionales sans image associée, selon les exclusions de la vue publique ;
- priorité aux images déjà documentées puis aux relations attestées ;
- requêtes préparées à partir des noms, matricules, sources et relations ;
- extraction des adresses d’images d’une page et de leur contexte HTML ;
- aucune fusion de personnes ni attribution automatique.

Commandes :
```sh
python scripts/recherche_portraits.py inventaire --sortie docs/pistes_portraits.csv
python scripts/recherche_portraits.py images https://www.bbc.com/news/stories-59566983
```
Les noms de naissance inclus dans le nom complet et les variantes déjà structurées doivent encore être examinés par le chercheur ; les requêtes générées ne constituent pas une résolution d’identité.

## Résultats intégrés : sept fiches régionales
| Personne | Résultat réel | Limite |
|---|---|---|
| Anne-Marie / Anne Spoerry | Deux photographies d’après-guerre réunies dans un montage Amref publié par le DHS ; biographie, Radio Patrie, médecine au Kenya et procédures d’après-guerre ajoutées | Une fiche nouvellement illustrée ; droits Amref, aucune licence libre affirmée ; accusations et abandon des poursuites décrits sans les confondre |
| Jacqueline Aubéry du Boulley | Montage déjà présent au verso rendu visible au recto, avec légende « Jacky en haut à droite » ; source BBC contrôlée | Pas un nouveau portrait découvert ; montage intégral conservé et affiché sans découpe |
| Lucienne Vanucci | Ligne nominative retrouvée dans une reproduction de liste de Ravensbrück du 30 août 1943, p. 105 imprimée / 106 PDF d’une étude espagnole | Matricule 22464 concordant ; 28.10.22 sur la pièce contre 28.10.1925 au Livre-Mémorial. Date conservée et divergence affichée ; pas une photographie |
| Marie Jouffron née Martin | Notice SHD AC 21 P 577992 retrouvée | Nom et date concordent, Boëge dans la notice contre Paris au Livre-Mémorial. Dossier non consulté ; rapprochement à confirmer |
| Églantine Martin épouse Pelloux | Référence d’homologation GR 16 P 397370 | Répertoire indexé ; dossier non consulté |
| Émilienne Antetomaso née Tartat | Piste GR 16 P 562560 sous Victorine Émilienne Louise Tartat | 28/29 septembre 1903 : rapprochement à confirmer ; dossier non consulté |
| Élisabeth Barbier Campbell | GR 28 P 4 254 174, concordance GR 16 P 31893 | Répertoire indexé ; dossiers non consultés |

### Sources de cette série
- DHS, Christian Baertschi, Anne Spoerry : https://hls-dhs-dss.ch/fr/articles/045830/2022-01-13/
- Photographies Amref : https://hls-dhs-dss.ch/download/Articles/045830/2022-01-13/med045830-001/SPOERRY-Anne_Collage-AMREF.png?rev=1.3&width=620
- BBC, Lucy Wallis, article du 2 janvier 2022 et légende du montage : https://www.bbc.com/news/stories-59566983
- Étude Instituto de las Mujeres, document p. 105, référence Arolsen 1.1.35.1 / 3765097 : https://www.inmujeres.gob.es/publicacioneselectronicas/documentacion/Documentos/DE2401.pdf#page=106
- SHD Jouffron : https://www.servicehistorique.sga.defense.gouv.fr/en/node/1415424
- Répertoires SHD : https://www.museedelaresistanceenligne.org/musee/doc/pdf/ressource_source/SHDGR_16P_M.pdf ; https://www.museedelaresistanceenligne.org/musee/doc/pdf/ressource_source/SHDGR_16P_T.pdf ; https://museedelaresistanceenligne.org/musee/doc/pdf/ressource_source/209.pdf

## Pistes écartées ou non abouties
- Lucienne Thévenin : quatre images légendées repérées sur Mémoire Vive, mais adresses de cache 404 ; un chemin d’original essayé renvoie 404 ; recherche publique de médias WordPress sans résultat. Ne pas insérer ces adresses cassées. Source : https://www.memoirevive.org/lucienne-dite-lulu-thevenin-nee-serre-31642/
- Pierrette Doize / Petra Folch : page AFMD avec image « photo non trouvée » ; la photo d’Alicia Pérez Comesaña dans la page Amical n’est pas attribuée à Petra.
- Juliette Eyraud / Julie Josette Marie : piste déjà connue, pas de nouvelle preuve.
- Jeanne Clavet : fonds transmis à l’Ordre par Richard Clavet identifié, aucun portrait nouveau validé.
- Rose Nielsen : photo danoise d’un couple homonyme non rattachée à la femme née à Tallard ; non intégrée.
- Louise de Giraud d’Agay : dossier de dommages de guerre retrouvé sous Louise née Anglès ; aucun rapprochement de portrait validé.
- Henriette Bardi de Fourtou : forme Nervegno et médaille 1O2771 corroborées, pas de portrait nouveau.
- Pas de résultat probant sur les portraits de Raymonde Temmermann, Laurence Caila, Thérésa Wasilewska dans cette série.

## État et contrôles
80 régionales visibles, 35 avec une image associée, 45 sans image associée. Les images associées ne sont pas toutes des photographies individuelles ; ce nombre n’est pas un total de portraits historiquement certifiés.
64 femmes du convoi, 660 hommes et 201 entrées du tableau des portraits conservés.
Le tableau des 64 femmes et les hommes sont inchangés dans cette série. Aucun document ou portrait antérieur supprimé.
JSON contrôlé ; sept fiches modifiées par nom stable ; photographies téléchargées et inspectées ; page 106 du PDF rendue et inspectée ; extraction HTML exercée sur la BBC ; syntaxe JavaScript contrôlée.
Clé de cache mise à jour : regionales-croisees-20261115. Montages affichés en entier et légendés au recto. Aucun corrigé enseignant ajouté au parcours élève.

## Prochaines actions utiles
- Traiter les 45 lignes du CSV, remplir résultat, preuve d’identité, source et crédit après chaque recherche.
- Thévenin : rechercher les originaux dans d’autres publications de la famille Serre ou du convoi des 31000, plutôt que répéter les liens 404.
- Clavet : dépouiller les publications et inventaires de la collecte Ordre de la Libération sous Thomas, Zaza et Clavet.
- Vanucci : vérifier l’état civil et la pièce Arolsen originale avant toute correction d’année.
- Tartat, Jouffron : lever les divergences d’identité avant attribution de documents ou de photos.
