# Interface vocabulary

For interface design, read [codebase-design](../../codebase-design/SKILL.md), the shared source for module, interface, depth, seam and adapter definitions. This is a design reference, not permission to start an architecture review. If unavailable, retain the current public interface and test observable behavior; report the missing design reference only when an unresolved design choice depends on it.

Use project domain names and existing ADRs. For a bug, choose a test that fails on the reported behavior and passes after the fix, using an independent expected outcome.
