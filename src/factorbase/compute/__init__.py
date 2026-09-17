"""Reference implementations, one module per family.

Each public function here is named in the `implementation` field of a catalogue
entry, in the form `factorbase.compute.<module>:<function>`. The wiring check
in `scripts/check_catalog_wired.py` walks the catalogue and confirms that every
name resolves, so an entry cannot quietly point at a function nobody wrote.
"""

from __future__ import annotations
