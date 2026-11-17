import json,re,sys,unicodedata
P='/home/claude/n-oublions-pas/data.json'
d=json.load(open(P));H=d['hommes'];PO=d['portraits']
ARK='https://www.memoiredeshommes.defense.gouv.fr/ark:40699/m00'
def n(s): return unicodedata.normalize('NFD',s or '').encode('ascii','ignore').decode().upper().replace('-',' ')
CODES={'DIR':'déporté-interné de la Résistance (DIR)','FFI':'Forces françaises de l’intérieur (FFI)','FFC':'Forces françaises combattantes (FFC)','RIF':'Résistance intérieure française (RIF)','FFL':'Forces françaises libres (FFL)'}
st={'h':0,'f':0,'skip':[],'diff':[],'nodeath':[]}
seen=set()
for line in open(sys.argv[1],encoding='utf-8'):
    p=line.rstrip('\n').split('|')
    if len(p)<10: continue
    pid,pre,cotes,dec,codes,net,mvt,ps,flags,ark=p[:10]
    key=pid.rstrip('j')
    if key in seen: continue
    x=H[int(key[1:])] if key[0]=='h' else PO[int(key[1:])]
    a=n(x.get('prenom','')).split(); b=n(pre).split()
    REJ={'BORGE PANERO','BRAFMANN','DEBOE','HAMERLAK','ORGUEIL','NIBAUT','DEMELLE','DUBARRY','LEVY'}
    if x.get('nom') in REJ: st['skip'].append((x.get('nom'),x.get('prenom'),pre)); continue
    if False:
        st['skip'].append((x.get('nom'),x.get('prenom'),pre)); continue
    seen.add(key)
    cl=[c for c in cotes.split(';') if c]
    ac=[c for c in cl if c.startswith('AC')]; gr=[c for c in cl if c.startswith('GR')]
    bits=[]
    if ac: bits.append('dossier au SHD de Caen (victimes et déportés) : '+', '.join(ac))
    if gr: bits.append('dossier au SHD de Vincennes (services de résistance) : '+', '.join(gr))
    stat=[CODES[c] for c in codes.split(',') if c in CODES]
    s2=''
    if stat: s2='Statut reconnu : '+', '.join(stat)
    if net: s2+=(' — réseau '+net.title())
    if mvt and mvt!='ISOLE': s2+=(' — mouvement '+mvt.title().replace('Ex-Mur','ex-MUR').replace('Mln','MLN').replace('Ora','ORA').replace('Ocm','OCM').replace('Pown','POWN'))
    if ps: s2+=(' — pseudonyme « '+ps+' »')
    extra=[]
    if 'M' in flags.split(','): extra.append('médaille de la Résistance (base des médaillés)')
    if 'MPF' in flags: extra.append('mention « Mort pour la France »')
    if 'fus' in flags: extra.append('cause du décès : fusillé')
    txt='Mémoire des hommes (ministère des Armées) — '+' ; '.join(bits)+'.'
    if s2: txt+=' '+s2+'.'
    if extra: txt+=' '+'; '.join(e[0].upper()+e[1:] for e in extra)+'.'
    # death (men only, plausible)
    if key[0]=='h' and dec:
        m=re.match(r'(\d+)/(\d+)/(\d{4})',dec) or re.match(r'()(\d+)/(\d{4})',dec)
        y=int(m.group(3)) if m else 0; mo=int(m.group(2)) if m else 0
        if y>1944 or (y==1944 and mo>=7):
            txt+=' Décès enregistré : '+dec+'.'
            ds=x.get('date_sortie','')
            if x.get('situation','').startswith('DCD') and m and m.group(1) and re.match(r'\d{2}/\d{2}/\d{4}$',ds):
                if (int(m.group(1)),mo,str(y))!=(int(ds[:2]),int(ds[3:5]),ds[6:]): st['diff'].append((x['nom'],x.get('prenom'),ds,dec))
            if x.get('situation') in ('E *','L *'): st['diff'].append((x['nom'],x.get('prenom'),'situation '+x.get('situation'),dec))
        else: st['nodeath'].append((x['nom'],dec))
    ref=(x.get('reference_archives') or '').split('Mémoire des hommes (ministère des Armées) —')[0].rstrip()
    x['reference_archives']=(ref+'\n' if ref else '')+txt
    fld='sources' if key[0]=='h' else 'sources_complementaires'
    L=x.setdefault(fld,[]); u=ARK+ark
    if ark and not any(s.get('url')==u for s in L): L.append({'label':'Mémoire des hommes — fiches officielles (SHD)','url':u})
    st[key[0]]+=1
IDX={(h['nom'],h.get('prenom')):h for h in H}
for nom,pre,ds,dec in st['diff']:
    h=IDX[(nom,pre)]
    if ds.startswith('situation'): note=f"À vérifier : nos tableaux le donnent évadé ou libéré, mais Mémoire des hommes enregistre un décès le {dec}."
    else: note=f"Écart de date : nos tableaux indiquent un décès le {ds}, Mémoire des hommes enregistre le {dec}."
    o=(h.get('observations') or '').strip()
    if note not in o: h['observations']=(o+' '+note).strip() if o and o!='—' else note
open(P,'w').write(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
print('hommes',st['h'],'femmes',st['f']);print('SKIP',st['skip']);print('NODEATH',st['nodeath']);print('DIFF',len(st['diff']));[print(' ',z) for z in st['diff']]
