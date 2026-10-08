# Frankenstein: učení z workflow a hodnocení webů

**8. 10. 2026. Stav: rozbor a návrhy, ne vybraný produkt ani implementace.** David pokračuje sólo. Chce širší smysluplný produkt a porozumět podmínkám; původní nabídky/faktury odmítl jako příliš úzké. [Přihlášený brief](https://hq.agents007.ai/topics#frankenstein) byl při tomto rozboru znovu celý přečten.

## Aktualizace z druhého chatu — 8. 10. 2026, přibližně 23:59

Na Davidův výslovný požadavek byl přečten chat **„Najdi odbornější název projektu“**. Následující zachycuje diskusi, nikoli schválený stack či pokyn k implementaci. Starší doporučení níže zůstávají pro kontext; kontrola webů už není předpokládaným hlavním směrem.

**Aktuální Davidova představa:** asistent, který si osvojuje práci v aplikacích. Uživatel zadá konkrétní práci, agent se zorientuje v rozhraní, práci provede a získaný postup si uchová pro další použití. Při podobném požadavku s jinými vstupy nemusí znovu objevovat celou cestu. Davidovi záleží na viditelně provedené práci, hmatatelném výsledku a srozumitelném přínosu předchozí zkušenosti.

- Předchozí varianta byla **učení z lidské ukázky**: zaznamenat vybranou část práce, odvodit proměnné a postup, ověřit ho a později použít. Nejnovější Davidův návrh zdůrazňuje učení z práce provedené samotným agentem; druhý agent doporučil lidskou ukázku zachovat jako doplňkovou cestu.
- **Bakaláři a docházka jsou pouze ilustrace**, nikoli vybraný zákazník, integrace ani oprávnění provádět skutečné zápisy. Totéž platí pro příklady budíku a projektového boardu.
- Časy **40 → 15 sekund**, případně **40 → 5–10 sekund**, jsou ilustrační očekávání nebo Davidův popis Petrova příkladu, nikoli naše naměřené výsledky. Rychlost je nutné porovnávat při stejném výchozím stavu; důležitá je také správnost a počet zásahů člověka.
- Je třeba rozlišovat aktuální mapu obrazovky, zapamatovaný postup a otestovanou vykonatelnou schopnost. Druhý agent navrhl průběžné poznávání potřebných částí místo předběžného mapování celé aplikace a pro první ověření prohlížeč. Jde o návrhy asistenta, ne Davidem schválené technické rozhodnutí.
- David chce **kritické posouzení a vlastní přínos**, nikoli přidání chatu a hezkého rozhraní k běžnému recorderu. Konkrétní uživatel, hodnotný opakovaný úkol a odlišení zůstávají otevřené.
- V druhém chatu byly probírány Miguel, AgentFactory, MUSE, Hermes, Record-and-Run, OpenAdapt a webové workflow systémy. AgentFactory byl navržen jako praktická reference. **Žádný základ nebyl vybraný**; zjištění druhého agenta nejsou v této synchronizaci znovu nezávisle ověřována.
- Inspirace principem Petrova řešení **neobnovuje spolupráci ani přístup k jeho kódu**. Nový projekt zůstává sólo a platforma nebyla schválená.

Pro Frankenstein stále nestačí rychlejší opakování stejného úkolu. Nutné jsou testy před registrací, vlastní rozvoj discovery/správy a **jiný úkol v čisté session kombinující dříve vytvořené schopnosti**, při nezměněných oprávněních.

**Sdílení podkladů při kontrole:** oba chaty používají stejnou lokální složku a druhý agent již četl [zdejší rešerši](self-extending-agents-research-2026-10-08.md). GitHub HEAD byl ověřen jako `2a0b3b61ee50bd12156d9f5d141af2bc17648736` (starší dokumentace Stitche); novější rešerše a změny směru jsou zatím lokální, necommitnuté. V rámci této synchronizace nebyla odeslána zpráva do druhého chatu ani proveden push.

## Co v tomto zadání znamená učení

Agent z konkrétního úkolu zjistí mezeru, vytvoří chybějící schopnost, otestuje ji, zaregistruje a úkol dokončí. V nové session pak jiný úkol kombinuje dříve vytvořené schopnosti. Navíc sám vytváří nebo rozšiřuje nástroje pro jejich vyhledávání a správu. Schopnost může být kód, MCP server nebo promptový skill s explicitním rozhraním, oprávněními a spustitelnými testy.

Není povinné vytvářet dalšího agenta. Požadavek se týká rozšiřování vlastních schopností; fine-tuning vah je výslovně mimo zadání. Pouhé přidání agentů či delegování na hotové role nestačí.

| Co přibylo | Co to dokládá | Co ještě chybí pro celé zadání |
| --- | --- | --- |
| Poznámka o uživateli nebo historii | Trvalou informaci | Novou schopnost a její testy |
| Nahrávka klikání | Záznam konkrétního průchodu | Zobecnění, podmínky použití, ověření a skládání |
| Skill s parametry a testy | Opakovaně použitelný postup | Použití s dalšími skills v nové session a rozvoj jejich správy |
| Agentem rozvíjená knihovna ověřených skills | Základ požadovaného ekosystému | Funkční uživatelský přínos a důkazy všech částí v demu |

Zkušenost se může ukládat mimo model v souborech, programech a registru. Pozdější chování se změní díky tomu, co agent najde a použije. Jeden úspěšný průchod neprokazuje obecnou schopnost zvládnout libovolnou aplikaci.

## Dva Davidovy směry

### A. Agent zkoumající web a navrhující zlepšení

Uživatel: tvůrce webu nebo produktu, který potřebuje před vydáním zjistit problémy. Výstup: konkrétní zjištění, důkazy, kroky reprodukce a doporučení.

Samotné posouzení screenshotu a report používají již existující schopnosti modelu; není tím doložen Frankenstein. Silnější varianta během úkolu vytvoří chybějící opakovatelné kontroly nebo postupy a na další verzi/jiném webu je sám zkombinuje. Agent může kontrolovat například funkční chování formuláře nebo dostupnost akce na mobilu. Technická pozorování je nutné odlišit od subjektivních návrhů a hypotéz o lidech.

Agentovo procházení webu není měření chování skutečných uživatelů. Tvrzení o nepochopení, frustraci, konverzi či obchodním dopadu vyžadují další doklady. Pokud „screening“ znamená záznam skutečného člověka, z jednoho záznamu lze popsat pozorované chování, ale ne automaticky vysvětlit jeho motiv ani zobecnit výsledek.

### B. Agent učící se z práce s člověkem

Uživatel: člověk, který s agentem opakovaně řeší podobné postupy, učí jej místní pravidla a opravuje stejné chyby. Produktová hypotéza: uživatel nemusí pokaždé znovu předávat postup, protože agent z dokončené práce vytváří testovatelné a znovu použitelné schopnosti. Tato konkrétní hypotéza zatím nebyla ověřena u cílových zákazníků.

Interakce: uživatel zadá skutečný výsledek, agent se při práci zorientuje a při potřebě dostane ukázku či vysvětlení. Z průchodu a oprav sám odvodí vhodné schopnosti, zobecní konkrétní hodnoty na parametry a ověří použití. Uživatel nemusí zadat „vytvoř skill X“. Lidská ukázka nesmí suplovat agentovu detekci mezery, tvorbu a testování.

Z pouhého klikání často není jasný důvod ani správný výsledek. V prvním prototypu proto použít krátkou cílenou ukázku s vysvětlením nebo společné řešení úkolu. Trvalé sledování celého počítače není potřebné k prokázání principu. Zaznamenávaný rozsah a dostupné akce mají být explicitní, oprávnění se učením nemění.

## Doporučení k diskusi: osobní pracovní agent, první oblast weby

Širší záměr: **agent, který ze společně provedené práce vytváří vlastní ověřené skills a v dalších úkolech je skládá.** První demonstrační oblast může být kontrola webů, protože Davidovi dává smysl. Toto spojení obou nápadů je doporučení asistenta, nikoli schválený produkt.

Ilustrační průchod:

1. Zadání: „Prověř tento web před vydáním, hlavně cestu k registraci na mobilu.“ Agent má obecné browser nástroje, ale žádné předem vložené specializované skills vydávané za vlastní výtvor.
2. Během úkolu vznikne potřeba opakovatelné kontroly. Člověk může vysvětlit očekávaný výsledek nebo opravit agentovu interpretaci. Agent sám vytvoří příslušné parametrizované postupy, například pro ověření formuláře a pro kontrolu dostupnosti jeho ovládání při různých šířkách.
3. Spustitelné testy ověří očekávané výsledky na funkčních i rozbitých variantách. Člověkem připravený kontrolní vzorek musí být nezávislý na implementaci schopnosti. Pouhé „agent říká, že test prošel“ není důkaz.
4. Teprve ověřené verze vstoupí do knihovny. Agent vytvoří/rozšíří discovery a správu, například vyhledání podle cíle, typu stránky a vstupů. Pouhá statická nabídka předem napsaná týmem by tento požadavek nenahradila.
5. V nové session dostane jiný úkol, například porovnání funkčnosti původní a upravené registrační cesty. Sám vyhledá a zkombinuje dříve vytvořené kontroly a doloží rozdíly. Test musí ověřit, že jde o skutečně odlišný úkol a že schopnosti nebyly přegenerované.

Tyto příklady nejsou příkazem vnutit agentovi předem konkrétní názvy nástrojů. Přesné hranice schopností a druhý úkol je třeba vybrat tak, aby jejich tvorba přirozeně vyplynula z práce. Jinou první oblastí stejného produktu může být rešerše nebo práce s interní aplikací; pro noc je vhodné zvolit jedinou ověřitelnou oblast.

## Co ukázat a jak rozlišit kvalitu

- Prázdný či pravdivě popsaný výchozí registr, vznik nových artefaktů, viditelné testy a registrace až po úspěchu.
- Původ zkušenosti: která část úkolu nebo oprava vedla ke které schopnosti. Neodvozovat obecný zákon z jedné preference bez vymezení kontextu.
- Druhý úkol s vyčištěným konverzačním kontextem: použité verze, kombinace a správný výsledek.
- Měřit především správnost a ruční zásahy; čas a modelová volání jsou doplňující metriky. Nižší čas sám nevysvětluje příčinu zlepšení.
- Sandbox pro generovaný kód, neměnná oprávnění a limity iterací/útraty v kódu jsou povinné. Verze a možnost vrácení změny pomáhají ovládání uživatelem.

## Konkurence a existující podklady

[OpenAdapt](https://openadapt.ai/how-it-works) přímo popisuje převod ukázaného GUI workflow do programu a ověřování výsledku. Myšlenka „ukaž práci a agent se ji naučí“ tedy sama není nová. Produktové tvrzení dodavatele není naše nezávislé měření. Vlastní přínos musíme vymezit konkrétně, například způsobem práce s opravami, transparentností vzniklých skills a jejich skládáním; nebylo ověřeno, že konkurence tyto vlastnosti postrádá.

V rámci existujícího workflow `find-skills` byl zkontrolován katalog [skills.sh](https://www.skills.sh/), který již obsahuje obecné webové review skills. Není důvod zaměňovat instalaci takového hotového skillu za novou schopnost vytvořenou naším produktem. Nebyla doporučená ani provedena instalace třetí strany. Existující lokální skill-creator byl přečten jako referenční materiál ke struktuře skills; nevznikl žádný nový vývojový skill.

## Co váží porota

35 % hodnota a relevance, 25 % originalita, 20 % fungující úplný průchod, 10 % technické provedení a 10 % ověření a přiznané limity. Z toho plyne potřeba spojit širší produktovou myšlenku s konkrétním doloženým přínosem. Není požadováno během jedné noci obsloužit všechny typy práce; není ani předepsán úzký obchodní segment.
