from dataclasses import dataclass, field

@dataclass
class Pregunta:
    id: str
    numero: str
    pregunta: str
    tipo: str
    tipo_opciones: str
    dimension: str
    fuente: str
    opciones: list[dict] = field(default_factory=list)
    hijas: list[dict] = field(default_factory=list)

    def to_dict(self):
        return self.__dict__

@dataclass(kw_only=True)
class PreguntaHija(Pregunta):
    opcion_papa: str = None

    
