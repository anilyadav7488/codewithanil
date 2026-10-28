import re
from typing import List, Tuple

ZERO_WIDTH_CHARS_PATTERN = re.compile(r'[\u200B-\u200D\uFEFF\u00A0]')
MULTIPLE_SPACES_PATTERN = re.compile(r'[ \t]+')
NEWLINES_PATTERN = re.compile(r'\r\n|\r')

COMMON_ABBREVIATIONS = [
    "Dr.", "Prof.", "Mr.", "Mrs.", "Ms.", "e.g.", "i.e.", "vs.", "a.m.", "p.m.", "etc."
]

def clean_text(raw_text: str) -> str:
    """
    Cleans raw user input by stripping zero-width tokens,
    normalizing line breaks, and eliminating extraneous whitespace.
    """
    if not raw_text:
        return ""
    
    # Normalize line breaks
    text = NEWLINES_PATTERN.sub('\n', raw_text)
    # Remove hidden zero-width unicode
    text = ZERO_WIDTH_CHARS_PATTERN.sub(' ', text)
    # Clean excessive whitespace inside lines
    lines = [MULTIPLE_SPACES_PATTERN.sub(' ', line).strip() for line in text.split('\n')]
    cleaned = '\n'.join([line for line in lines if line])
    return cleaned.strip()

def split_into_sentences(text: str) -> List[str]:
    """
    Splits cleaned text into discrete sentences while respecting common abbreviations.
    """
    if not text:
        return []
    
    # Protect common abbreviations so period does not trigger a false split
    protected = text
    for abbrev in COMMON_ABBREVIATIONS:
        placeholder = abbrev.replace(".", "@DOT@")
        # Match case-insensitively with boundary
        pattern = re.compile(r'\b' + re.escape(abbrev), re.IGNORECASE)
        protected = pattern.sub(placeholder, protected)

    raw_sentences = re.split(r'(?<=[.!?])\s+', protected.strip())
    
    refined: List[str] = []
    for s in raw_sentences:
        s_clean = s.replace("@DOT@", ".").strip()
        if s_clean:
            refined.append(s_clean)
            
    return refined

def compute_text_metrics(text: str) -> Tuple[int, int]:
    """
    Returns (word_count, character_count).
    """
    words = [w for w in text.strip().split() if w]
    return len(words), len(text)
