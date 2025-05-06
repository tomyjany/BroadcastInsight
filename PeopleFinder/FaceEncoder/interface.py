from abc import ABC, abstractmethod


class EncoderI(ABC):
    @abstractmethod
    def encode(self, image: bytes) -> bytes:
        pass


libraries = [
    "insightface",
]


def get_encoder(encoder_name: str) -> EncoderI:
    if encoder_name not in libraries:
        raise NotImplementedError(f"Encoder {encoder_name} not implemented")
    if encoder_name == "insightface":
        from PeopleFinder.FaceEncoder.insightEncoder import InsightEncoder

        return InsightEncoder()
