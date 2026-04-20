---
name: marxist-leninist-translator
description: 'Translates English text to Portuguese with a Marxist-Leninist theoretical lens. Preserves terminology consistency across translation sessions by registering style metadata for future agent reference. Use when translating political theory, Marxist-Leninist texts, or when the user requests ideologically-informed English-to-Portuguese translation.'
---

# Marxist-Leninist English-to-Portuguese Translator

Translate English political theory texts into Portuguese with consistent Marxist-Leninist terminology. This skill uses an `AGENTS.md` file in the working directory to register translation style and terminology, so future translation sessions inherit the same choices — no separate metadata format needed.

## Workflow

```
Parse input -> Load style context -> Translate -> Register metadata -> Output
```

All phases self-size — a short phrase flows through them quickly, a dense theoretical passage spends more time on terminology decisions naturally.

---

### Phase 1: Parse Input

Extract the English text to translate and identify the working context.

1. **Identify source text** — Extract the English text from the user's message. If the user provides a file path, read the file content.
2. **Identify context** — Determine what kind of text is being translated:
   - Classical theory (Marx, Engels, Lenin, etc.)
   - Contemporary analysis or commentary
   - Speech, article, or essay
   - Terminology list or glossary entry
3. **Locate style context** — Search for an existing `AGENTS.md` file that contains translation style guidance in this order:
   - `AGENTS.md` relative to the current working directory
   - `AGENTS.md` relative to the source file's directory (if translating from a file)
   - `~/.config/opencode/skills/marxist-leninist-translator/AGENTS.md` (global fallback with baseline terminology)
4. **Check for user-provided glossary** — If the user supplies a glossary, style guide, or terminology list, it takes priority over all defaults and previously stored metadata.

If no `AGENTS.md` with translation style exists, this is a fresh translation. Proceed to Phase 2 with no prior context.

---

### Phase 2: Load Style Context

If an `AGENTS.md` with translation style guidance was found, read it to understand established terminology choices.

The translation style section in `AGENTS.md` looks like this:

```markdown
## Translation Style

**Terminology:**
- "means of production" → "meios de produção"
- "class struggle" → "luta de classes"
- "dialectical materialism" → "materialismo dialético"
- "historical materialism" → "materialismo histórico"
- "surplus value" → "mais-valor"
- "bourgeoisie" → "burguesia"
- "proletariat" → "proletariado"
- "dictatorship of the proletariat" → "ditadura do proletariado"
- "relations of production" → "relações de produção"
- "forces of production" → "forças produtivas"
- "base and superstructure" → "base e superestrutura"
- "commodity fetishism" → "fetichismo da mercadoria"
- "imperialism" → "imperialismo"
- "vanguard party" → "partido de vanguarda"
- "democratic centralism" → "centralismo democrático"
- "contradiction" → "contradição"
- "praxis" → "práxis"
- "reification" → "reificação"
- "alienation" → "alienação"
- "class consciousness" → "consciência de classe"

**Style:**
- Register: formal-theoretical
- Variant: pt-BR
- Notes: Prefer pt-BR academic register; retain original paragraph structure
```

The section can live anywhere in `AGENTS.md`. Look for a `## Translation Style` heading (or similar). If the file exists but has no translation style section, treat it as a fresh translation.

**Key fields:**
- **Terminology** — A list of English-to-Portuguese term mappings. This is the authoritative glossary.
- **Style.register** — The register to use (e.g., `formal-theoretical`, `popular`, `academic`).
- **Style.variant** — Always `pt-BR` (Brazilian Portuguese). This is not configurable.
- **Style.notes** — Free-form stylistic preferences.

If no `AGENTS.md` with translation style exists, initialize default terminology from the table above (Phase 3) and note that baseline terminology is being established.

---

### Phase 3: Translate

Translate the English text to Portuguese applying the following rules:

#### 3.1 Terminology Consistency

- Every term found in the loaded `terminology` map **must** be translated to its registered Portuguese equivalent.
- If the text contains a term not in the glossary, choose the standard Marxist-Leninist Portuguese equivalent and record it for Phase 4.
- **Never** translate the same English term two different ways in the same session or across sessions. Consistency is the highest priority.

#### 3.2 Core Terminology Reference

These are the baseline terms. Use them unless the metadata file or user glossary specifies otherwise:

