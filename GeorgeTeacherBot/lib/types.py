# TODO: move it to something more rigorous (like protobuf)
# TODO: force a blank elem to be a singleton
class Triplet:
    def __init__(
            self,
            word_to_ask: str = "",
            language_to_ask: str = "",
            word_to_answer: str = "",
            language_to_answer: str = "",
            context: str = ""
    ) -> None:
        self._word_to_ask = word_to_ask
        self._language_to_ask = language_to_ask
        self._word_to_answer = word_to_answer
        self._language_to_answer = language_to_answer
        self._context = context
    
    @property
    def word_to_ask(self) -> str:
        return self._word_to_ask

    @property
    def language_to_ask(self) -> str:
        return self._language_to_ask

    @property
    def word_to_answer(self) -> str:
        return self._word_to_answer

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
                    self._word_to_ask,
                    self._language_to_ask,
                    self._word_to_answer,
                    self._language_to_answer,
                    self._context  # TODO: think about removing this
                ]
            )
        )

    def __eq__(self, other: 'Triplet') -> bool:
        return (self._word_to_ask == other.word_to_ask)\
            and (self._language_to_ask == other.language_to_ask)\
            and (self._word_to_answer == other.word_to_answer)\
            and (self._language_to_answer == other.language_to_answer)\
            and (self._context == other.context)

