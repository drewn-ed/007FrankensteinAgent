# Review implementace pracovního agenta

Novější stav po dokončení tohoto checkpointu zachycuje [funkční review se skutečnými UI a modelovými testy](functional-review-2026-10-09.md). Níže zůstává původní kontrola z 03:26–03:33.

Backend už existuje a obsahuje vlastní engine nad Gemini, Docker sandbox, trvalý registr, verzování a opravy schopností přes regresní testy. Nejde o runtime postavený na Hermesovi. Největší mezera je mezi tímto funkčním jádrem a slibem, že se agent naučí ovládat aplikaci a příště použije otestovaný postup.

Review pro Davida a vývojový chat MAIN, 9. října 2026 přibližně 03:26–03:33 Europe/Prague. MAIN v této době aktivně mění soubory. Nálezy níže platí pro uvedený kontrolní stav; před opravou ověř aktuální kód. Tento dokument nemění AGENTS.md ani soutěžní pravidla.

## Co vývojový agent skutečně dělá

MAIN nejprve podle předchozích požadavků předělával pracovní rozhraní. Během review dokončil napojení UI na API a začal ověřovat browser scénář na místním registračním formuláři. V novém kódu jsou skutečné běhy, události, výsledky, knihovna verzí a testů, opravy, zastavení běhu, deaktivace, rollback a připojení odděleného Chrome.

Původně otevřená instance na portu 8767 při kontrole vracela pro nové API `Not found`; rozhraní zobrazilo Offline. Čerstvá izolovaná instance stejného aktuálního serveru nové UI načetla a projekt přežil obnovení stránky. Rozdíl odpovídá potřebě restartovat starší server po změně endpointů. Samotný stav staré instance tedy nedokazuje, že nová implementace nefunguje.

## Co je ověřeno

- V oddělené kopii prošlo všech **12 existujících testů**, za 15,747 sekundy. Testy zahrnují skutečný Docker sandbox, blokování neúspěšné instalace, zachování původních testů při opravě, limity a hranice katalogu. LLM odpovědi v automatických testech jsou fixtures.
- V místní databázi byly při kontrole dva dokončené skutečné běhy: vytvoření a použití `clean_registrations` a jeho oprava na v2. Registr obsahoval jednu aktivní schopnost typu `task`. To dokládá užitečné části implementace; samo o sobě to nedokládá kombinaci několika schopností ani vznik discovery nástroje.
- V izolovaném UI fungovalo načtení, vytvoření projektu, zachování projektu po reloadu a zobrazení podpory aplikací. Tato instance měla prázdnou dočasnou databázi a žádný API klíč; nebyl na ní proveden reálný modelový úkol.
- Následující tři reprodukční sondy používají syntetický model, dočasnou databázi a žádné externí služby. [Výsledky](review-evidence-2026-10-09/results.json), [spustitelný skript](review-evidence-2026-10-09/probes.py) a [identifikace testovaného stavu](review-evidence-2026-10-09/snapshot.json).

Sondy lze z kořene repozitáře zopakovat příkazem `PYTHONPATH=. .venv/bin/python docs/review-evidence-2026-10-09/probes.py`. Vypisují pozorované chování; jejich úspěšné ukončení neznamená, že popsané problémy jsou opravené.

## Nálezy k opravě

### P1 Úspěch browser úkolu nemá kontrolu výsledného stavu

V `workbench/engine.py:266` akce `finish` přijme modelový výsledek bez ověření, že požadovaná změna nastala. Sonda zadala vytvoření položky, podstrčila modelovou odpověď „vytvořeno“ a získala stav `completed`, přestože neproběhla žádná browser akce; log obsahoval jen `session` a `finished`. To je ověření reakce na chybný planner, nikoli pozorované selhání Gemini.

Pro úkol vyžadující změnu aplikace navázat dokončení na ověřitelnou podmínku výsledku a pozorování po akci. Pokud výsledek ověřit nelze, zobrazit jej jako neověřený. Regresní kontrola má odmítnout falešné dokončení i případ, kdy akce proběhne, ale očekávaný výsledek nenastane.

### P2 Paměť aplikací přechází mezi projekty

`workbench/store.py:62` ukládá mapu pouze pod origin webu; `ScopedStore` nepřepisuje `remember_app` ani `applications`. `workbench/engine.py:257` pak mapu předává modelu. Sonda uloží mapu v projektu A a načte ji v projektu B. Mapa může obsahovat názvy prvků z jiného pracovního kontextu a poslední návštěva jiného projektu ji přepíše.

Přidat explicitní scope také k mapám aplikací a ověřit dva projekty na stejné doméně. Pokud má být nějaká paměť sdílená, musí být jako sdílená označená a nesmí se vydávat za oddělenou projektovou paměť.

### P2 Důkaz změny registru porovnává různé množiny

`workbench/server.py:52` vytváří běh přes globální Store, takže `registry_before` zahrnuje všechny projekty. `workbench/engine.py:241` zapisuje `registry_after` ze scoped Store. Sonda s jednou schopností v projektu B a během v projektu A zaznamenala rozdílné hashe, i když se skutečný registr vůbec nezměnil.

Oba otisky počítat nad stejným scope a uložit jej k důkazu. Přidat kontrolu, že běh bez změn zachová shodné otisky i při existenci jiných projektů.

### P2 Běžná navazující zpráva neobsahuje předchozí výsledek

