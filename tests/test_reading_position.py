from Core.reading_position import word_start


def test_word_start_snaps_back_to_word_beginning():
    assert word_start('hello world', 8) == 6


def test_word_start_on_space_moves_to_next_word():
    assert word_start('hello world', 5) == 6
