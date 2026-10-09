# První implementace — 9. 10. 2026

David autorizoval zahájení stavby; konkrétní cílová aplikace ani finální název nejsou zvolené.

Typografii a vizuální identitu David řeší samostatně s jiným agentem. Funkční rozhraní používá dočasný styl; výstupy v `design/` nepřepisovat.

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
- První runner zpracovává explicitně dodaná data; neovládá prohlížeč ani aplikace.
- Modelový autor testů není nezávislý důkaz správnosti. Důležité očekávané výsledky musí potvrdit člověk nebo pevný zdroj.
- Docker je ochranná hranice nočního prototypu, nikoli certifikovaný víceuživatelský sandbox.
- Discovery a skládání nejsou splněné pouhou existencí registru. Vyžadují zaznamenaný skutečný průchod.
- Přístup k seznamu modelů neověřuje tarif ani úspěšnou inferenci; nulová útrata vyžaduje Free projekt.
