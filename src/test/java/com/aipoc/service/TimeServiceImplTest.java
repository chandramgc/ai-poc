package com.aipoc.service;

import com.aipoc.dto.TimeResponse;
import com.aipoc.service.impl.TimeServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.ZoneId;
import java.time.ZonedDateTime;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Unit tests for {@link TimeServiceImpl}.
 *
 * <p>No Spring context is loaded — pure Mockito-free unit test since
 * {@link TimeServiceImpl} has no collaborators.
 */
@DisplayName("TimeServiceImpl unit tests")
class TimeServiceImplTest {

    private TimeService timeService;

    /** Instantiates a fresh {@link TimeServiceImpl} before each test. */
    @BeforeEach
    void setUp() {
        timeService = new TimeServiceImpl();
    }

    @Test
    @DisplayName("getCurrentTime() returns a non-null response")
    void getCurrentTime_returnsNonNullResponse() {
        final TimeResponse response = timeService.getCurrentTime();

        assertThat(response).isNotNull();
    }

    @Test
    @DisplayName("getCurrentTime() timestamp is close to now")
    void getCurrentTime_timestampIsCloseToNow() {
        final ZonedDateTime before = ZonedDateTime.now().minusSeconds(1);

        final TimeResponse response = timeService.getCurrentTime();

        final ZonedDateTime after = ZonedDateTime.now().plusSeconds(1);
        assertThat(response.timestamp())
                .isAfterOrEqualTo(before)
                .isBeforeOrEqualTo(after);
    }

    @Test
    @DisplayName("getCurrentTime() timezone matches the JVM default")
    void getCurrentTime_timezoneMatchesSystemDefault() {
        final TimeResponse response = timeService.getCurrentTime();

        assertThat(response.timezone())
                .isEqualTo(ZoneId.systemDefault().getId());
    }

    @Test
    @DisplayName("getCurrentTime() formatted string is not blank")
    void getCurrentTime_formattedIsNotBlank() {
        final TimeResponse response = timeService.getCurrentTime();

        assertThat(response.formatted()).isNotBlank();
    }
}
