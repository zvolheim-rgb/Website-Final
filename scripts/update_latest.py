"""Best-effort updater for Zac Volheim's latest KPAX stories.

Reads a public article index and verifies each candidate against KPAX article
metadata. On failure, leaves the last verified data/latest.json unchanged.
This is intentionally conservative: no unverified or guessed results.
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'data' / 'latest.json'
INDEX = 'https://muckrack.com/zach-volheim/articles'
HEADERS = {'User-Agent':'Mozilla/5.0 (compatible; ZacVolheimPortfolioUpdater/1.0)'}
DATE_RE = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+20\d\d\b',re.I)

def get(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text

def article_image(soup):
    tag=soup.select_one('meta[property="og:image"],meta[name="twitter:image"],meta[property="twitter:image"]')
    candidate=(tag.get('content','') if tag else '').strip()
    parsed=urlparse(candidate)
    if parsed.scheme=='https' and parsed.hostname=='ewscripps.brightspotcdn.com':
        return candidate
    return None

def published_and_byline(url, session):
    try:
        r=session.get(url,timeout=20,headers=HEADERS)
        r.raise_for_status()
        if urlparse(r.url).hostname not in ('kpax.com','www.kpax.com'):
            return None
        soup=BeautifulSoup(r.text,'html.parser')
        for tag in soup.select('script[type="application/ld+json"]'):
            try: obj=json.loads(tag.string or tag.get_text())
            except Exception: continue
            nodes=obj if isinstance(obj,list) else obj.get('@graph',[obj]) if isinstance(obj,dict) else []
            for node in nodes:
                if not isinstance(node,dict):continue
                typ=node.get('@type',[]);typ=[typ] if isinstance(typ,str) else typ
                if not any('Article' in x for x in typ if isinstance(x,str)):continue
                author=node.get('author',[]);author=[author] if isinstance(author,(str,dict)) else author
                names=' '.join(a.get('name','') if isinstance(a,dict) else str(a) for a in author)
                if not re.search(r'\bZach Volheim\b',names,re.I):continue
                title=node.get('headline') or (soup.title.get_text(strip=True) if soup.title else '')
                date=(node.get('datePublished') or '')[:10]
                if date and title:return {'title':title.strip(),'date':date,'url':r.url,**({'image':image} if (image:=article_image(soup)) else {})}
        # Conservative fallback if article JSON-LD unavailable
        text=soup.get_text(' ',strip=True)[:12000]
        if not re.search(r'By:\s*Zach Volheim',text,re.I):return None
        date_tag=soup.select_one('meta[property="article:published_time"],meta[name="datePublished"],meta[itemprop="datePublished"]')
        date=(date_tag.get('content','')[:10] if date_tag else '')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',date):return None
        title=(soup.select_one('h1').get_text(' ',strip=True) if soup.select_one('h1') else '')
        if not title:return None
        return {'title':title,'date':date,'url':r.url,**({'image':image} if (image:=article_image(soup)) else {})}
    except (requests.RequestException,ValueError):return None

def main():
    soup=BeautifulSoup(get(INDEX),'html.parser')
    session=requests.Session()
    candidates=[]
    # Public index lists article cards with KPAX outbound links.
    # Do not trust any byline metadata from the third-party site alone.
    for a in soup.select('a[href]'):
        href=urljoin(INDEX,a['href'])
        host=urlparse(href).hostname
        if host not in ('kpax.com','www.kpax.com'):continue
        if '/news/' not in urlparse(href).path:continue
        if href not in candidates:candidates.append(href)
    found=[];seen=set()
    for url in candidates[:40]:
        item=published_and_byline(url,session)
        if item and item['url'] not in seen:
            found.append(item);seen.add(item['url'])
        if len(found)>=12:break
    found.sort(key=lambda a:a['date'],reverse=True)
    if len(found)<3:
        print(f'Only {len(found)} verifiable stories; keeping previously verified feed.')
        return
    selected=found[:3]
    previous=json.loads(DEST.read_text()) if DEST.exists() else []
    if selected != previous:
        DEST.write_text(json.dumps(selected,indent=2,ensure_ascii=False)+'\n')
        print('Updated three latest verified KPAX articles.')
    else:print('No changes.')

if __name__=='__main__':
    main()
