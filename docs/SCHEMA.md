# LM Wiki Schema

This document defines the structure and workflows for the Arkhe(n) Knowledge Base.

## 🏗️ Structure

- `docs/sources/`: Raw, immutable source files (PDFs, Markdown clips, data).
- `docs/wiki/`: LLM-maintained markdown files.
    - `concepts/`: High-level theoretical and philosophical frameworks.
    - `systems/`: Technical architecture and component specifications.
    - `protocols/`: Operational procedures and standard workflows.
    - `entities/`: Information on specific people, organizations, or hardware components.
- `docs/index.md`: Catalog of all wiki pages.
- `docs/log.md`: Chronological log of wiki operations.

## 🔄 Workflows

### Ingest
When a new source is added to `docs/sources/`:
1. **Analyze**: Read the source and extract key entities, concepts, and claims.
2. **Synthesize**: Identify how this information connects to existing wiki pages.
3. **Update**:
    - Create/update a summary page in `docs/wiki/sources/` (if applicable).
    - Update relevant concept/system/protocol pages with new data or citations.
    - Flag contradictions or superseding information.
4. **Index**: Update `docs/index.md` if new pages were created.
5. **Log**: Append a record to `docs/log.md`.

### Query
When asked a complex question:
1. **Search**: Consult `docs/index.md` and use `grep` or search tools to find relevant wiki pages.
2. **Read**: Load and synthesize information from multiple pages.
3. **Answer**: Provide a comprehensive answer with citations to specific wiki pages or sources.
4. **Commit**: If the answer is particularly valuable (e.g., a new analysis), file it back as a new page in the wiki.

### Lint
Periodically health-check the wiki:
- Check for broken cross-references.
- Identify "orphan" pages with no inbound links.
- Find contradictory claims between older and newer pages.
- Suggest "gap-fill" research for missing definitions.

## 📝 Conventions
- Use Obsidian-style internal links: `[[page_name|Alias]]`.
- Add YAML frontmatter to all wiki pages (tags, date, source_count).
- Citations should point back to files in `docs/sources/` or other wiki pages.
