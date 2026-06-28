package com.aipoc.controller;

import com.aipoc.dto.TimeResponse;
import com.aipoc.service.TimeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller exposing the current server time.
 *
 * <p>All business logic is delegated to {@link TimeService}.
 * This controller is intentionally thin — it only handles HTTP concerns.
 *
 * <p>Base path: {@code /api/v1/time}
 */
@RestController
@RequestMapping("/api/v1/time")
@Tag(name = "Time", description = "Current server time API")
public class TimeController {

    private static final Logger log = LoggerFactory.getLogger(TimeController.class);

    private final TimeService timeService;

    /**
     * Constructs a {@code TimeController} with the required {@link TimeService}.
     *
     * @param timeService the service used to obtain the current time; must not be {@code null}
     */
    public TimeController(final TimeService timeService) {
        this.timeService = timeService;
    }

    /**
     * Returns the current server time.
     *
     * <p>Response includes the ISO-8601 timestamp with timezone offset,
     * the server's timezone ID, and a human-readable formatted string.
     *
     * @return {@code 200 OK} with a {@link TimeResponse} body
     */
    @GetMapping
    @Operation(
            summary = "Get current server time",
            description = "Returns the current server timestamp, timezone, and a formatted time string.")
    @ApiResponse(
            responseCode = "200",
            description = "Current time retrieved successfully",
            content = @Content(schema = @Schema(implementation = TimeResponse.class)))
    public ResponseEntity<TimeResponse> getCurrentTime() {
        log.info("Received request for current time");
        final TimeResponse response = timeService.getCurrentTime();
        return ResponseEntity.ok(response);
    }
}
