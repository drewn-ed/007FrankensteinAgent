# Produktový návrh pracovního prostředí s učenlivým asistentem

**9. 10. 2026.** David potvrzuje, že se chce vydat směrem agenta, který se učí práci v aplikacích, a žádá ucelený produkt, užitečné navazující funkce a kritické posouzení škálovatelnosti. YouTube, Meta Ads a DaVinci jsou příklady, nikoli vybrané integrace. Konkrétní stack a demonstrační prostředí nejsou potvrzené. Tento podklad doplňuje technický [handoff](learning-browser-agent-handoff-2026-10-09.md); jeho úzký scénář nesmí být zaměňován za definici celého produktu.

## Produkt a uživatelský přínos

**Pracovní prostředí, ve kterém zadáváte výsledky a asistent si postupně osvojuje vaše aplikace, pravidla a opakovanou práci.** Z úspěšných postupů vznikají ověřitelné schopnosti; relevantní schopnosti se používají a skládají napříč dalšími úkoly. Pokud je potřeba, hlavní agent přidělí dílčí práci specialistovi. Každá přijatá změna zkušenosti má vymezený rozsah a důkaz, nikoli jen nové tvrzení v promptu.

Hlavní produktová hypotéza: čas investovaný do opravy nebo zaučení se uživateli vrací tím, že nemusí stejnou věc vysvětlovat a opravovat znovu. Další hodnota vzniká, když lze ověřený postup vyvolat jednou větou, použít jako část většího úkolu nebo spouštět opakovaně. Počet uložených skills ani počet agentů sám o sobě není přínos.

První skupina uživatelů k ověření: jednotlivci a malé týmy, které pravidelně pracují v několika aplikacích a mají vlastní postupy, šablony a klientská pravidla. Jde o hypotézu segmentu, nikoli výsledek zákaznického výzkumu. Produkt není omezený na zveřejňování videí ani na jeden konkrétní formulář.

## Jak by vypadalo běžné použití

Uživatel otevře projekt s jeho podklady, pravidly a povolenými aplikacemi. Zadá výsledek, například přípravu podkladů pro uvedení produktu. Asistent použije dostupné schopnosti, rozdělí práci na účelné části a průběžně ukazuje výstupy. V místech, kde narazí na novou potřebu, vytvoří a otestuje doplnění schopnosti.

Když uživatel opraví konkrétní chybu, může určit, zda oprava platí jen nyní, pro tento projekt nebo obecně. Uložení preference je jednoduché; změna vykonávaného postupu musí projít testem. Například formát značky nebo povinné sekce lze ověřovat konkrétně, zatímco estetický vkus potřebuje lidské posouzení.

Po dokončení uživatel dostane výsledek a stručný přehled naučeného. Příští úkol z těchto schopností těží. Nabídka „použít znovu“ pracuje s parametry, nabídka „opakovat pravidelně“ mění ověřený postup na rutinu. Automatické spouštění se nastavuje výslovně, nikoli odvozením z jednorázového požadavku.

## Funkce které tvoří celek

| Funkce | Přidaná hodnota pro uživatele | Vztah k učení | Rozsah |
| --- | --- | --- | --- |
| Projekty a kontext | Pravidla, podklady a aplikace jsou pohromadě; různým klientům se nemíchá styl | Určuje, kdy je zkušenost relevantní | MVP v jednoduché podobě |
| Učení z konkrétní opravy | Uživatel neopakuje stejnou korekci | Kandidát pravidla nebo nové verze schopnosti s jasným rozsahem | MVP na jednom ověřitelném typu korekce |
| Knihovna „Co už umím“ | Naučený postup lze najít, spustit s novými vstupy, prohlédnout či deaktivovat | Čitelná podoba trvalých schopností a jejich původu | MVP |
| Skládání schopností a specialisté | Jedno zadání může využít různé dovednosti; uživatel je nemusí ručně propojit | Agent najde a kombinuje dřívější schopnosti | MVP malý počet schopností, jeden doložený případ delegace, pokud se stihne |
| Přehled výsledku a převzetí práce | Uživatel ví, co se změnilo a kde je potřeba pomoc | Oprava má konkrétní pozorovaný podklad | MVP log a výsledek; plné převzetí a obnovení práce později |
| Rutiny z hotové práce | Povedený postup lze zopakovat bez dalšího vysvětlování | Amortizuje cenu zaučení; používá přijaté verze | MVP ruční opakování; plánovač jako další krok |
| Údržba a opravy knihovny | Nehromadí se zaměnitelné nebo rozbité postupy | Vyhledání platných verzí, deaktivace a testované opravy | MVP malé discovery a správa; automatické slučování později |
| Sdílení v týmu | Další člověk může převzít ověřený postup místo dalšího školení | Přenos postupu s ověřením v novém prostředí | Později |