`web/app.js:89` přidává `previous_result` pouze po explicitním kliknutí na Follow up. Běžná další zpráva ve stejném chatu jej nepředá; `workbench/engine.py:245` vždy začíná s prázdnou historií. Zadání „a teď je seřaď“ tak běžným odesláním nemá předchozí data, ačkoli je uživatel v chatu vidí.

Oddělit nový nezávislý běh od pokračování stejného chatu. Pro pokračování přidávat omezený kontext a relevantní výsledek; pro důkaz nové session jej naopak prokazatelně vyčistit. Ověřit obě cesty zvlášť.

## Mezery mezi produktem a soutěžním demem

**Ovládání prohlížeče zatím není naučený browser skill.** Pevný konektor umí klikání a vyplňování; agentem generované schopnosti mají pouze oprávnění `compute` a běží jako Python nad JSON daty. Mapa aplikace obsahuje pozorované prvky, nikoli otestovaný postup s parametry a podmínkou úspěchu. Uložené workflow nyní uchovává zejména zadání a odkazy na původní skills; není tím doloženo opakované vykonání naučeného postupu.

Pro širší produkt dává smysl rozhraní browser postupu: parametry, předpoklady stránky, omezené kroky přes schválený konektor a kontrola výsledku. Postup musí vzniknout z úkolu, projít testem v kontrolovaném prostředí a být znovu použit s jinými daty. Do té doby formulovat slib přesně: agent si osvojuje a opravuje výpočetní schopnosti a má připojené ovládání webu.

**Katalog má infrastrukturu, ale soutěžní důkaz ještě vyžaduje skutečný vznik a použití.** Model dostává celý inventář při každém kroku (`engine.py:259`), takže existence discovery pluginu sama neprokazuje, že pomohl schopnosti vyhledat. V důkazech musí být agentem vytvořený plugin, jeho testy a jeho skutečně použité výsledky. Pro škálování následně oddělit vyhledané kandidáty od předávání celého registru do každého promptu.

**Druhý úkol musí být jiný, nejen stejný prompt nad jinými řádky.** Například po přípravě registračního seznamu zadat v čisté session rozdělení účastníků a čekací listiny podle kapacit. Ověřit, že tento jiný výsledek vznikl kombinací více již existujících schopností, bez nového generování a bez ručního propojování. Konkrétní scénář je návrh ověření, nikoli změna definice celého produktu.

## Vlastní přínos a rady od dalších AI

Z návrhů Gemini a Claude dává největší smysl pokračovat v již implementované opravě: zpětná vazba → konkrétní regresní test → selhání staré verze → dvě kandidátní opravy → přijetí verze, která projde novým i předchozími testy. Autor počátečních testů dostává kontrakt bez implementace. Jde o oddělené modelové kontexty, nikoli důkaz nezávislosti různých modelů; očekávané výsledky mohou být stále chybné.

Hermes už má [tvorbu a úpravy skills včetně poučení z korekcí](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills), [computer use](https://hermes-agent.nousresearch.com/docs/user-guide/features/computer-use) a [Curator](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator). Tvrzení „Hermes neumí vidět obrazovku“ nebo „neučí se z oprav“ proto není vhodné odlišení. Vlastní kód také sám o sobě neprokazuje vyšší kvalitu než Hermes.

Obhajitelná věta pro prezentaci:

> We turn user corrections into executable regression tests. A new skill version is accepted only when it passes the new case and all previous checks.

Ve videu ukázat selhání v1 na konkrétním případu, vznik v2 a zachování starých testů. Netvrdit „už nikdy neudělá stejnou chybu“, „první takový agent“ ani měřenou převahu nad Hermesem. Dvě kandidátní opravy dnes znamenají první vyhovující variantu; nejsou benchmarkem rychlosti či evolučním turnajem.

Další široké směry z konzultací — soustavné pozorování desktopu, platby lidem nebo více soutěžících agentů — nyní odvádějí práci od chybějícího důkazu. Kontrolovaná porucha a následná oprava se naopak hodí jako test stávajícího mechanismu.

## Pořadí další práce

1. Dokončit právě rozpracované propojení UI a ověřit jeden skutečný uživatelský úkol od zadání po výsledek. Restartovat server, pokud obsluhuje staré endpointy.
2. Opravit kontrolu dokončení, přenos kontextu a oba reprodukované problémy se scope; přidat cílené regresní testy.
3. Zaznamenat prázdný registr, vznik netriviálních schopností a discovery nástroje, testy a užitečný první výsledek. Nepředepisovat modelu přesné názvy nástrojů, které má vytvořit.
4. Restartovat proces a v nové session splnit jiný úkol kombinací existujících schopností. Uchovat ID, verze, počty generování a volání, výsledky a shodný rozsah oprávnění.
5. Předvést opravu přes regresní test. Pokud čas dovolí, porovnat stejný úkol bez zkušenosti, s textovým shrnutím a s otestovanými skills; jednotlivé běhy označit jako demonstraci, nikoli robustní benchmark.
6. Z těchto skutečných důkazů připravit 90sekundové video, minutový pitch a pravdivý popis limitů. Backend nezačínat znovu a další obecné funkce nepřidávat před tímto průchodem.

Pravidla a deadline zůstávají v [ověřeném briefu](hackathon-brief.md). Review nepředstavuje nové ověření HQ, odevzdání projektu ani zveřejnění videa.
