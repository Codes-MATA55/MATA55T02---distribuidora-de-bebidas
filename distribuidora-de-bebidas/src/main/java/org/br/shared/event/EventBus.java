package org.br.shared.event;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class EventBus {

    private final List<DomainEvent> eventosPublicados = new ArrayList<>();

    public void publicar(DomainEvent evento) {

        if (evento == null) {
            throw new IllegalArgumentException(
                    "Evento é obrigatório"
            );
        }

        eventosPublicados.add(evento);
    }

    public List<DomainEvent> eventosPublicados() {
        return Collections.unmodifiableList(eventosPublicados);
    }

    public void limpar() {
        eventosPublicados.clear();
    }
}
