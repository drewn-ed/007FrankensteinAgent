# Frankenstein — pracovní prototyp učenlivého agenta

**Stav k 9. 10. 2026:** David na projektu pracuje sám. Vedle rešerší zde vzniká lokální prototyp pro track **Frankenstein** hackathonu **Agents 0.0.7 — From Dusk Till Dawn #01**. Základ používá Python, Gemini a Docker. Cílová aplikace, finální název a produktové demo nejsou potvrzené. Příklady nejsou hotové integrace.

## Spuštění prototypu

Požadavky: Python 3.11+, `uv`, běžící Docker. Generovaný kód se nikdy nespouští přímo na hostiteli.

```sh
uv sync
docker pull python:3.12-slim
cp .env.example .env
chmod 600 .env
# Do .env lokálně vlož GEMINI_API_KEY.
# GEMINI_FREE_TIER_CONFIRMED=true nastav pouze po kontrole Free tarifu projektu v AI Studiu.
uv run python -m workbench.server
```

Otevři **http://127.0.0.1:8767**. Nevkládej skutečná citlivá data: obsah zadání a příloh se odesílá Gemini. Klíč zůstává na serveru; nepředává se do UI ani sandboxu. `.env` a `.runtime/` jsou ignorované Gitem.

Každý nový úkol začíná bez historie předchozí konverzace. Udržuje se pouze lokální SQLite registr, verze, testy a záznamy běhů. Funkční vzhled je dočasný; typografii řeší David s jiným agentem.

```sh
# Skutečné kontroly Docker izolace a kritických hranic; vyžadují běžící Docker.
uv run python -m unittest discover -s tests -v

# Skutečný modelový běh nad explicitně syntetickými daty, v odděleném registru.
uv run python -m workbench.cli 'Očisti registrace a vyhodnoť kapacity workshopů.' --input examples/registrations.json --data-dir .runtime/verification
```

Modelový kontext pro testy nevidí implementaci. Neúspěšné testy blokují aktivaci. Oprava porovnává původní verzi s novým případem a zkouší dvě kandidátní opravy proti všem zachovaným testům. Modelové testy stále mohou být chybné; nepředstavují obecnou záruku správnosti. Infrastrukturní testovací fixtures jsou ručně napsané a nejsou vydávané za schopnosti vytvořené agentem.

**Co ještě nelze tvrdit:** produkt neovládá webové/desktopové aplikace, nemá ověřenou zákaznickou poptávku ani měřenou výhodu nad běžným agentem. Agentem vytvořené discovery/správa a skládání několika schopností v nové session vyžadují další implementaci a důkazy. Registr sám tuto podmínku nesplňuje. Není implementované připojení přes předplatné Codexu.

Aktuální pracovní podklady: [plán stavby](docs/build-plan.md), [pět polí k odevzdání](docs/submission-draft.md).

David chce pokračovat směrem asistenta, který plní úkoly v aplikacích, z vlastní práce vytváří otestované opakovaně použitelné schopnosti a kombinuje je při dalších úkolech. Nejnovější [produktový návrh](docs/learning-agent-product-blueprint-2026-10-09.md) popisuje celé pracovní prostředí, navazující funkce, využití existujících projektů a rizika škálování. Technický [handoff](docs/learning-browser-agent-handoff-2026-10-09.md) rozpracovává malý demonstrační průchod. Příklady nejsou vybrané integrace ani ověřené výsledky.

## Podklady pro dalšího agenta

**Pro nezávislé posouzení začni zde: [zadání pro Claude](docs/claude-independent-review-2026-10-09.md).** Obsahuje kontext eventu, pořadí čtení, vývoj úvah, stav důkazů a otázky pro kritický verdikt.

| Dokument | Obsah |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Pravidla práce v repozitáři |
| [Hackathon brief](docs/hackathon-brief.md) | Ověřené soutěžní požadavky, hodnocení, porota a odevzdání |
| [Produktový návrh, 9. 10.](docs/learning-agent-product-blueprint-2026-10-09.md) | Celkový produkt, užitečné funkce, role agentů a frameworků, škálovatelnost a MVP |
| [Learning browser agent — handoff, 9. 10.](docs/learning-browser-agent-handoff-2026-10-09.md) | Konkrétní návrh dema, technické hranice a otevřené otázky |
| [Learning Agent Concepts](docs/learning-agent-concepts.md) | Vývoj úvah o učení z úkolů, workflow a lidských ukázek |
| [Self-extending agents — rešerše](docs/self-extending-agents-research-2026-10-08.md) | Existující řešení, zdroje, limity důkazů a možné odlišení |

## Dřívější průzkumy

Tyto dokumenty zachycují starší úvahy; nejsou aktuálním zadáním ani potvrzeným plánem:

- [Průzkum problémů](docs/problem-research-2026-10-08.md) — počáteční hledání problémů a možných scénářů.
- [Návrh porovnávání dodavatelských nabídek](docs/solo-project-proposal.md) — Davidem odmítnutý návrh.

**Uzávěrka:** 9. října 2026 v **07:14 Europe/Prague**. Odevzdání: veřejné repo a YouTube Unlisted demo do **90 sekund**. Živý pitch má podle Davidova zadání **60 sekund**.

Pravidla byla ověřena v [přihlášeném HQ](https://hq.agents007.ai/topics#frankenstein) dne 8. října 2026. Podrobnosti a rozdíly proti veřejné stránce akce jsou v briefu.
