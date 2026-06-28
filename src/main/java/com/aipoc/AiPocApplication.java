package com.aipoc;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Entry point for the AI POC Spring Boot application.
 *
 * <p>This application exposes a REST API that provides the current server time
 * and is configured for SonarQube quality analysis.
 */
@SpringBootApplication
public class AiPocApplication {

    /**
     * Private constructor to prevent instantiation of this utility-style launcher.
     * Spring Boot requires a public main method but not a public constructor.
     */
    protected AiPocApplication() {
        // Spring Boot entry point — do not instantiate directly
    }

    /**
     * Application entry point.
     *
     * @param args command-line arguments passed to the Spring Boot launcher
     */
    public static void main(final String[] args) {
        SpringApplication.run(AiPocApplication.class, args);
    }
}
