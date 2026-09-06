# Interface vocabulary for test placement

This standalone reference applies the module vocabulary used by improve-architecture to a different task: placing meaningful tests. Reading it does not start an architecture review.

- **Module:** a unit with interface and implementation, at function, class, package or cross-layer scale.
- **Interface:** everything callers must know, including types, invariants, ordering, failures, configuration and material performance constraints.
- **Depth:** how much useful behavior a small interface hides; a shallow wrapper may expose as much complexity as its implementation.
- **Seam:** a place where behavior can vary without editing that location. Tests observe the appropriate public interface; not every private helper needs its own seam.
- **Adapter:** translates between interfaces at a real varying boundary; do not invent one only to satisfy a test.
- **Leverage:** one implementation supports many callers and tests.
- **Locality:** changes and validation stay concentrated in the responsible module.

Use project domain names and existing ADRs. For a bug, choose a test that fails on the reported behavior and passes after the fix, using an independent expected outcome.
