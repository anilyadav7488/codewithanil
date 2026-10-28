import re
from typing import Dict, List, Any
from app.schemas.prompt import PromptAnalysisResponse, PromptMetrics

VAGUE_TERMS = [
    r"\bsome\b", r"\bstuff\b", r"\bthings\b", r"\bgood\b", r"\bfast\b",
    r"\bquick\b", r"\betc\b", r"\band so on\b", r"\bnice\b", r"\bany\b",
    r"\bsomething\b", r"\bmake it better\b"
]

FORMAT_TERMS = [
    r"\bjson\b", r"\bmarkdown\b", r"\btable\b", r"\bbullet points?\b",
    r"\blist\b", r"\bcsv\b", r"\byaml\b", r"\bformat\b", r"\bschema\b"
]

ROLE_TERMS = [
    r"\byou are\b", r"\bact as\b", r"\bas an? expert\b", r"\byour role\b",
    r"\byour goal\b", r"\bcontext:\b", r"\bbackground:\b"
]

CONSTRAINT_TERMS = [
    r"\bdo not\b", r"\bdon't\b", r"\bmust\b", r"\bnever\b", r"\blimit to\b",
    r"\bonly\b", r"\bmaximum\b", r"\bminimum\b", r"\bavoid\b", r"\bkeep it\b"
]

def evaluate_prompt(prompt_text: str) -> PromptAnalysisResponse:
    text = prompt_text.strip()
    words = text.split()
    word_count = len(words)
    lower_text = text.lower()

    # 1. Clarity (0-100)
    clarity_score = 70
    if word_count < 6:
        clarity_score -= 35
    elif word_count > 150:
        clarity_score -= 10
    if "?" in text or any(k in lower_text for k in ["write", "explain", "generate", "create", "analyze", "list"]):
        clarity_score += 15
    clarity_score = max(10, min(100, clarity_score))

    # 2. Specificity (0-100)
    specificity_score = 40
    # Numbers, code blocks, or technical terms increase specificity
    if re.search(r'\d+', text):
        specificity_score += 20
    if word_count >= 15:
        specificity_score += 20
    if word_count >= 30:
        specificity_score += 15
    specificity_score = max(10, min(100, specificity_score))

    # 3. Context (0-100)
    has_role = any(re.search(term, lower_text) for term in ROLE_TERMS)
    context_score = 85 if has_role else (50 if word_count > 25 else 25)

    # 4. Constraints (0-100)
    constraint_matches = [t for t in CONSTRAINT_TERMS if re.search(t, lower_text)]
    constraints_score = min(100, len(constraint_matches) * 35 + 20)

    # 5. Output Formatting (0-100)
    format_matches = [t for t in FORMAT_TERMS if re.search(t, lower_text)]
    formatting_score = min(100, len(format_matches) * 45 + 15)

    # 6. Ambiguity Reduction (0-100, higher = less ambiguous)
    vague_found = [t for t in VAGUE_TERMS if re.search(t, lower_text)]
    ambiguity_reduction = max(15, 100 - (len(vague_found) * 25))

    # 7. Completeness (0-100)
    completeness_score = int(
        (clarity_score * 0.2) +
        (specificity_score * 0.2) +
        (context_score * 0.2) +
        (constraints_score * 0.2) +
        (formatting_score * 0.2)
    )

    # Overall weighted average
    overall_score = int(
        (clarity_score * 0.18) +
        (specificity_score * 0.18) +
        (context_score * 0.16) +
        (constraints_score * 0.16) +
        (formatting_score * 0.16) +
        (ambiguity_reduction * 0.16)
    )

    # Strengths and Weaknesses
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []

    if has_role:
        strengths.append("Defines a clear persona or contextual background.")
    else:
        weaknesses.append("Lacks explicit role assignment (e.g. 'You are a senior developer...').")
        suggestions.append("Add a persona or perspective to frame the response context.")

    if format_matches:
        strengths.append(f"Specifies desired output structure ({', '.join([f.replace(r'\\b', '') for f in format_matches[:2]])}).")
    else:
        weaknesses.append("Does not define desired output format (Markdown, JSON, bullet points).")
        suggestions.append("Explicitly state the output format, such as 'Format your response as a Markdown table'.")

    if constraint_matches:
        strengths.append("Sets actionable negative constraints or boundaries.")
    else:
        weaknesses.append("No boundary constraints provided (e.g. length limits, excluded topics).")
        suggestions.append("Include constraints such as 'Keep the explanation under 200 words' or 'Do not use jargon'.")

    if vague_found:
        weaknesses.append(f"Contains subjective or ambiguous qualifiers: {', '.join([v.replace(r'\\b', '') for v in vague_found[:3]])}.")
        suggestions.append("Replace vague terms like 'fast' or 'good' with measurable quantitative criteria.")

    if clarity_score >= 80:
        strengths.append("High instructional clarity and direct call to action.")

    # Generate an improved prompt version
    improved = _generate_improved_prompt(text, has_role, format_matches, constraint_matches, vague_found)

    summary = (
        f"Prompt scored {overall_score}/100. "
        + ("It is well-structured for immediate LLM deployment." if overall_score >= 75
           else "It would benefit from tighter constraints and structured formatting.")
    )

    return PromptAnalysisResponse(
        original_prompt=text,
        overall_score=overall_score,
        metrics=PromptMetrics(
            clarity=clarity_score,
            specificity=specificity_score,
            context=context_score,
            constraints=constraints_score,
            output_formatting=formatting_score,
            completeness=completeness_score,
            ambiguity_reduction=ambiguity_reduction,
        ),
        strengths=strengths,
        weaknesses=weaknesses,
        suggestions=suggestions,
        improved_prompt=improved,
        analysis_summary=summary,
        disclaimer="Prompt quality analysis evaluates structural completeness and clarity. It is separate from AI text detection and does not determine AI authorship.",
    )

def _generate_improved_prompt(
    text: str,
    has_role: bool,
    format_matches: List[str],
    constraint_matches: List[str],
    vague_found: List[str]
) -> str:
    parts = []
    if not has_role:
        parts.append("### Role & Context\nYou are a domain specialist with deep expertise in technical communication.")
    else:
        parts.append("### Context\n" + text.split('.')[0] + ".")

    parts.append("### Task\n" + text)

    parts.append("### Requirements & Constraints\n- Be specific, concise, and technically accurate.\n- Address edge cases and potential failure modes.")
    if not constraint_matches:
        parts.append("- Avoid generic filler language; jump straight to actionable answers.")

    if not format_matches:
        parts.append("### Output Format\n- Provide the output in clean GitHub-flavored Markdown.\n- Use bullet points for key takeaways and code blocks for implementations.")

    return "\n\n".join(parts)
