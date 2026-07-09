package shared.valueobject;

import org.br.shared.valueobject.Quantidade;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class QuantidadeTest {

    @Test
    @DisplayName("Deve criar quantidade valida")
    void deveCriarQuantidadeValida() {

        Quantidade quantidade = new Quantidade(10);

        assertEquals(10, quantidade.valor());
    }

    @Test
    @DisplayName("Deve rejeitar quantidade zero")
    void deveRejeitarQuantidadeZero() {

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> new Quantidade(0)
                );

        assertEquals(
                "Quantidade deve ser maior que zero",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve rejeitar quantidade negativa")
    void deveRejeitarQuantidadeNegativa() {

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> new Quantidade(-1)
                );

        assertEquals(
                "Quantidade deve ser maior que zero",
                exception.getMessage()
        );
    }
}