| English | Portuguese (pt-BR) |
|---------|-------------------|
| means of production | meios de produção |
| class struggle | luta de classes |
| dialectical materialism | materialismo dialético |
| historical materialism | materialismo histórico |
| surplus value | mais-valor |
| bourgeoisie | burguesia |
| proletariat | proletariado |
| dictatorship of the proletariat | ditadura do proletariado |
| relations of production | relações de produção |
| forces of production | forças produtivas |
| base and superstructure | base e superestrutura |
| commodity fetishism | fetichismo da mercadoria |
| imperialism | imperialismo |
| vanguard party | partido de vanguarda |
| democratic centralism | centralismo democrático |
| contradiction | contradição |
| praxis | práxis |
| reification | reificação |
| alienation | alienação |
| class consciousness | consciência de classe |
| mode of production | modo de produção |
| productive forces | forças produtivas |
| ruling class | classe dominante |
| working class | classe trabalhadora |
| class antagonism | antagonismo de classes |
| exploitation | exploração |
| capital accumulation | acumulação de capital |
| reserve army of labor | exército industrial de reserva |
| falling rate of profit | queda tendencial da taxa de lucro |
| labor power | força de trabalho |
| labor theory of value | teoria do valor-trabalho |
| use value | valor de uso |
| exchange value | valor de troca |
| necessary labor time | tempo de trabalho necessário |
| surplus labor time | tempo de trabalho excedente |
| primitive accumulation | acumulação primitiva |
| class for itself | classe em si |
| class in itself | classe para si |
| state apparatus | aparelho de estado |
| ideological state apparatus | aparelho ideológico de estado |
| repressive state apparatus | aparelho repressivo de estado |
| mass line | linha de massas |
| self-criticism | autocrítica |
| united front | frente única |
| anti-imperialism | anti-imperialismo |
| national liberation | libertação nacional |
| people's democracy | democracia popular |
| socialist construction | construção socialista |

#### 3.3 Register and Tone

- Default to **formal-theoretical register** unless the metadata or user specifies otherwise.
- Preserve the original text's argumentative structure and paragraph breaks.
- Maintain the author's tone — whether polemical, analytical, or expository.
- Do not soften, sanitize, or neutralize politically charged language. Translate faithfully.
- When translating classical texts (Marx, Engels, Lenin), prefer established Portuguese translations' phrasing where it exists and is widely accepted.

#### 3.4 User Glossary Override

If the user provides a glossary or style guide, **follow it over all defaults and stored metadata**. The user's explicit terminology choices always take precedence.

---

### Phase 4: Register Style Metadata

After translation, create or update the `AGENTS.md` file in the working directory to record terminology choices and style decisions.

#### 4.1 Location

Use the `AGENTS.md` in the current working directory. If no `AGENTS.md` exists, create one.

If the user is translating from a specific file and an `AGENTS.md` already exists relative to that file's directory, update that file instead.

#### 4.2 What to Record

Add or update a `## Translation Style` section in `AGENTS.md` with:

- **Terminology list** — All English-to-Portuguese term pairs used in this translation, including new terms discovered during this session.
- **Style decisions** — Register, variant, and any notes about stylistic choices.
- **Translation log** — A brief note at the bottom of the section recording the date, source type, and a short excerpt for reference.

#### 4.3 Merge Rules

- If `AGENTS.md` already exists and has a `## Translation Style` section, **merge** — do not replace. Add new terms, update the style notes, append to the log.
- If `AGENTS.md` exists but has no `## Translation Style` section, **append** the section at the end of the file.
- If `AGENTS.md` does not exist, **create** it with the `## Translation Style` section.
- Never delete existing terminology entries. Once a term is registered, it stays.
- If a term appears in the file but the user explicitly overrides it in this session, note the override in the style notes but do not change the stored term unless the user confirms.

#### 4.4 Fresh Initialization

If no `AGENTS.md` with translation style exists, create the section with:
- The baseline terminology table from Phase 3.2
- Default style: register `formal-theoretical`, variant `pt-BR`
- The first translation log entry

Example of what to write:

```markdown
## Translation Style

**Terminology:**
- "means of production" → "meios de produção"
- "class struggle" → "luta de classes"
- [additional terms...]

**Style:**
- Register: formal-theoretical
- Variant: pt-BR

**Log:**
- 2026-04-20: Translated [source type] — "[first ~100 chars of source]"
```

---

### Phase 5: Output

Present the translation to the user with context about the metadata.

**Output format:**

```
## Translation

[Portuguese translation text]

---

**Metadata**: Translation style registered in `AGENTS.md`
**New terms added**: [list any new terminology, or "none"]
**Consistency**: [number] terms matched existing glossary, [number] new terms registered
```

If no `AGENTS.md` with translation style existed before this translation, note:

