from __future__ import annotations

from pathlib import Path

package_root = Path(__file__).resolve().parent
src_package = package_root.parent / "src" / "scribe_web"
if src_package.exists():
    __path__.append(str(src_package))
