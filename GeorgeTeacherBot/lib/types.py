# TODO: move it to something more rigorous (like protobuf)
# TODO: force a blank elem to be a singleton
class Triplet:
    def __init__(
            self,
            phrase_to_ask: str = "",
            language_to_ask: str = "",
            phrase_to_answer: str = "",
            language_to_answer: str = "",
            context: str = ""
    ) -> None:
        self._phrase_to_ask = phrase_to_ask
        self._language_to_ask = language_to_ask
        self._phrase_to_answer = phrase_to_answer
        self._language_to_answer = language_to_answer
        self._context = context

    @property
    def phrase_to_ask(self) -> str:
        return self._phrase_to_ask

    @property
    def language_to_ask(self) -> str:
        return self._language_to_ask

    @property
    def phrase_to_answer(self) -> str:
        return self._phrase_to_answer

    @property
    def language_to_answer(self) -> str:
        return self._language_to_answer

    @property
    def context(self) -> str:
        return self._context

    def __hash__(self) -> int:
        return hash(
            "".join(
                [
                    self._phrase_to_ask,
                    self._language_to_ask,
                    self._phrase_to_answer,
                    self._language_to_answer,
                    self._context  # TODO: think about removing this
                ]
            )
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return (self._phrase_to_ask == other.phrase_to_ask)\
                and (self._language_to_ask == other.language_to_ask)\
                and (self._phrase_to_answer == other.phrase_to_answer)\
                and (self._language_to_answer == other.language_to_answer)\
                and (self._context == other.context)
        else:
            return False