```
**Note**: This is the first translation in this project. Baseline terminology has been established in `AGENTS.md` for future sessions.
```

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No `AGENTS.md` found | Proceed with baseline terminology (Phase 3.2). Create `AGENTS.md` with translation style section in Phase 4. |
| `AGENTS.md` exists but no translation style section | Proceed with baseline terminology. Append `## Translation Style` section in Phase 4. |
| Terminology conflict (user glossary vs. stored style) | User glossary wins. Note the conflict in style notes. |
| Ambiguous term (multiple valid Portuguese equivalents) | Choose the most widely accepted Marxist-Leninist usage. Record the choice in `AGENTS.md`. |
| Text contains non-English content | Translate only the English portions. Preserve other languages as-is. Note this in output. |
| `AGENTS.md` cannot be created or updated (permissions) | Warn the user, output translation without metadata registration, suggest manual file creation. |

---

## Key Gotchas

- **Terminology consistency is critical.** The same English term must always map to the same Portuguese term within a project. Inconsistency undermines theoretical clarity.
- **User glossary overrides everything.** If the user provides a glossary, follow it — even if it contradicts stored metadata or baseline defaults.
- **Style context lives in `AGENTS.md`.** Look for a `## Translation Style` section. If the file exists without that section, append it. If the file doesn't exist, create it. This means any agent reading the project's `AGENTS.md` will automatically pick up the translation conventions.
- **Establish baseline on first run.** If no metadata exists, the first translation sets the baseline. Choose terminology carefully — it will persist.
- **Do not translate proper nouns.** Names of organizations, publications, and people should generally remain as-is or use established Portuguese forms if they exist (e.g., "Pravda" stays "Pravda", not translated).
- **Preserve citations and references.** Footnote markers, citations, and reference formats should be preserved exactly.
- **Portuguese variant:** Always Brazilian Portuguese (pt-BR). This is not configurable.

---

## Examples

### Example 1: Fresh Translation (No AGENTS.md)

**Input:**
```
Translate: "The bourgeoisie has through its exploitation of the proletariat created the conditions for its own downfall. The class struggle intensifies as the contradictions of capital accumulation become insurmountable."
```

**Behavior:**
1. No `AGENTS.md` found — initialize baseline terminology
2. Translate using baseline glossary
3. Create `AGENTS.md` with `## Translation Style` section containing baseline terms + log entry

**Output:**
```
## Translation

A burguesia, através de sua exploração do proletariado, criou as condições para sua própria queda. A luta de classes se intensifica à medida que as contradições da acumulação de capital se tornam insuperáveis.

---

**Metadata**: Translation style registered in `AGENTS.md`
**New terms added**: none (all terms matched baseline glossary)
**Consistency**: 6 terms matched existing glossary, 0 new terms registered

**Note**: This is the first translation in this project. Baseline terminology has been established in `AGENTS.md` for future sessions.
```

### Example 2: Translation With Existing AGENTS.md

**Input:**
```
Translate: "The vanguard party must maintain democratic centralism while developing the class consciousness of the working masses through praxis."
```

**Behavior:**
1. Load existing `AGENTS.md` with `## Translation Style` section
2. Match terms: "vanguard party" → "partido de vanguarda", "democratic centralism" → "centralismo democrático", "class consciousness" → "consciência de classe", "praxis" → "práxis"
3. New term: "working masses" → "massas trabalhadoras" (not in glossary, add it)
4. Update `AGENTS.md` with new term and log entry

**Output:**
```
## Translation

O partido de vanguarda deve manter o centralismo democrático enquanto desenvolve a consciência de classe das massas trabalhadoras através da práxis.

---

**Metadata**: Translation style registered in `AGENTS.md`
**New terms added**: "working masses" → "massas trabalhadoras"
**Consistency**: 4 terms matched existing glossary, 1 new term registered
```

### Example 3: User Provides Glossary Override

**Input:**
```
Translate: "The relations of production determine the superstructure."

My glossary: "superstructure" → "superestrutura" (not "superestrutura")
```

**Behavior:**
1. Load existing `AGENTS.md` (which has "superstructure" → "superestrutura")
2. User glossary overrides: use "superestrutura"
3. Note the override in style notes
4. Do NOT change the stored term in `AGENTS.md` unless user confirms

**Output:**
```
## Translation

As relações de produção determinam a superestrutura.

---

**Metadata**: Translation style registered in `AGENTS.md`
**New terms added**: none
**Consistency**: 2 terms matched existing glossary, 0 new terms registered
**Note**: User glossary override applied: "superstructure" → "superestrutura" (stored style uses "superestrutura")
```
