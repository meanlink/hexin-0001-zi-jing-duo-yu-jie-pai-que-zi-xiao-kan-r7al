"""Text and font coverage rules shared by proof intake, matching, and sign-off."""
from enum import StrEnum
from unicodedata import category, normalize


class UseKind(StrEnum):
    COMMERCIAL = "commercial"
    PUBLIC = "public"


class LicenseKind(StrEnum):
    OPEN = "open"
    PUBLIC_ONLY = "public_only"


class ProofState(StrEnum):
    DRAFT = "draft"
    LOCKED = "locked"


def normalize_copy(value: str) -> str:
    cleaned = normalize("NFC", value.replace("\r\n", "\n")).strip()
    if not cleaned:
        raise ValueError("稿件必须包含可见字符")
    if any(category(char)[0] in {"C", "M"} and char != "\n" for char in cleaned):
        raise ValueError("请移除控制符、变体选择符或未能组合的附加符号")
    return cleaned


def required_glyphs(value: str) -> list[str]:
    """Whitespace is spacing governed by the layout, not font inventory."""
    return list(dict.fromkeys(char for char in value if not char.isspace()))


def permitted(use_kind: str, license_kind: str) -> bool:
    return use_kind == UseKind.PUBLIC or license_kind == LicenseKind.OPEN
