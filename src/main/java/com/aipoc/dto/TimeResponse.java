package com.aipoc.dto;

import java.time.ZonedDateTime;

/**
 * Response DTO for the current-time API endpoint.
 *
 * <p>Carries the current server timestamp along with the active timezone
 * and a human-readable formatted string for convenience.
 *
 * @param timestamp  the current date-time with timezone offset (ISO-8601)
 * @param timezone   the timezone ID of the server (e.g. {@code America/Los_Angeles})
 * @param formatted  a human-readable representation of the current time
 */
public record TimeResponse(
        ZonedDateTime timestamp,
        String timezone,
        String formatted) {
}
