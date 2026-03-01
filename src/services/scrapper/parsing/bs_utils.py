from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import Tag

# log = logging.getLogger(__name__)


def get_tag(tag: Tag | None, tag_name: str, class_: str | None = None) -> Tag:
    """Find and return a tag by name and optional class.

    Args:
        tag: Parent tag to search in.
        tag_name: Name of the tag to find.
        class_: Optional class attribute to filter by.

    Returns:
        Found tag.

    Raises:
        ValueError: If parent tag is None or tag not found.
    """
    if not tag:
        raise ValueError("No tag found")

    new_tag: Tag | None = (
        tag.find(
            tag_name,
            class_=class_,
        )
        if class_
        else tag.find(tag_name)
    )

    if not new_tag:
        raise ValueError(f"No {tag_name} tag found")

    return new_tag


def get_text(tag: Tag) -> str:
    """Extract and strip text content from a tag.

    Args:
        tag: Tag to extract text from.

    Returns:
        Stripped text content.
    """
    return tag.text.strip()


def get_href_attr(tag: Tag, attr: str) -> str:
    """Extract and strip attribute value from a tag.

    Args:
        tag: Tag to extract attribute from.
        attr: Attribute name.

    Returns:
        Stripped attribute value.

    Raises:
        ValueError: If attribute not found.
    """
    if not tag.has_attr(attr):
        raise ValueError(f"No found attribute: {attr} into tag: {tag}")

    return str(tag["href"]).strip()


__all__ = (
    "get_href_attr",
    "get_tag",
    "get_text",
)
