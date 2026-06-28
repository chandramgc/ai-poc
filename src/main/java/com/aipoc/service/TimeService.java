package com.aipoc.service;

import com.aipoc.dto.TimeResponse;

/**
 * Contract for retrieving the current server time.
 *
 * <p>Implementations are responsible for determining the authoritative
 * time source and formatting strategy.
 */
public interface TimeService {

    /**
     * Returns the current server time encapsulated in a {@link TimeResponse}.
     *
     * @return a non-null {@code TimeResponse} containing the current timestamp,
     *         timezone, and a formatted string representation
     */
    TimeResponse getCurrentTime();
}
