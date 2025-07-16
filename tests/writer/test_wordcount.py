import pytest  # pylint: disable=W0611,E0401
from writer.wordcount import get_ia_writer_style_wordcount_from_string


def test_checkbox_pattern():
    """Test that checkbox patterns are removed and don't count as words"""
    test_cases = [
        ("- [ ] ", 0),  # Empty checkbox
        ("- [x] ", 0),  # Checked checkbox
        ("- [ ] Hello", 1),  # Checkbox with word
        ("Text\n- [ ] Task\nMore text", 4),  # Checkbox in middle of content
        ("- [ ] Task 1\n- [x] Task 2", 4),  # Multiple checkboxes
    ]

    for input_text, expected_count in test_cases:
        assert (
            get_ia_writer_style_wordcount_from_string(input_text) == expected_count
        ), f"Failed for input: '{input_text}', expected {expected_count} words"


def test_ia_writer_indentation():
    """Test that indentation word counting matches iA Writer's behavior"""
    test_text = "Normal text\n\n\tIndented block\n\tcontinues here\n\nNormal text\n\tThis indent without blank line\nNormal text"
    result = get_ia_writer_style_wordcount_from_string(test_text)
    assert result == 11, (
        f"Expected 11 words, got {result}. iA Writer should count:\n"
        + "- 'Normal text' (2)\n"
        + "- 'Normal text' (2)\n"
        + "- 'This indent without blank line' (5)\n"
        + "- 'Normal text' (2)\n"
        + "Total: 11 words"
    )

    # Additional test cases to verify specific behaviors
    test_cases = [
        # Basic indentation after blank line (should exclude)
        ("1text\n\n\tindented\n\tstill indented\n\ntext", 2),
        # Indentation without blank line (should include)
        ("2text\n\tindented\ntext", 3),
        # Multiple indented blocks
        ("3text\n\n\tblock one\n\tmore one\n\ntext\n\n\tblock two\n\tmore two", 2),
        # Mixed indentation
        ("4text\n\tno blank line indent\n\ntext\n\n\tblank line indent", 6),
    ]

    for test_text, expected_count in test_cases:
        result = get_ia_writer_style_wordcount_from_string(test_text)
        assert (
            result == expected_count
        ), f"Failed for text:\n{test_text}\nExpected {expected_count} words, got {result}"


def test_special_character_splitting():
    """Test that special characters are properly converted to spaces for word counting"""
    test_cases = [
        # Basic cases - matching [_:><\/=]
        ("snake_case", 2, "underscore splits words"),
        ("13:37", 2, "colon splits numbers"),
        ("3<4", 2, "less than splits"),
        ("4>3", 2, "greater than splits"),
        ("1/11/1111", 3, "forward slashes split"),
        ("x=3", 2, "equals sign splits"),
        # Multiple of same special chars
        ("snake_case_long", 3, "multiple underscores"),
        ("1:2:3:4", 4, "multiple colons"),
        ("a<b>c=d", 4, "mixed special chars from pattern"),
        # Edge cases with these specific chars
        ("_start_end_", 2, "leading/trailing underscore"),
        ("===", 0, "only special chars"),
        ("a_", 1, "trailing special char"),
        ("_a", 1, "leading special char"),
    ]

    for input_text, expected_count, description in test_cases:
        result = get_ia_writer_style_wordcount_from_string(input_text)
        assert (
            result == expected_count
        ), f"{description}: Expected {expected_count} words for '{input_text}', got {result}"


def test_wordchar_slash_splitting():
    """Test that word characters separated by forward slash are split into words"""
    test_cases = [
        ("this/that", 2, "basic slash split"),
        ("2/2", 2, "number slash number"),
        ("red/blue/green", 3, "multiple slashes"),
        ("a/b", 2, "single letters"),
        ("word/2", 2, "word and number"),
        ("2/word", 2, "number and word"),
        ("snake_case/word", 3, "interaction with previous pattern"),
    ]

    for input_text, expected_count, description in test_cases:
        result = get_ia_writer_style_wordcount_from_string(input_text)
        assert (
            result == expected_count
        ), f"{description}: Expected {expected_count} words for '{input_text}', got {result}"


def test_decimal_joining():
    """Test that decimal numbers are counted as single words"""
    test_cases = [
        ("1.11", 1, "basic decimal"),
        ("3.14159", 1, "pi"),
        ("1.2.3", 1, "multiple dots"),
        ("1.a", 2, "number dot letter"),
        ("a.1", 2, "letter dot number"),
        ("version 2.0", 2, "decimal in sentence"),
        ("1.11.23", 1, "version number"),
        ("123.456.789", 1, "multiple decimal sections"),
    ]

    for input_text, expected_count, description in test_cases:
        result = get_ia_writer_style_wordcount_from_string(input_text)
        assert (
            result == expected_count
        ), f"{description}: Expected {expected_count} words for '{input_text}', got {result}"


def test_emdash_splitting():
    """Test that words separated by em dash are split correctly"""
    test_cases = [
        ("word—word", 2, "basic em dash split"),
        ("multiple—word—split", 3, "multiple em dashes"),
        ("1—2", 2, "numbers with em dash"),
        ("no—split—here—either", 4, "longer em dash split"),
        ("pre — post", 2, "em dash with spaces already"),
    ]

    for input_text, expected_count, description in test_cases:
        result = get_ia_writer_style_wordcount_from_string(input_text)
        assert (
            result == expected_count
        ), f"{description}: Expected {expected_count} words for '{input_text}', got {result}"
