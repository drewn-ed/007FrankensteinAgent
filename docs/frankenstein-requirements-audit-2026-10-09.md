# Frankenstein: audit požadavků a posouzení pivotů

**Verdikt k 9. 10. 2026, přibližně 04:23 Europe/Prague: kompletní splnění není doložené.** Tvorba otestovaných schopností, opravy a reuse mají skutečné důkazy. Agentem vytvořená správa/discovery a skládání více schopností v čisté session je stále potřeba předvést. Nový nezávislý průchod zastavily chyby poskytovatele; není označený za úspěšný ani nahrazený simulací.

## Zdroje a rozsah

- Dnes znovu přečtené přihlášené [HQ — Frankenstein](https://hq.agents007.ai/topics#frankenstein), [odevzdání](https://hq.agents007.ai/submit) a [tým](https://hq.agents007.ai/team). Požadavky se shodují s uloženým briefem. Z HQ se neukládá surový export ani pozvánka.
- Testovaný izolovaný snapshot pracovního stromu: [otisky zdrojů](review-evidence-2026-10-09/requirements/source-hashes.json). Nejde pouze o commit `be1328d`, protože implementační změny nejsou commitnuté. Vlastní aplikace a databáze na portu 8767 nebyly tímto auditem měněné.
- **39 automatických testů prošlo**, včetně skutečného Dockeru, Chrome a nových regresních testů předchozích závad. [Výstup](review-evidence-2026-10-09/requirements/infra-tests.txt). To potvrzuje konkrétní hranice, nikoli celý soutěžní scénář.
- [Předchozí nezávislé UI review](functional-review-2026-10-09.md) dokládá skutečnou tvorbu, opravu a reuse. Čtyři jeho hlavní závady mají nyní v testovaném snapshotu opravy a procházející regresní testy; celý předchozí UI průchod nebyl znovu opakován.
- MAIN během auditu dál měnil browser část `engine.py` (práce se zbývajícím rozpočtem a kontrola původu účastníků). Tyto pozdější změny nejsou vydávané za součást testovaného snapshotu. Nemění zde popsaný počet automatických oprav skillu ani modelový limit.

## Co znamená „loopuje a zlepšuje se“

Brief požaduje ohraničené samorozšiřování a trvalé znovupoužití. Nepožaduje nekonečný běh, změny vah ani automatické zlepšení po každém úkolu. Další iterace bez měřitelného přínosu nejsou zlepšení.

Současný engine má tři odlišné cesty:

1. **Vznik schopnosti:** plánovač odhalí mezeru, jiný kontext sestaví testy, builder napíše kód. Pokud testy selžou, dostane kód jednu automatickou opravu. Pokud znovu neprojde, běh se zastaví a schopnost se neinstaluje.
2. **Oprava na podnět uživatele:** nový test musí nejdřív odhalit chybu staré verze. Dva kandidáty se zkontrolují proti starým i novým testům. První úspěšný se uloží jako další verze. To je doložené zlepšení pro konkrétní regresní případ, ne důkaz celkově vyšší inteligence nebo rychlosti.
3. **Selhání již uloženého skillu při použití:** nyní se běh ukončí. Nevzniká automaticky nový regresní test, oprava a bezpečné zopakování. Neplatný JSON od modelu také není uvnitř stejného běhu automaticky opravovaný.

Nová [deterministická sonda](review-evidence-2026-10-09/requirements/loop_probes.py) ve skutečném Dockeru potvrdila obě hranice: neúspěšná tvorba → jedna oprava → úspěšné testy → instalace; ale pozdější výjimka při použití → `failed`, jedno modelové volání, žádná oprava, registr beze změny. [Výsledky](review-evidence-2026-10-09/requirements/loop-probes.json). Model i schopnost v této sondě jsou výslovně ručně napsané testovací náhrady a **nepočítají se jako vznik schopnosti pro soutěž**.

## Kontrola všech technických požadavků tracku

„Ověřeno“ znamená konkrétní průchod nebo kontrolu, ne univerzální záruku.

| Požadavek HQ | Stav | Důkaz nebo chybějící část |
| --- | --- | --- |
| Skutečný úkol odhalí chybějící schopnost | Ověřeno v předchozím běhu | CSV zadání vyvolalo nový skill bez pokynu vytvořit konkrétní nástroj. Uživatelská hodnota tohoto scénáře ještě nemá externí validaci. |
| Agent schopnost sám vytvoří | Ověřeno | Gemini vytvořil Python v čistém registru; nejde pouze o výběr knihovny. |
| Explicitní rozhraní a oprávnění | Ověřeno | Vstupní/výstupní JSON schéma, verze, původ, `permissions=["compute"]`. |
| Spustitelné testy před instalací | Ověřeno | Testovací brána a negativní test neúspěšné verze. Testy vytvořené modelem nejsou důkaz univerzální správnosti. |
| Testy a jejich výsledek viditelné v logu | Ověřeno | `test_plan`, `tests_failed`, `tests_passed`, `installed`; detail i v UI. |
| Úkol po tvorbě skutečně dokončen | Ověřeno pro CSV | Browser nový scénář zůstává k ověření. Nový složený scénář v tomto auditu nezačal úspěšně. |
| Agent vytvoří/rozšíří discovery a správu | **Nedoloženo** | Nový `catalog.py` definuje protokol, hostitel ukládá index a ověřuje metadata. Algoritmus má napsat agent. Procházející testy protokolu ani ručně napsaná infrastruktura nejsou důkaz takového vzniku. V přečtených validačních bězích není úspěšná generace a použití katalogového skillu. |
| Nová session zachová schopnosti | Ověřeno | Předchozí průchody a restart Store potvrzují persistence a reuse. |
| Jiný úkol v čisté session kombinuje více vzniklých schopností | **Nedoloženo** | Reuse jedné schopnosti nestačí. Připravený nový test má samostatné procesy a prázdný konverzační kontext, ale poskytovatel zastavil první fázi. |
| Žádné nové vytváření ani ruční propojení ve druhé session | **Nedoloženo pro kombinaci** | Potřebujeme sled událostí s několika dřívějšími ID/verzemi, správným předáním dat a bez `installed`/nových verzí. |
| Generovaný kód jen v sandboxu bez hostitelských credentials | Ověřeno v testovaném rozsahu | Docker bez sítě, připojeného workspace, hostitelského klíče, se zamčeným rootem a limity. Nejde o certifikaci sandboxu. |
| Schopnosti přibývají, oprávnění se nezvětšují | Ověřené mechanismy; celý průchod zbývá | Manifest odmítá rozšíření práv, browser plán nezíská nový origin. Regresní test blokuje i redirect. Finální demo musí zachovat a ukázat hranice před/po. |
| Vlastní iterace omezené kódem | Ověřeno | Aktuálně načtené nastavení: 12 modelových volání, 240 s, 8192 výstupních tokenů na odpověď; počítají se i selhání, sandbox má vlastní limity. |
| Útrata na běh omezená kódem | **Podmíněné / mezera** | Free potvrzení, allowlist modelů, omezená volání a žádný placený fallback. Chybí samostatný peněžní rozpočet s rezervací před voláním. Měření ceny po volání je pouze evidence. Odhad $0 závisí na skutečném Free projektu; aplikace billing neověřuje. |
| Kontrola operátorem | Ověřeno | Detail registru, deaktivace, výběr otestované verze, oprava a Stop; externí browser kroky mají schválení. Instalaci může schvalovat člověk, ale samostatná instalační brána není povinná. |
| Žádné podvržené předpřipravené „generované“ nástroje | Splněno v nezávislém UI důkazu | Před tvorbou byl registr prázdný. Ručně napsaná infrastruktura a testovací náhrady jsou označené odděleně. Finální video musí registr před během ukázat. |
| Žádný fine-tuning ani neotestované změny core loopu za běhu | V kontrolovaných cestách splněno | Běžící produkt vytváří omezené schopnosti; nemění vlastní engine ani systémový prompt. Vývojové změny MAIN jsou jiná věc. |
| Netriviální užitečné schopnosti | Částečně | Čištění registrací a práce s kapacitami mají užitečný základ. Reverzace seznamu jmen z diagnostiky není vhodné soutěžní demo. |
| Nejen vestavěná funkce frameworku | Technický základ doložený | Vlastní testovací/aktivační/correction mechanismus; samotný claim „pamatuje si skills“ originalitu neprokazuje. |
| Selhání ve videu nezmizí; simulace a limity přiznané | Dosud nelze ověřit | Hotové video v HQ není. Čekání lze zrychlit, selhání se nesmí vystříhat. |

## Nový pokus o celý průchod

[Harness](review-evidence-2026-10-09/requirements/live_acceptance.py) má čistou izolovanou databázi, skutečný Gemini/Docker, žádné předpřipravené skills a samostatný OS proces pro každou fázi:

1. Vyčistit syntetické CSV registrací, odstranit duplicity, zachovat skupiny a preference.
2. Z přiložených strukturovaných registrací rozdělit celé skupiny do kapacit podle preferencí.
3. V novém procesu dostat jiné raw CSV a po ztrátě velké místnosti připravit nové rozmístění. Očekávaná kombinace: načtení/validace a přidělení míst. Zadání nejmenuje žádné ID nástroje ani nepřikazuje „vytvoř tool X“.

První fáze skončila po jednom volání na [neplatném JSON](review-evidence-2026-10-09/requirements/live-1-initial-failed.json). Jediný explicitní retry skončil po jednom volání na [HTTP 429 / vyčerpané kvótě](review-evidence-2026-10-09/requirements/live-1.json). Registr zůstal prázdný, další fáze nebyly spuštěné. Nejde o důkaz, že skládání nikdy fungovat nemůže; jde o chybějící úspěšný akceptační důkaz. Model ani tarif nebyl změněn.

## Ground rules, hodnocení a odevzdání

| Bod | Aktuální stav |
| --- | --- |
| Sólo nebo max. tři členové | HQ ukazuje jednoho člena a správný track Frankenstein. |
| Registrace HQ a Luma | HQ přihlášení a tým ověřené; Luma tímto auditem neověřená. |
| Projekt vzniká od kick-offu; knihovny/boilerplate povolené | Ve zdrojích se odděluje infrastruktura od vzniklých schopností; celý původ práce nelze potvrdit unit testy. |
| Veřejné repo | `gh repo view` potvrdilo PUBLIC pro [007FrankensteinAgent](https://github.com/drewn-ed/007FrankensteinAgent). Aktuální změny jsou necommitnuté. |
| Repo propojené v HQ | **Chybí** na stránce týmu i v odevzdání. |
| Odevzdání před 07:14 dne 9. 10. | **Není odevzdané.** HQ ukazuje prázdný DRAFT, Submit je neaktivní. |
| Název, jednovětý pitch | Prázdné. |
| Popis problému/uživatele/řešení do 3000 znaků | Prázdný. |
| Funkční celý scénář do 2000 znaků | Prázdný. |
| Simulace, chybějící části a limity do 2000 znaků | Prázdné. |
| YouTube Unlisted, max. 90 s, běžící produkt | Odkaz není vyplněný; existence jiného hotového videa nebyla ověřovaná. |
| Poslední commit před freeze | Změny bude nutné commitnout a pushnout; samotné lokální soubory porota nedostane. |
| Live demo, stack, ElevenLabs | Volitelné. |
| 60sekundový živý pitch | Davidův požadavek; nikoli dodatečně nalezená technická podmínka HQ. |
| IP zůstává týmu | Pravidlo akce, nikoli funkce k testování. |

Hodnocení je stále 35 % hodnota/relevance, 25 % originalita, 20 % fungující scénář, 10 % technika, 10 % validace a přiznané limity. Skóre nelze odvodit z počtu prošlých testů. Tvorba schopností sama nezodpovídá, proč je konkrétní uživatel potřebuje.

## Upřímné posouzení PATCH / BLACKOUT / ACCESS

**PATCH je nejlepší produktové vysvětlení ze tří; ještě není prokázané odlišení.** „Doplní chybějící funkci“ slibuje konkrétní výsledek. Přínos může být nová rozhodovací logika — například držet skupiny pohromadě a respektovat kapacity — kterou cílová aplikace nemá. Pokud jen přidáme tlačítko ke stejnému chatu nebo přehrajeme klikání, tak jsme hlavně změnili obal. Samostatný panel také není změna zdrojového kódu či backendu cizí aplikace; pitch to musí popsat přesně.

Workshopový příklad je vhodný test, protože má kontrolovatelné výsledky. Zatím ale nemáme potvrzeného organizátora, jeho skutečný systém ani důkaz, že tuto práci řeší ručně. Practice app nemá kompletní model čekací listiny a kapacit potřebný pro celý navržený příběh. Nesmí se tvářit jako hotová integrace. Pro dnešek bych zachoval engine, zvolil jeden panel a konkrétní operaci, místo stavby obecného systému doplňujícího funkce do libovolných aplikací.

**BLACKOUT dává silný měřitelný vedlejší důkaz, slabší samostatnou originalitu.** Spouštění uloženého kódu bez LLM je očekávatelná vlastnost programu; samo o sobě není nový druh agenta. Smysl má, pokud přináší skutečnou provozní kontinuitu, nižší latenci nebo náklady.

Ověřil jsem to prakticky: dříve skutečně vygenerovaný CSV skill v2 z nezávislého UI testu zpracoval čerstvá data v Dockeru bez sítě, bez vytvoření modelového adaptéru a s **0 modelovými voláními**. Správně zachoval dva různé kontakty bez emailu a odstranil duplicitní neprázdný email. [Důkaz](review-evidence-2026-10-09/requirements/blackout-probe.json). Je to přímé vývojářské spuštění, **ne hotová funkce dnešního UI**. Nové zadání v přirozeném jazyce nadále potřebuje plánovač/model; externí web může potřebovat internet. V demu proto lze odpojit modelový přístup, ale nelze bez důkazu slibovat offline provoz celé aplikace.

**ACCESS bych dnes nevolil jako hlavní pivot.** Jednodušší ovládání může být hodnotné, ale přístupnost vyžaduje konkrétní uživatele a ověření jejich úloh, chybových stavů a způsobu ovládání. Větší tlačítka a hlas samy nestačí. Bez tohoto ověření je obhajitelný osobní panel pro časté operace, nikoli prokázaná dostupnost softwaru pro určitou skupinu lidí.

Originalitu nelze opřít pouze o učení a knihovnu: [Hermes Skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) dokumentuje tvorbu, změny a reuse, [Curator](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator) údržbu a volitelnou konsolidaci. [Bardeen](https://www.bardeen.ai/posts/automation-assistant-beta) popisuje návrhy automatizací z pozorovaného chování. Tyto primární zdroje byly znovu přečtené; nejde o nezávislé porovnání skutečné kvality produktů.

Moje volba: **PATCH jako srozumitelný scénář, BLACKOUT jako volitelný důkaz po dokončení povinného průchodu, ACCESS odložit.** Hlavní odlišení musí být vidět: nová užitečná logika vznikne za běhu, neúspěšný kandidát se neinstaluje, konkrétní oprava zachová staré testy a další úkol složí vzniklé schopnosti bez nové tvorby. Vlastní kód je dobrý základ, ale nestačí k tvrzení o převaze nad Hermesem.

## Nejbližší práce podle priority

1. Uzavřít jeden užitečný scénář a ověřit očekávané výsledky ručně připravenými případy.
2. Po obnovení dostupnosti modelu zaznamenat skutečnou generaci discovery/správy a skládání několika schopností po restartu. Selhání zachovat.
3. Doplnit nebo přesně vymezit vynucení finančního rozpočtu; neoznačovat statistiku ceny za limit.
4. Natočit pravdivý průchod, commitnout/pushnout ověřený stav a vyplnit skutečné odevzdání.
5. Teprve potom rozšiřovat panel nebo přidat model-free spuštění uložené operace.

Audit neupravoval implementaci ani pravidla, neměnil model/tarif, nic neodeslal do HQ, nepushoval a nekontaktoval jiného agenta či organizátory.
