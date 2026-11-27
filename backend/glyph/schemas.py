from pydantic import BaseModel, Field, field_validator

from glyph.models import LicenseKind, UseKind, normalize_copy, required_glyphs


class ProofForm(BaseModel):
    code: str = Field(pattern=r"^[A-Z][A-Z0-9-]{1,19}$")
    location: str = Field(min_length=2, max_length=100)
    copy_text: str = Field(min_length=1, max_length=240)
    use_kind: UseKind

    @field_validator("copy_text")
    @classmethod
    def cleaned_copy(cls, value):
        return normalize_copy(value)


class ProofRevision(BaseModel):
    copy_text: str = Field(min_length=1, max_length=240)
    revision: int = Field(ge=1)

    @field_validator("copy_text")
    @classmethod
    def cleaned_copy(cls, value):
        return normalize_copy(value)


class TypefaceForm(BaseModel):
    code: str = Field(pattern=r"^[A-Z][A-Z0-9-]{1,19}$")
    family: str = Field(min_length=2, max_length=100)
    license_kind: LicenseKind
    coverage: str = Field(min_length=1, max_length=8000)
    specimen: str = Field(min_length=2, max_length=3000)
    font_file: str = Field(max_length=100, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]*\.(otf|ttf|ttc)$")

    @field_validator("coverage")
    @classmethod
    def unique_visible_chars(cls, value):
        return "".join(required_glyphs(normalize_copy(value)))

    @field_validator("specimen")
    @classmethod
    def cleaned_specimen(cls, value):
        return normalize_copy(value)


class AssignmentForm(BaseModel):
    glyph: str = Field(min_length=1, max_length=1)
    revision: int = Field(ge=1)
    face_code: str = Field(pattern=r"^[A-Z][A-Z0-9-]{1,19}$")


class ReviewVersion(BaseModel):
    revision: int = Field(ge=1)
