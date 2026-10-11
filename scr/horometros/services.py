from decimal import Decimal, InvalidOperation


class ValidadorDatos:
    """Valida datos de entrada del dominio, en particular lecturas de horómetro."""

    def validar(self, equipo, valor) -> bool:
        """True si 'valor' es una lectura de horómetro válida para el equipo.

        Reglas:
        - No puede ser negativa.
        - No puede ser menor al horómetro actual (el horómetro no retrocede).
        """
        try:
            lectura = Decimal(valor)
        except (InvalidOperation, TypeError, ValueError):
            return False
        if lectura < 0:
            return False
        return lectura >= equipo.horometro_actual
