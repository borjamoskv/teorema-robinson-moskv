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
