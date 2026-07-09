package shared.event;

import org.br.shared.event.DomainEvent;
import org.br.shared.event.EventBus;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.Instant;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class EventBusTest {

    @Test
    @DisplayName("Deve publicar evento em memoria")
    void devePublicarEventoEmMemoria() {

        EventBus eventBus = new EventBus();
        DomainEvent evento = new EventoTeste(Instant.now());

        eventBus.publicar(evento);

        assertEquals(1, eventBus.eventosPublicados().size());
        assertEquals(evento, eventBus.eventosPublicados().get(0));
    }

    @Test
    @DisplayName("Deve rejeitar evento nulo")
    void deveRejeitarEventoNulo() {

        EventBus eventBus = new EventBus();

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> eventBus.publicar(null)
                );

        assertEquals(
                "Evento é obrigatório",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve limpar eventos publicados")
    void deveLimparEventosPublicados() {

        EventBus eventBus = new EventBus();
        eventBus.publicar(new EventoTeste(Instant.now()));

        eventBus.limpar();

        assertEquals(0, eventBus.eventosPublicados().size());
    }

    private record EventoTeste(Instant ocorridoEm) implements DomainEvent {
    }
}
