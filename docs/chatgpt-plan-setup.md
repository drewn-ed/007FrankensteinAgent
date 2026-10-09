# Přímé připojení předplatného ChatGPT

Implementováno podle oficiálního Sign in with ChatGPT pro lokální aplikace, dokumentace ověřena 9. 10. 2026. Nejde o reverzní proxy ani kopírování tokenu z Codexu. Samotný API klíč není toto připojení.

## Postup

Aktuální návod pro porotu je v [jury quickstart](jury-quickstart.md#option-b-continue-with-chatgpt-provider-managed-plan-usage). Přístup závisí na způsobilosti konkrétního účtu/workspace a jeho dostupné kvótě, nikoli jen na existenci předplatného. Obecný OpenAI API klíč ani reverse proxy tento adaptér nepodporuje.

1. Nainstalovat závislosti pomocí `uv sync --frozen`. Pro vědomé použití ChatGPT nastavit v lokálním `.env` `SPEND_POLICY=existing_plan`, potom spustit/restartovat `uv run python -m workbench.server`. Výchozí `strict` tuto neoceněnou cestu blokuje; `existing_plan` nemá lokální dolarovou garanci.
2. Otevřít Personal workspace / Settings → **Continue with ChatGPT**.
3. V přihlašovacím okně OpenAI sám potvrdit účet, workspace a oprávnění používat předplatné pro **Wisp**. Přístup ke konverzacím se tímto flow neposkytuje. Pokud nechceš placené čerpání, nepovoluj aplikaci kredity po vyčerpání plánu; zkontroluj její oprávnění v ChatGPT Settings → Usage.
4. Po návratu otevřít Settings, vybrat model z katalogu připojeného účtu a zvolit **Use selected model**. Připojený účet a aktivní poskytovatel jsou samostatné stavy; přihlášení samo model nepřepíná. Aktivní volba je označena **Active model**, opakované přihlášení je označeno **Reconnect account**.
5. Ověřit malý skutečný běh. Přihlášení ani seznam modelů samy nedokládají dostupnou inferenci.

Nové registrace používají název **Wisp**. Dříve připojený účet může v OpenAI dál ukazovat původní název aplikace; přejmenování produktu nemění jeho registraci, tokeny ani oprávnění.

Přihlašovací údaje jsou v `~/.config/007-frankenstein/accounts.json` (0600, adresář 0700), mimo repo. Obsahují oddělené registrace účtů a tokeny; nikdy je neposílat do chatu, GitHubu, veřejných logů ani sandboxu. Ukládání je atomické, refresh rotujících tokenů používá procesový zámek. ID token prochází ověřením podpisu RS256, issuer/audience/expiry a nonce. Callback má jednorázový state a PKCE.

Výběr poskytovatele/modelu se zapisuje do ignorovaného `.env` jako `MODEL_PROVIDER=chatgpt` a `CHATGPT_MODEL=<slug>`. Původní Gemini nastavení zůstává pro ruční návrat. Automatický fallback neexistuje. Změna účtu/modelu je blokovaná během probíhajícího úkolu.

## Přenos a limity

- Přímé `POST https://api.openai.com/v1/responses`, OAuth bearer, `store=false`, `stream=true`; žádný ChatGPT backend endpoint.
- Samostatné modelové kontexty pro plánovače, testy a kód zůstávají zachované. Do požadavku se předává pouze kontext z enginu.
- Úspěch vyžaduje terminální `response.completed` a validní JSON objekt. Neúplný/přerušený stream ani chyba kvóty nejsou úspěch.
- Počet pokusů a délka běhu dál používají společný Budget. Preview tohoto OAuth flow nepodporuje `max_output_tokens`; parametr se neposílá. Místní limit velikosti streamu a timeout nejsou serverový limit účtovaných tokenů. Nastavení `MAX_OUTPUT_TOKENS` se vztahuje k Gemini.
- Tokeny se zaznamenávají ze skutečné usage odpovědi; reasoning není započítané dvakrát. Dolary z předplatného/creditů nejsou odhadované jako automatická nula. Podrobnosti čerpání ověřuje uživatel v ChatGPT Settings → Usage.
- HTTP chyby a terminální streamové chyby se zobrazují bez tokenů či surových odpovědí. Neprobíhá placený API fallback ani nekonečné obnovování přihlášení.
- Omezení první lokální integrace: bez tlačítka lokálního sign-out/revokace; přístup lze odebrat v nastavení ChatGPT. Není to hotová distribuce pro další uživatele ani srovnávací benchmark modelů.

## Ověření

Nové testy `tests/test_chatgpt.py` ověřují neplatný podpis/issuer/audience/expiry/nonce, jednorázový callback, použití vydaného client ID, souhlas s plan usage, soukromé úložiště a opakované přihlášení se stejným host ID. Transportní testy kontrolují terminální událost, účtování tokenů a ukončení při kvótě/limitu. Jde o syntetické testy protokolu; živé ověření vyžaduje souhlas uživatele v OpenAI.

**Živá kontrola 9. 10. 2026 po dokončení přihlášení uživatelem:** model `gpt-6.1-sol` dokončil kontrolní JSON odpověď přes veřejné Responses API (1 požadavek, 60 tokenů, terminální stav `completed`). Před opravou byly zachyceny dvě chyby naší integrace: JSON mode vyžadoval zmínku o JSON také uvnitř `input`; terminální obálka měla prázdné `output`, zatímco text přicházel ve streamu. Adaptér nyní zachovává textové události a přijme je až po `response.completed`. Regresní sada pro toto napojení: 9 testů prošlo. Tato kontrola dokládá připojení a přenos odpovědi, nikoli splnění celého Frankenstein scénáře nebo převahu nad Gemini.

Následně byl model aktivován přes skutečné Settings UI na `127.0.0.1:8767` a ověřen běžným chatem: run `7781afd4c3ec4ed3b1eefaea7580ee31`, `completed`, 1 modelový požadavek, výsledek „ChatGPT connection verified.“ za přibližně 4 sekundy. Tento test žádnou schopnost nevytvářel ani nespouštěl; je pouze kontrolou UI → engine → model → UI. Nastavení ukázalo `Active model: gpt-6.1-sol` a runtime přešel z Gemini na ChatGPT plan.

## Další poskytovatelé — posouzení, ne implementace

Přihlášení k modelu nemá být povinným účtem celého lokálního produktu. Aktuálně engine umí explicitně zvolený Gemini a ChatGPT plan. Pro širší nabídku dává smysl výběr poskytovatele, jeho vlastního přístupu a modelu; přepnutí nemá mazat projekty, registry ani dřívější výsledky. Přenositelnost generovaných schopností mezi modely je třeba samostatně otestovat.

Claude: [Help centrum aktualizované 7. 10.](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan) uvádí používání Agent SDK, `claude -p` a third-party aplikací v rámci předplatného. [Dokumentace Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) současně omezuje nabízení claude.ai přihlášení či limitů ve vlastním produktu bez předchozího schválení. Z těchto rozporných pokynů nevyvozujeme obecné povolení distribuovat subscription login. Jasná cesta pro vlastní produkt je explicitní Claude API připojení s vlastním klíčem a zvoleným účtováním. Adaptér zatím není implementovaný.

Reverzní proxy sama neřeší oprávnění k předplatnému. Přidává instalaci/proces, obnovování přihlášení, převod protokolu a další selhání. Doporučení pro hackathon: dokončit a ověřit stávající provider; případné další připojení řešit samostatným adaptérem, ne přepisem řídicí smyčky produktu. Žádná proxy nebyla nainstalována ani zapnuta.

Zdroje: [registrace a přihlášení](https://developers.openai.com/siwc/token-sharing-open-source/sign-in), [účty a refresh](https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions), [modely a inference](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference), [omezení preview](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).
