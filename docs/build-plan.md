# První implementace — 9. 10. 2026

David autorizoval zahájení stavby. Později 9. 10. potvrdil název **Wisp**; rané produktové úvahy níže zachovávají svůj původní kontext.

Typografii a vizuální identitu David řeší samostatně s jiným agentem. Rozhraní přebírá aktuální tokeny, písma a Nucleo ikony přímo z `design/`; tyto zdroje nepřepisovat.

## Aktuální funkční verze

Na Davidův navazující požadavek je frontend zapojený na skutečný engine. Používá schválené logo z `design/logo/`, aktuální typografii a navigaci podle Codexu. Chat zobrazuje skutečné události, výsledek a důkazy. Umí přílohy, zastavení běhu, opravu schopnosti s volitelným konkrétním testem, historii verzí, deaktivaci, obnovení otestované verze a export. Projekty, instrukce, chaty a ručně spouštěné workflows jsou uložené na lokálním serveru. Projektové schopnosti se nemíchají mezi projekty; sdílené schopnosti jsou dostupné všem.

Položka Computer připojuje samostatnou session Chrome k jedné stránce. Pevný konektor mapuje viditelné prvky, pořizuje náhled a provádí omezené operace (kliknutí, vyplnění, výběr, checkbox, klávesa, navigace v připojeném originu). Cizí síťové originy jsou blokované včetně vedlejších zdrojů. Interakce s externími stránkami čekají na schválení jednotlivého kroku; lokální practice aplikace běží bez této brány. Nejde o ovládání všech nativních aplikací ani import osobního prohlížeče.

Agentem generovaný `browser_plan` je stále čistý Python v Dockeru s oprávněním `compute`. Vytváří parametrizovaný deklarativní postup. Pevný hostitelský konektor po kontrole formátu a originu přemapuje názvy ovládacích prvků, provede jednotlivé kroky a ověří očekávaný text. Generovaný kód nedostává přístup na hostitele. Testy vzniku plánu se ověřují i proti skutečně pozorovaným názvům a hodnotám prvků; samy nejsou důkazem funkčnosti libovolné stránky.

Ověřeno: skutečná tvorba browser plánu, zablokování první chybné implementace testy, modelová oprava do v2, zachování starých testů a dva nové běhy využívající v2 bez další tvorby. Podrobnosti v `docs/build-validation.md`. Stále chybí doložená kombinace několika schopností a agentem vytvořená správa pro kompletní soutěžní průchod.

## Rozsah prvního průchodu

1. Lokální pracovní rozhraní: úkol, vstupní data, výsledek a skutečný průběh práce.
2. Gemini jako první poskytovatel. Pouze potvrzený Free projekt, omezený počet volání, výstupních tokenů a délka běhu; bez automatického přechodu na placený model.
3. Generované Python schopnosti s JSON rozhraním. Spouštění pouze v Dockeru bez sítě, přístupových údajů a připojeného pracovního adresáře.
4. Druhý modelový kontext navrhuje testovací případy podle rozhraní a zadání, bez znalosti implementace. Hostitel porovnává očekávané a skutečné výsledky.
5. Trvalý registr verzí, oprávnění, původu a výsledků testů. Neúspěšná verze se neaktivuje.
6. Oprava uživatele vytvoří test; současná verze musí prokazatelně selhat. Opravená verze musí projít novými i staršími případy.
7. Nová session zachová pouze registr a deklarované artefakty. Jiný úkol musí skutečně použít dřívější schopnosti.

## Pořadí

- Připojení modelu a izolovaný runner; ověřit zamítnutí chybné verze a stálá oprávnění.
- Registr, orchestrátor a přehledné rozhraní se skutečnými událostmi.
- Skutečný modelový běh, oprava a přenos do nové session.
- Agentem rozvíjené vyhledávání/správa, závěrečné důkazy a scénář dema.

## Limity, které zatím platí

- Poptávka ani odlišení produktu nejsou ověřené. Není vybraný konečný obor ani integrace.
- Podpora ovládání je omezena na samostatný Chrome a jeden origin. Nativní aplikace, upload/download přes agenta, přihlášení napříč originy, plánovač, týmové sdílení a plné převzetí/obnovení nejsou hotové. Mobilní responzivita a úplný audit přístupnosti zůstávají další fází.
- Modelový autor testů není nezávislý důkaz správnosti. Důležité očekávané výsledky musí potvrdit člověk nebo pevný zdroj.
- Docker je ochranná hranice nočního prototypu, nikoli certifikovaný víceuživatelský sandbox.
- Discovery a skládání nejsou splněné pouhou existencí registru. Vyžadují zaznamenaný skutečný průchod.
- Přístup k seznamu modelů neověřuje tarif ani úspěšnou inferenci; nulová útrata vyžaduje Free projekt.
