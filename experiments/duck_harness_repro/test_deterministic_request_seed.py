from deterministic_request_seed import RequestSeedSequence, stable_request_seed


def test_seed_is_stable_and_namespaced() -> None:
    assert stable_request_seed("tn36", 0, "pair-v1") == stable_request_seed(
        "tn36", 0, "pair-v1"
    )
    assert stable_request_seed("tn36", 0, "pair-v1") != stable_request_seed(
        "ft09", 0, "pair-v1"
    )
    assert stable_request_seed("tn36", 0, "pair-v1") != stable_request_seed(
        "tn36", 1, "pair-v1"
    )


def test_sequence_is_independent_between_games() -> None:
    first = RequestSeedSequence("ar25", salt="pair-v1")
    noisy_neighbor = RequestSeedSequence("tn36", salt="pair-v1")
    second = RequestSeedSequence("ar25", salt="pair-v1")

    expected = [first.next_seed() for _ in range(3)]
    for _ in range(20):
        noisy_neighbor.next_seed()
    observed = [second.next_seed() for _ in range(3)]

    assert observed == expected


def test_empty_namespace_preserves_original_fallback() -> None:
    sequence = RequestSeedSequence(None, salt="pair-v1", fallback_seed=-1)
    assert sequence.next_seed() == -1
    assert sequence.next_seed() == -1
