# GitHub Discord BOT - AI Agent Guidelines

Dit project maakt integraal onderdeel uit van de Workbench 001 workspace en erft alle bindende richtlijnen van het centrale hoofd-instructiedocument:
👉 **[Centrale AGENTS.md](file:///g:/My%20Drive/Workbench%20001/AGENTS.md)**

Lees tevens altijd eerst [.agent/memory.md](file:///g:/My%20Drive/Workbench%20001/.agent/memory.md) vóór analyse of modificatie (Regel 1 van AGENTS.md).

---

## 1. Project Context & Backlog Directory

- **Project:** `githubDiscordBOT` (Standalone Discord bot service)
- **Backlog Map:** `plugins/githubDiscordBOT/backlog/`
- **Directory Context (CRITICAL):** Alle `backlog` CLI commando's en MCP interacties **MOETEN** worden uitgevoerd met de werkmap ingesteld op `plugins/githubDiscordBOT` (bijv. `cd plugins/githubDiscordBOT` of via de `Cwd` parameter in toolcalls), zodat taken correct in de backlog van de bot worden geplaatst en beheerd.

---

## 2. Bindende Centrale Regels (Inherited from Master AGENTS.md)

Alle standaarden uit de centrale [AGENTS.md](file:///g:/My%20Drive/Workbench%20001/AGENTS.md) zijn hier onverkort van toepassing:

- **Taakbeheer via Backlog.md:** Eerst taak registreren/WIP zetten in `backlog-md` vóór het schrijven of wijzigen van code. Afronden pas na testen, linting en type-checks.
- **Tooling & Omgeving:** `uv` voor package management, `Ruff` voor code formatting/linting, `pytest` voor testen.
- **Security:** Sla nooit Discord tokens of GitHub secrets op in code of docker files. Gebruik environment variables en `.env`.
- **Pre-Commit Verificatie:** Update `README.md` vóór taakafronding. Nooit automatische releases of tags.
