# Ověření první implementace

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

## Co stále chybí

- Agentem vytvořené/rozšířené vyhledávání a správa schopností. Ručně napsaný registr se za to nepočítá.
- Jiný pracovní úkol v nové session, který skutečně zkombinuje více dříve vzniklých schopností.
- Prokázání výhody oproti agentovi bez zkušenosti a s pouhým textovým shrnutím.
- Potvrzený název, cílový uživatel, finální demo, veřejně pushnutá implementace a video.
- Převzetí vizuální identity od druhého agenta. Typografie je mimo aktuální implementační práci.

Všechny vstupy v těchto kontrolách byly syntetické. Žádné webové účty, registrace skutečných lidí ani externí publikování se nepoužívaly.
