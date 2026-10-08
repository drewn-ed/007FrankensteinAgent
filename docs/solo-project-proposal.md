# Nový sólo projekt — návrh zadání

> **Tento návrh není aktivním směrem:** David jej odmítl jako příliš úzký. Aktuální diskuse se týká [učení agenta z workflow a hodnocení webů](learning-agent-concepts.md). Níže zůstává historický návrh pro dohledání úvah.

**8. 10. 2026, večer Praha.** Pracovní doporučení pro Davida; nejde o schválený produkt, zvolený stack ani příslib dokončení. David výslovně potvrdil **Frankenstein sólo**, uzávěrka podle briefu je 9. 10. v 07:14. Podle dříve ověřeného briefu je jednočlenný tým povolený; změna registrace musí být potvrzená v HQ/organizátory.

## Doporučený problém

Člověk v malé firmě potřebuje porovnat cenové nabídky dodavatelů. Každá má jiný formát a jinak uvádí jednotky, balení a dopravu. Opakovaně je převádí do společné tabulky; při změně objednávky musí propočet upravit.

Navržený produkt: **agent, který se naučí zpracovávat nabídky konkrétních dodavatelů, ověří své převody a znovu je použije pro jiný nákupní úkol.** Název zatím nevybíráme.

Podklad: [diskuse r/procurement](https://www.reddit.com/r/procurement/comments/1nnhsbn/how_do_you_handle_bid_comparisons/) popisuje ruční srovnávání souborů a různé cenové základy; [r/estimators](https://www.reddit.com/r/estimators/comments/1jk85xd/talk_to_me_about_your_love_of_bid_leveling_gc/) obsahuje zkušenosti s používáním Excelu i vedle specializovaného softwaru. Jedná se o jednotlivá svědectví, nikoli reprezentativní průzkum nebo ověřenou ochotu platit. Konkrétní první segment níže je náš návrh, ne přímo potvrzený zákazník.

## Rozsah zvládnutelný pro první pokus

- Jeden typ nákupu: například balicí materiál pro malý e-shop, jasné SKU a množství v kusech/baleních.
- Dva dodavatelé, dva textové/CSV formáty a jedna měna; ceny se stejným daňovým základem. Syntetická data tak označit.
- Jedna obrazovka: vstupy, viditelné kroky agenta, vytvořené schopnosti s testy a srovnání výsledku.
- Bez napojení na firemní účty a bez zadávání objednávky; prototyp pracuje s nahranými soubory. OCR a obecný výklad smluv nejsou součástí první verze.

## Dva úkoly pro skutečného Frankensteina

**Úkol A — porovnej nabídky:** „Porovnej cenu této objednávky u obou dodavatelů, včetně dopravy, a ukaž nejasné položky.“ Agent z úkolu odhalí nepodporované formáty či cenové jednotky. V izolovaném běhu vytvoří potřebné adaptéry/kalkulační schopnosti, otestuje je a až potom zaregistruje. Musí rovněž vytvořit nebo rozšířit vyhledávání a správu těchto schopností, například index jejich vstupů, výstupů a podmínek použitelnosti. Příklady schopností nejsou předem napsanými nástroji vydávanými za výtvor agenta.

**Úkol B — jiný úkol v nové session:** „Zkontroluj tuto fakturu vůči uložené nabídce a označ odlišnou jednotkovou cenu, balení nebo dopravné.“ Faktura pro první prototyp používá jednoduché předem podporované tabulkové schéma. Agent s prázdným konverzačním kontextem najde a zkombinuje dříve vytvořený adaptér nabídky a cenovou normalizaci. Doloží použité verze bez jejich znovuvytváření. Konkrétní rozdíly porovná s ručně připraveným očekávaným výsledkem.

Tím je druhý úkol odlišný od pouhého opakování s jiným množstvím. Přesnou hranici základních funkcí a nově vznikajících schopností je nutné ověřit prototypem. Nezávislé kontrolní příklady jsou přípustné; předpřipravené schopnosti vydávané za nově vytvořené nejsou.

## Podmínky, bez kterých zadání nesplníme

- Generovaný kód izolovaný od hostitele s přístupovými údaji; pevná oprávnění a kódem omezené iterace/útrata.
- Viditelné testy před registrací. Neúspěch instalaci blokuje.
- Zachování SKU, správný přepočet balení, dohledatelnost zdrojových hodnot a explicitní označení chybějících údajů. Nedoplňovat neznámou cenu nulou.
- Trvalé schopnosti, agentem rozvíjené discovery/správa a jejich použití v nové session.
- Pravdivý záznam prvního i druhého úkolu; žádné tvrzení o ušetřeném čase bez měření.

## Originalita a největší nejistota

[Opstream](https://www.opstream.ai/) a další procurement nástroje již existují. Také běžný AI asistent dokáže jednorázově srovnávat dokumenty. Náš předpokládaný přínos je viditelný vznik otestovaných schopností a jejich přenos mezi porovnáním nabídky a kontrolou faktury. Rešerše nepotvrdila, že tuto kombinaci nikdo jiný nemá. Netvrdit prvenství ani univerzální správnost.

Proti původnímu směru dodavatelských importů volíme užší kontrolovatelný nákupní scénář: předchozí rešerše našla velmi přímé překrytí importů s Matrixify MCP. Cenou za tuto volbu je náročnější ověření významu cen, které omezujeme explicitními položkami, jednotkami a jedním typem nákupu.

## Postup po výběru směru

1. Krátká technická zkouška: ověřit dostupný model, sandbox a skutečné vygenerování/testování jedné užitečné schopnosti. Neřešit nejdřív značku nebo landing page.
2. Dokončit první úkol, poté novou session a druhý úkol. Pokud nejde doložit opakované použití, řešit tento mechanismus před vizuálními detaily.
3. Přidat čitelný přehled výsledků a důkazů; ověřit nezávislý kontrolní vzorek.
4. Vyhradit posledních přibližně 90 minut na záznam dema do 90 sekund, minutový pitch, repo a odevzdání. Časy jsou plánovací rezerva, ne záruka vývoje.

David může průběžně ověřovat srozumitelnost a výsledky, přinést zpětnou vazbu od mentora a připravovat pitch. Implementace v tomto chatu začne až po výběru směru; žádná změna týmu, repozitářových přístupů ani odevzdání tímto návrhem neproběhla.