Nejde o požadavek vytvořit osm oddělených produktů. Projekty, zadání a průběh práce jsou hlavní obrazovka. Knihovna a pravidla jsou přehledy nad stejnými uloženými daty. Rutina odkazuje na existující postup. Specialista je vykonavatel vymezeného dílčího úkolu, nemusí mít vlastní oddělený chat a celé nové uživatelské rozhraní.

## Role agentů a co se skutečně zlepšuje

Hlavní agent rozumí zadání a skládá plán. Specialista řeší ohraničenou část s jasnými vstupy a výstupem. Tvůrce schopností z nové potřeby a zkušenosti připraví kandidáta. Nezávislý vykonavatel spustí testy. Správa knihovny uloží přijatou verzi, najde vhodnou schopnost a eviduje její použitelnost. Některé role mohou být oddělená volání stejného modelu; registry a testovací brány mají být běžný kód.

Příklad delegace: jeden specialista zpracuje podklady, druhý připraví návrh výstupu; agent ovládající cílovou aplikaci jej použije až po dokončení závislostí. Nezávislé přípravy mohou běžet souběžně. Více agentů nemá současně klikat v jedné sdílené session. Oprávnění dílčích agentů nepřekročí oprávnění hlavního běhu.

Použití specialisty automaticky nezlepšuje hlavní model. Učení nastane, až když se vhodná zkušenost převede na použitelný artefakt, ověří a později úspěšně použije. V první verzi se nemění váhy modelu. Naučený deterministický krok může později provést obyčejný kód bez dalšího modelového rozhodování; jinde bude i nadále potřeba model.

Užitečná jednotka přenosu je například práce s časovaným přepisem, formátování podkladů podle pravidel nebo ověřená práce s konkrétním typem záznamu. Ovládání YouTube se samo nepřenese do DaVinci. Přenositelné části a části závislé na aplikaci musí být odlišené.

## Jak použít prozkoumané projekty

Následující mapování vychází z primárních dokumentací a dřívější statické kontroly; neznamená ověřenou vzájemnou kompatibilitu ani instalaci. Vybrat jeden runtime a převzít potřebné části nebo principy, nikoli spouštět všechny frameworky nad sebou.

