Latest extension: [files, desktop, schedules and complex event showcase](operations-extension-2026-10-09.md). Includes 57 passing tests, three completed live event tasks and the remaining native-permission/discovery limits.

# Ověření první implementace

Latest follow-up: [functional review fixes and preserved failures](review-fixes-2026-10-09.md). The current full suite passed 41 tests; the historical checkpoints below remain unchanged.

Záznam 9. 10. 2026, lokální vývojová větev `codex/learning-agent-mvp`. Nejde o finální soutěžní demo ani ověření poptávky.

## Skutečně provedené kontroly

- `uv run python -m unittest discover -s tests -v`: **9 testů prošlo**. Testy skutečně spouštějí Docker; chybějící Docker nesmí vyústit v tiché přeskočení.
- Ověřeno: neúspěšná verze nezmění aktivní registr; rozšíření práv je odmítnuté; generovaný kód nedostane hostitelský klíč, síť ani zapisovatelný root; nekonečný běh i nadměrný výstup se zastaví; nový Store načte přetrvávající schopnosti; deaktivace se projeví; limity volání/času a brána Free tarifu fungují; HTTP 429 nespouští placený fallback; externí JSON schema reference jsou odmítnuté; nový opravný test zachová staré kontroly; nadbytečné pole s kódem neprojde k autorovi testů.
- Playwright + instalovaný Chrome: vložení syntetického příkladu, přepínání práce/knihovny, desktop 1440 px a mobil 390 px. Žádná zachycená chyba JS, žádný horizontální přesah na mobilu.
- API health/state a hlavní stránka odpovídají HTTP 200; požadavek s cizím Origin byl odmítnut HTTP 403.
- `.env` i runtime databáze jsou ignorované Gitem; lokální `.env` má práva 0600. Poskytovatelské odpovědi se nevypisují do chybových logů.

## Skutečný modelový průchod

Model: `gemini-3.5-flash-lite`. Free tarif potvrdil David. Před prvním během každého ověřovaného registru nebyly vložené žádné schopnosti.

1. CLI nad syntetickými registracemi: model vytvořil `process_workshop_registrations`, tři testy prošly a schopnost se zaregistrovala. Další modelové volání skončilo HTTP 503. Selhání zůstalo v záznamu.
2. Nový proces a jiné znění úkolu: uložená schopnost byla skutečně vykonána, registr před/po měl stejný hash a úkol skončil správným přehledem. Design: 3 rezervovaná místa, kapacita 2, přetíženo; AI: 1 místo, kapacita 3. Toto je reuse jedné schopnosti, **nikoli povinná kombinace několika schopností**.
3. Webové UI: syntetické tři registrace prošly skutečným modelem, vytvořením a použitím `clean_registrations`; výsledek měl dva jedinečné záznamy a jednu odstraněnou duplicitu.
4. Skutečný opravný běh: explicitní případ obsahoval dva různé lidi bez emailu na stejném workshopu. Původní verze jednoho odstranila, nový test selhal. Dvě modelové implementace prošly všemi pěti testy; první úspěšná byla uložena jako v2. Pořadí kandidátů není tvrzení o jejich rychlosti či ekonomické výhodě.

## Zjištěná chyba a její oprava

Při prvních bězích model přidal `code` přímo do objektu manifestu. To se dostalo i do zadání testovacímu kontextu. Přestože se testy skutečně vykonaly, **první modelové testy nelze označovat za vytvořené bez znalosti implementace**.

Oprava zavádí pevný seznam povolených polí manifestu ještě před tvorbou zadání pro testy, zápisem a inventářem. Regresní test pokrývá cestu od modelové odpovědi přes autora testů až po registr. Staré logy nejsou přepsané tak, aby chyba zmizela. Následující soutěžní demonstrace musí použít nový registr a zkontrolovat skutečný obsah předaných kontraktů.

## Navazující ověření živého UI a ovládání prohlížeče

- Aktuální sada `python -m unittest discover -s tests -v`: **22 testů prošlo**. Zahrnuje skutečný Docker, skutečný Chrome, projektovou izolaci, historii/aktivaci verzí, zrušení běhu, bránu externích interakcí, nemožnost rozšířit origin uloženým plánem, kontrolu mapování prvků a nepřenášení hodnot polí do trvalé mapy aplikace.
- Playwright + Chrome, 1440 × 1000 a 1280 × 800: **19 kontrol UI prošlo**, včetně skutečné deaktivace/opětovné aktivace, prohlížení verzí, opravného případu, serverového ukládání instrukcí, workflow a důkazů běhu. Poslední průchod neměl chybu JavaScriptu ani neúspěšné načtení prostředku. Lokální zpráva: `.runtime/live-verification/ui-report.json`.
- Skutečný model ovládl lokální registrační formulář: vyplnil a odeslal syntetického účastníka, zvolil workshop a zaškrtnutí a pozoroval zápis na stránce. Šest volání modelu, přibližně sedm sekund. Pevný browser konektor je týmový kód, ne schopnost vytvořená agentem.
- Model vytvořil parametrizovaný browser plán. První kandidát neprošel 0/3 testů, jeden opravný pokus prošel 3/3 a vznikla verze 1. Následné provedení zapsalo dva účastníky a ověřilo je. Šest modelových volání, přibližně 16 sekund v tomto běhu.
- Další session skutečně použila v1 bez nové tvorby, ale ověření selhalo: plán předpokládal prázdný seznam a očekával `1 registered`, přestože stránka správně obsahovala tři účastníky. Výsledek není vydáván za úspěch.
- Oprava s explicitním regresním případem přidala volitelný `existing_count`. Starý kód v novém případu selhal; oba modelové kandidáty prošly všemi čtyřmi testy. Vznikla v2. Staré případy, požadované vstupy a oprávnění zůstaly zachované. Volitelný vstup a změna popisu jsou viditelné v manifestu nové verze; starý manifest se nepřepsal.
- Dvě nové session použily v2 s novými účastníky a různými workshopy. Obě zaznamenaly `used` a `browser_verified`, žádná `installed`. Dvě volání modelu v každé, přibližně 4 a 3 sekundy. První pracovala s prázdnou stránkou, druhá s již existujícím účastníkem. Jde o jednotlivé diagnostické běhy, nikoli benchmark nebo důkaz škálovatelnosti.

