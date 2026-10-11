from Core.reading_position import word_start


def test_word_start_snaps_back_to_word_beginning():
    assert word_start('hello world', 8) == 6


def test_next_sentence_skips_to_following_sentence():
    from Core.reading_position import next_sentence
    assert next_sentence('One. Two. Three.', 1) == 5


def test_next_sentence_at_last_sentence_returns_none():
    from Core.reading_position import next_sentence
    assert next_sentence('One. Two.', 6) is None


def test_previous_sentence_restarts_current_sentence():
    from Core.reading_position import previous_sentence
    assert previous_sentence('One. Two words here.', 12) == 5


def test_previous_sentence_at_start_goes_back_one():
    from Core.reading_position import previous_sentence
    assert previous_sentence('One. Two.', 5) == 0


def test_word_start_on_space_moves_to_next_word():
    assert word_start('hello world', 5) == 6