| Zdroj | Konkrétní využití v našem produktu | Co nepřebírat bez úprav |
| --- | --- | --- |
| [AgentFactory](https://github.com/zzatpku/AgentFactory) | Vytváření a uchovávání spustitelných specialistů, jejich volání z hlavního agenta a skládání do dalších úkolů | Dříve kontrolovaná cesta importovala generovaný kód do procesu; vyžaduje naši izolaci a povinnou testovací bránu |
| [MUSE Autoskill](https://arxiv.org/html/2605.27366v2) | Paměť ke konkrétní schopnosti: kde fungovala, jaké měla potíže, jak se má vybrat a upravit | Výzkumný návrh není ověřený hotový plugin. V2 má testy volitelné; naše brána musí vynutit spustitelné testy |
| [AutoSkill](https://github.com/ECNU-ICALK/AutoSkill) | Zachycení trvalých oprav a pravidel, rozhodování zda zkušenost zahodit, sloučit, doplnit nebo vytvořit nový skill | Ne každá interakce má vytvářet nový skill; popsané automatické zápisy samy neplní povinné testování |
| [Hermes skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills), [delegace](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation), [rutiny](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Reference celého produktu, propojení knihovny s delegovanou i opakovanou prací; možný alternativní základ místo AgentFactory | Již existující funkce neprezentovat jako vlastní vynález; zkontrolovat izolaci, tvorbu a testy před rozhodnutím o převzetí runtime |
| [Hermes Curator](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator) | Údržba knihovny, používání versus zastarávání, archivace a návrat předchozích verzí | Slučování může být drahé a škodit; v dokumentaci je volitelné. Do noční verze stačí menší správa |
| [Miguel](https://github.com/soulfir/miguel) | Inspirace viditelným průběhem vývoje schopností a historií práce | Dřívější kontrola nalezla důvody nepřebírat jeho široké úpravy vlastního kódu. Není doporučeným hlavním základem |

AgentFactory je nejbližší reference k požadovanému mechanismu spustitelných specialistů. Hermes je významné srovnání pro celkovou aplikaci a současně konkurent: přidání hezkého rozhraní nad stejný seznam funkcí samo nezaručí zákazníky. U MUSE je zajímavý životní cyklus a paměť; není nutné čekat na jeho kompletní implementaci.

## Co může produkt odlišovat

Pracovní hypotéza odlišení: **uživatel průběžně zaučuje asistenta do své práce a vidí, jak se jeho opravy promítly do dalších výsledků.** Zážitkem je „tohle už nemusím vysvětlovat znovu“, nikoli prohlížení souborů SKILL.md. Učení je ohraničené projektem a aplikací a zlepšení má konkrétní doklad.

Příklad: uživatel opraví strukturu podkladů a rozsah změny nastaví na konkrétní projekt. Při jiném úkolu asistent použije stejné pravidlo, načte potřebné ověřené schopnosti a předá výstup jinému specialistovi. Uživatel vidí výsledek a původ použitého postupu. Toto je navržený zážitek, nikoli tvrzení, že konkurence jednotlivé části neumí.

Kandidátem na pozdější obranu produktu jsou kvalitní postupy ověřené v reálných prostředích, historie vyřešených výjimek a snadné zaučení dalšího člena týmu. Hromadění soukromých dat bez možnosti exportu není žádoucí produktová strategie. Ochota platit a udržitelnost výhody vyžadují zákaznické ověření.

## Škálovatelnost a důvody projekt zastavit

Technicky dává smysl oddělit společný engine od připojení aplikací a jednotlivých naučených postupů. Každá nová aplikace ale přináší vlastní přístup, ovládání, verze a způsob ověření výsledku. API může být vhodnější než UI; na desktopu může být dostupné jiné rozhraní. Nyní netvrdíme funkční podporu Meta Ads ani DaVinci.

Začne-li každé připojení vyžadovat dlouhou ruční práci vývojáře a každá změna UI zásah týmu, hrozí podnikání založené na zakázkovém servisu místo škálovatelného produktu. Druhý problém je ekonomika: tvorba, ověřování, delegování a opravy mohou stát více než ušetřená práce. Třetí je kvalita knihovny: mnoho úzkých či konfliktních skills může zhoršit výběr i spotřebu kontextu.

Proto první verze podporuje omezené browser prostředí, ukládá jen zkušenosti s předpokládaným dalším využitím, načítá jen relevantní schopnosti a má limity výdajů i iterací. Nejde o trvalé omezení produktu na jeden obor. Plánované rozšiřování přidává podporované aplikace a testované varianty, nikoli slib univerzální spolehlivosti.

Ověření produktu má odpovědět na čtyři otázky: dokáže další uživatel začít bez zásahu vývojáře; přenese se oprava na nové vhodné zadání a ne na nevhodné; klesne celkový čas člověka včetně kontrol a oprav; vyplatí se opakované používání po započtení tvorby a údržby. Nejprve testovat na několika diagnostických případech, následně u skutečných uživatelů; malé demo neověřuje tržní poptávku.

## Noční MVP a širší prezentace

Noční produkt může mít ucelené rozhraní i při malém funkčním rozsahu: projekt s pravidly, zadání a živý průběh, knihovnu vzniklých schopností a jeden prokazatelný případ učení a dalšího použití. Ruční opakování je první krok k rutinám. Plánování, týmové sdílení a další aplikace mohou být ukázané jako označený návrh dalšího rozvoje.

Pro Frankenstein musí běžící část doložit: úkol vyvolá rozpoznání mezery; agent vytvoří schopnost, vykoná testy a až potom ji zaregistruje a dokončí úkol; rozšíří i discovery a správu; nový úkol v čisté session zkombinuje dřívější schopnosti; oprávnění se nezmění. Generovaný kód běží v sandboxu a rozpočet i iterace omezuje kód. To jsou požadavky z briefu, nikoli seznam funkcí potřebný v hlavní navigaci produktu.

Prezentace může prodávat širší vizi, ale musí označit rozdíl mezi běžícím MVP a návrhem. Video podle briefu ukazuje běžící produkt; koncept obrazovky není jeho náhrada. Silný pitch může znít: **Your instructions should become experience. Our assistant turns completed work and corrections into tested skills it can reuse on the next job.**

## Doporučení k nejbližšímu rozhodnutí

Zachovat směr pracovního prostředí s učenlivým asistentem. Hlavní přínos stavět na učení z oprav a opakovaném použití, rozvíjet jej projekty, skládáním práce, knihovnou a rutinami. Pro ověření vybrat jeden opakovaný proces z prostředí, které může David skutečně používat; nevybírat obor jen kvůli jednoduchému formuláři.

Další agent má posuzovat tuto celkovou koncepci a její závislosti, ne znovu redukovat produkt na YouTube metadata. Má kriticky určit, které tři části mají nejvyšší užitek a zda už dostupný základ poskytne totéž s menším úsilím. Volba technického runtime ani skutečný zápis do externí aplikace není tímto dokumentem automaticky schválená.
