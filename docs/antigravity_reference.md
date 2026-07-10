# Antigravity 2.0 Base de Operaciones (C5-REAL)

## Getting Started
- **Download**: Antigravity 2.0 requires macOS 12+ (X86 not supported), Windows 10 (64-bit), or Linux (glibc >= 2.28, glibcxx >= 3.4.25).
- **Projects**: Agents work within Projects, which define boundaries of folders/repos. Add folders to provide cross-repository context.
- **Starting an Agent**: Type goal/instruction and press Enter. Choose Mode:
  - **Local Mode**: Operates directly in active folders.
  - **New Worktree Mode**: Operates in an isolated Git worktree.
- **Basic Navigation**:
  - Open Conversation Picker: `⌘K` / `Ctrl+K`
  - Open File Search: `⌘P` / `Ctrl+P`
  - Focus Input: `⌘L` / `Ctrl+L`
  - New Conversation: `⌘N` / `Ctrl+N`
  - Next/Prev Conversation: `⌥ Up/Down`
- **Slash Commands**:
  - `/goal`: Run until task is completely finished without asking for intermediate input.
  - `/grill-me`: Ask questions to align on specific details before implementing.
  - `/schedule`: Run instruction as one-time timer or recurring schedule.
  - `/browser`: Explicitly allow agent to use browser primitives (requires Chrome + remote debugging).

## Skills (Agent Capabilities)
- **Concept**: Skills are reusable packages of knowledge (open standard) that extend agent capabilities via progressive disclosure.
- **Locations**:
  - `workspace-root/.agents/skills/<skill-folder>/` (Workspace-specific)
  - `~/.gemini/config/skills/<skill-folder>/` (Global/All workspaces)
- **Creation & Structure**:
  - Requires a `SKILL.md` file with YAML frontmatter (`name` and `description`).
  - Optional directories: `scripts/` (helper tools), `examples/` (reference implementations), `resources/` (templates).
- **Progressive Disclosure Pipeline**:
  - **Discovery**: Agent reads list of available skills (names & descriptions).
  - **Activation**: If description is relevant, agent ingests the full `SKILL.md`.
  - **Execution**: Agent executes according to the detailed instructions.
- **Best Practices**:
  - *Keep skills focused*: Do one thing well; avoid "do everything" skills.
  - *Write clear descriptions*: Write in 3rd person with keyword triggers.
  - *Use scripts as black boxes*: Rely on `--help` before reading full source.
  - *Include decision trees*: Add logic for complex execution paths.