Při vývoji nastala také starší chyba: autor testů neviděl skutečné mapování a vymyslel selektory i origin. Přestože čisté výstupní testy prošly, takový plán nebyl vhodný k provedení. Kandidát je deaktivovaný. Nový typ `browser_plan` má pevné výstupní schéma; oba modelové kontexty dostávají pozorované prvky a host kontroluje cíle a hodnoty selectů před aktivací. Selhání prvního běhu na limitu modelových volání i selhání kontroly počtu zůstala v SQLite a byla exportována do `.runtime/live-verification/failed-*.json`.

Lokální důkazy úspěšné opravy a opakování jsou v `.runtime/live-verification/browser-plan-correction.json`, `browser-reuse-one.json` a `browser-reuse-two.json`. Jejich surová data nejsou veřejnou přílohou dokumentace. Ovládání externího účtu nebylo použito. Practice app je lokálně doručená do samostatného Chrome pod virtuálním originem `https://workspace.demo`; formulář a klikání jsou skutečné, jména a emaily syntetické.

## Usage and overview verification (9 October)

- The full infrastructure suite passed **30 tests**, including eight accounting tests. The new checks cover cache/thinking token calculation, missing metadata, HTTP failure, malformed generated JSON with consumed tokens, pending calls, persisted metadata, prior-version provenance and history beyond the 30-run chat window. A lowercase `standard` service tier observed in the live provider response is covered by regression assertions; unknown service tiers do not receive a standard-rate comparison.
- A real Free-tier Gemini run normalized three synthetic workshop registrations into two entries and removed one duplicate. It used the existing `clean_registrations` version twice, with **3 model requests and 5,163 reported tokens**, and installed no new skill. Per-call metadata was saved in SQLite. The configured Free estimate is **$0**, not a verified bill; the standard paid-rate comparison from recorded usage is **$0.0022485**. This is a metering check, not evidence of a speed or quality improvement.
- Playwright exercised the live dashboard and detail APIs: all history rows, success/failure/reuse filters, unpriced historical records, per-call details, paid-rate labeling, matching-chat navigation, task/full-history JSON export and guide entry points. Final run: **24 checks passed**, no JavaScript or HTTP errors. The narrow layout closes navigation into a drawer and supports reopening it and choosing a view; desktop 1440/1280 px and narrow 390 px were visually inspected. This is not a complete accessibility audit. Screenshots and local reports are in `.runtime/usage-verification/`; synthetic provider fixtures remain only in temporary test databases.
- Pricing: [Google Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing). Token semantics: [GenerateContent usage metadata](https://ai.google.dev/api/generate-content#UsageMetadata). Both read 2026-10-09. No paid service or billing access was enabled. Failed calls without usage, old tasks without per-call records and local compute are explicitly unpriced.

## Remaining work

- Agentem vytvořené/rozšířené vyhledávání a správa schopností. Implementovaný protokol a pevný registr se za tento důkaz nepočítají.
- Jiný úkol v nové session, který skutečně zkombinuje více dříve vzniklých schopností. Ověřené reuse jedné schopnosti toto nenahrazuje.
- Srovnání s agentem bez zkušenosti a s textovou pamětí za stejných podmínek.
- Nativní aplikace, více originů, agentem prováděný upload/download, plánování, týmové sdílení, audit přístupnosti a kompletní mobilní verze.
- Potvrzený produktový název, finální cílový uživatel, soutěžní demo, push implementace a video.

## UX simplification, 9 October 2026

- Main navigation now groups saved workflows, learned skills and schedules under Library. Project chats can collapse; recent chats initially show five entries without deleting older work.
- Completed chats show one result card and a continuation action. Files, learned skills, verification, usage and exports remain available in result details or More options. Continuing a task retains its connected application mode. Drafts survive navigation.
- Computer presents the connected application and Start a task. Preview, connection options and remembered page maps are secondary. Pending browser approvals remain visible. Overview prioritizes task history; charts and detailed learning statistics expand on request.
- Playwright verified navigation, skill filtering, result download, draft persistence, continuation mode, settings, native setup, and the result → saved workflow → schedule form path. A temporary workflow created for this check was removed; no scheduled execution was created. No model call was made for these UX checks.
- Desktop screenshots were inspected after motion settled; 390px and 320px layouts had no document overflow. The browser reported no page errors. JS syntax checks and `git diff --check` passed. This is interaction/layout verification, not a new model-performance test or a full accessibility audit. Local evidence: `.runtime/ux-review/`.
