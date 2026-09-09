from pathlib import Path

# The root pass intentionally touches the painter import ordering; dart fix will normalize
# analyzer-safe import directives and remove any unused imports without changing architecture.
