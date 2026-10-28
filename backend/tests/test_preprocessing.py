from ml.preprocessing import clean_text, split_into_sentences, compute_text_metrics

def test_clean_text_removes_zero_width_and_normalizes_spaces():
    dirty = "Hello\u200B world!  \t This   is\r\na test.\uFEFF"
    cleaned = clean_text(dirty)
    assert "\u200B" not in cleaned
    assert "\uFEFF" not in cleaned
    assert "  " not in cleaned
    assert "Hello world!" in cleaned

def test_split_into_sentences_preserves_abbreviations():
    text = "Dr. Smith met with Prof. Jones at 10 a.m. They discussed natural language processing. The results were conclusive."
    sentences = split_into_sentences(text)
    assert len(sentences) >= 2
    # Ensure "Dr. Smith" wasn't sliced in half
    assert any("Dr. Smith" in s for s in sentences)

def test_compute_text_metrics():
    text = "The quick brown fox jumps over the lazy dog."
    words, chars = compute_text_metrics(text)
    assert words == 9
    assert chars == len(text)
