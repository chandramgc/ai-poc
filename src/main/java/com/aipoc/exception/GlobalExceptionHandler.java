package com.aipoc.exception;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Global exception handler for all REST controllers.
 *
 * <p>Centralises HTTP error responses so that no controller needs its own
 * try-catch blocks. Every exception type is mapped to an appropriate HTTP
 * status code and a consistent JSON error body.
 *
 * <p>Error response shape:
 * <pre>
 * {
 *   "timestamp": "2024-01-15T10:30:00Z",
 *   "status":    500,
 *   "error":     "Internal Server Error",
 *   "message":   "An unexpected error occurred",
 *   "path":      "/api/v1/time"
 * }
 * </pre>
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    private static final String KEY_TIMESTAMP = "timestamp";
    private static final String KEY_STATUS    = "status";
    private static final String KEY_ERROR     = "error";
    private static final String KEY_MESSAGE   = "message";
    private static final String KEY_PATH      = "path";

    /**
     * Handles all unhandled {@link Exception} types as a catch-all safety net.
     *
     * @param ex      the unhandled exception
     * @param request the current web request (used to extract the request path)
     * @return {@code 500 Internal Server Error} with a JSON error body
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGenericException(
            final Exception ex,
            final WebRequest request) {

        log.error("Unhandled exception on request [{}]: {}",
                request.getDescription(false), ex.getMessage(), ex);

        return buildErrorResponse(
                HttpStatus.INTERNAL_SERVER_ERROR,
                "An unexpected error occurred",
                request);
    }

    /**
     * Handles {@link IllegalArgumentException} — typically thrown for invalid input.
     *
     * @param ex      the exception carrying the validation message
     * @param request the current web request
     * @return {@code 400 Bad Request} with a JSON error body
     */
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, Object>> handleIllegalArgument(
            final IllegalArgumentException ex,
            final WebRequest request) {

        log.warn("Invalid argument on request [{}]: {}",
                request.getDescription(false), ex.getMessage());

        return buildErrorResponse(HttpStatus.BAD_REQUEST, ex.getMessage(), request);
    }

    /**
     * Builds a consistent error response map.
     *
     * @param status  the HTTP status to return
     * @param message the error message included in the response body
     * @param request the web request providing the path
     * @return a {@link ResponseEntity} containing the structured error body
     */
    private ResponseEntity<Map<String, Object>> buildErrorResponse(
            final HttpStatus status,
            final String message,
            final WebRequest request) {

        final Map<String, Object> body = new LinkedHashMap<>();
        body.put(KEY_TIMESTAMP, Instant.now().toString());
        body.put(KEY_STATUS, status.value());
        body.put(KEY_ERROR, status.getReasonPhrase());
        body.put(KEY_MESSAGE, message);
        body.put(KEY_PATH, request.getDescription(false).replace("uri=", ""));

        return ResponseEntity.status(status).body(body);
    }
}
