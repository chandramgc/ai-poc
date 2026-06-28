package com.aipoc.service.impl;

import com.aipoc.dto.TimeResponse;
import com.aipoc.service.TimeService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Default implementation of {@link TimeService} that returns the current
 * system time in the JVM's default timezone.
 *
 * <p>The formatted string uses a locale-neutral, human-readable pattern
 * ({@code yyyy-MM-dd HH:mm:ss z}) suitable for API consumers.
 */
@Service
public class TimeServiceImpl implements TimeService {

    private static final Logger log = LoggerFactory.getLogger(TimeServiceImpl.class);

    /** Human-readable date-time pattern included in every response. */
    private static final DateTimeFormatter DISPLAY_FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss z");

    /**
     * {@inheritDoc}
     *
     * <p>Captures the current {@link ZonedDateTime} at the moment of invocation.
     * The timezone is derived from {@link ZoneId#systemDefault()}.
     */
    @Override
    public TimeResponse getCurrentTime() {
        final ZonedDateTime now = ZonedDateTime.now();
        final String timezone = ZoneId.systemDefault().getId();
        final String formatted = now.format(DISPLAY_FORMATTER);

        log.debug("Serving current time: {} (timezone={})", formatted, timezone);

        return new TimeResponse(now, timezone, formatted);
    }
}
