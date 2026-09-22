"""Helpers to map dataset folder names to human-readable class labels."""

from __future__ import annotations


def display_name(folder_name: str) -> str:
    """'Tomato___Early_blight' -> 'Tomato Early Blight'."""
    plant, _, disease = folder_name.partition("___")
    words = disease.replace("_", " ").strip().split()
    pretty = " ".join(w.capitalize() for w in words)
    return f"{plant} {pretty}".strip()


def split_label(label: str) -> tuple[str, str, bool]:
    """'Tomato Early Blight' -> ('Tomato', 'Early Blight', False)."""
    parts = label.split(" ", 1)
    plant = parts[0]
    rest = parts[1] if len(parts) > 1 else "Unknown"
    is_healthy = "healthy" in rest.lower()
    return plant, rest, is_healthy
