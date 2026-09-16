# Sommer-Aktion 2026 · Mailing
20 Mails (3 Segmente × Wellen × DE/EN) aus einer Quelle, plus Gegenlese-Editor.
Voller Kontext: **CLAUDE.md**.
```
pip install -r requirements.txt && npm i -g mjml
python3 build_editor.py --publish
```
- `heroes.json` — die einzige redaktionelle Quelle (Wellen-Copy DE/EN, CTA-Labels, Motive, Wellenplan)
- `config.json` — Landing-URLs, UTM-Fix, CTA-Ziele je Welle (`wellen_ctas`), Theme, `asset_base_url`
- `links.py` — UTM-Logik (Supabase-Register); `python3 links.py` = Abgleich der 24 Registerzeilen
- `build_editor.py` — baut `dist/mail_*.html` (gehostete Bilder, < 100 KB, versandfähig) und den
  Editor; `--publish` legt Editor + Assets nach `../../apps/mail-editor/` (GitHub Pages);
  `--verify` prüft nach dem Merge, ob Editor und alle Bild-URLs live erreichbar sind
- `assets/motive/` — die 8 genutzten Motive · `assets/fonts/` — FazetaSans
- `supabase/` — Kommentar-Tabelle und Erledigt-RPC (beide auf dagcsnfrlbpxcmdimnrw angewendet)
