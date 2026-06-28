package com.aipoc.controller;

import com.aipoc.dto.TimeResponse;
import com.aipoc.service.TimeService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Web-layer slice test for {@link TimeController}.
 *
 * <p>Uses {@code @WebMvcTest} to load only the web layer — no full application
 * context, no database, no real service. {@link TimeService} is mocked.
 */
@WebMvcTest(TimeController.class)
@DisplayName("TimeController web-layer tests")
class TimeControllerTest {

    private static final String TIME_API_PATH = "/api/v1/time";
    private static final DateTimeFormatter DISPLAY_FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss z");

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private TimeService timeService;

    @Test
    @DisplayName("GET /api/v1/time returns 200 OK with JSON body")
    void getCurrentTime_returns200WithJsonBody() throws Exception {
        final ZonedDateTime fixedTime =
                ZonedDateTime.of(2024, 6, 15, 10, 30, 0, 0, ZoneId.of("America/Los_Angeles"));
        final String formatted = fixedTime.format(DISPLAY_FORMATTER);

        when(timeService.getCurrentTime())
                .thenReturn(new TimeResponse(fixedTime, "America/Los_Angeles", formatted));

        mockMvc.perform(get(TIME_API_PATH).accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.timezone").value("America/Los_Angeles"))
                .andExpect(jsonPath("$.formatted").value(formatted))
                .andExpect(jsonPath("$.timestamp").isNotEmpty());
    }

    @Test
    @DisplayName("GET /api/v1/time returns 200 even on a different timezone")
    void getCurrentTime_returnsOkForUtcTimezone() throws Exception {
        final ZonedDateTime utcTime =
                ZonedDateTime.of(2024, 1, 1, 0, 0, 0, 0, ZoneId.of("UTC"));
        final String formatted = utcTime.format(DISPLAY_FORMATTER);

        when(timeService.getCurrentTime())
                .thenReturn(new TimeResponse(utcTime, "UTC", formatted));

        mockMvc.perform(get(TIME_API_PATH).accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.timezone").value("UTC"));
    }

    @Test
    @DisplayName("GET /api/v1/time returns 500 when service throws unexpected exception")
    void getCurrentTime_returns500WhenServiceFails() throws Exception {
        when(timeService.getCurrentTime())
                .thenThrow(new RuntimeException("Simulated internal error"));

        mockMvc.perform(get(TIME_API_PATH).accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isInternalServerError())
                .andExpect(jsonPath("$.status").value(500))
                .andExpect(jsonPath("$.error").value("Internal Server Error"));
    }
}
