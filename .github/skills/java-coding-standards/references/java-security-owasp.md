# Java Security & OWASP Reference Guide

This reference details the OWASP Top 10 Java-specific mitigations, secure coding patterns, SAST/DAST tool integration, and dependency security practices.

---

## 1. OWASP Top 10 (2025) — Java-Specific Rules

| OWASP ID | Risk | Java-Specific Mitigation |
|----------|------|--------------------------|
| **A01** | Broken Access Control | Spring Security `@PreAuthorize`, `@Secured`, method-level security with SpEL expressions. Deny-by-default with `.anyRequest().authenticated()`. |
| **A02** | Cryptographic Failures | Use `java.security` and `javax.crypto` APIs. Avoid MD5/SHA-1 — use AES-256-GCM for encryption, SHA-256+ for hashing. Store keys in vaults, never in code. |
| **A03** | Injection | Parameterized queries via JPA `@Query` / JDBC `PreparedStatement`. Validate input with Jakarta Bean Validation (`@NotBlank`, `@Pattern`). Never concatenate SQL. |
| **A04** | Insecure Design | Incorporate threat modeling during spec phase. Write security user stories. Use abuse-case analysis before implementation. |
| **A05** | Security Misconfiguration | Spring Security auto-configuration. Explicit CORS, CSRF, and security headers. Disable debug endpoints in production. |
| **A06** | Vulnerable Components | Enable Dependabot/Snyk scanning in CI. Generate SBOM with CycloneDX. Pin dependency versions with Gradle lock files. |
| **A07** | Identity & Authentication | Spring Security OAuth2 Resource Server for JWT validation. Enforce session fixation protection. Use `BCryptPasswordEncoder` for passwords. |
| **A08** | Software & Data Integrity | SLSA provenance for build artifacts. Sign JARs with `jarsigner`. Pin CI action versions by SHA, not tag. |
| **A09** | Security Logging & Monitoring | SLF4J security event logging. Structured audit trails with `traceId`/`userId`. Forward to SIEM via OpenTelemetry. |
| **A10** | SSRF | Validate and allowlist URLs before HTTP calls. Restrict `HttpClient` to known hosts. Block internal network ranges (RFC 1918). |

---

## 2. Secure Coding Patterns

### Input Validation with Jakarta Bean Validation

```java
public record CreateUserRequest(
    @NotBlank(message = "Username is required")
    @Size(min = 3, max = 50, message = "Username must be 3-50 characters")
    @Pattern(regexp = "^[a-zA-Z0-9_]+$", message = "Username must be alphanumeric")
    String username,

    @NotBlank(message = "Email is required")
    @Email(message = "Email must be valid")
    String email,

    @NotBlank(message = "Password is required")
    @Size(min = 12, message = "Password must be at least 12 characters")
    String password
) {}
```

### Spring Security Configuration (CORS, CSRF, Headers)

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf
                .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
                .csrfTokenRequestHandler(new CsrfTokenRequestAttributeHandler()))
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .headers(headers -> headers
                .contentSecurityPolicy(csp ->
                    csp.policyDirectives("default-src 'self'; script-src 'self'"))
                .frameOptions(frame -> frame.deny())
                .httpStrictTransportSecurity(hsts ->
                    hsts.includeSubDomains(true).maxAgeInSeconds(31536000)))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated())
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("https://app.example.com"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
        config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
        config.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", config);
        return source;
    }
}
```

### JWT Token Validation

```java
@Configuration
public class JwtConfig {

    @Bean
    public JwtDecoder jwtDecoder(
            @Value("${spring.security.oauth2.resourceserver.jwt.issuer-uri}") String issuerUri) {

        NimbusJwtDecoder decoder = JwtDecoders.fromIssuerLocation(issuerUri);

        // ✅ Validate issuer, audience, and expiration
        OAuth2TokenValidator<Jwt> validators = new DelegatingOAuth2TokenValidator<>(
            JwtValidators.createDefaultWithIssuer(issuerUri),
            new JwtClaimValidator<List<String>>("aud",
                aud -> aud != null && aud.contains("my-api"))
        );

        decoder.setJwtValidator(validators);
        return decoder;
    }
}
```

### Secure Password Hashing (BCrypt)

```java
@Configuration
public class PasswordConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        // ✅ BCrypt with strength 12 — adaptive hashing
        return new BCryptPasswordEncoder(12);
    }
}

@Service
public class UserService {

    private final PasswordEncoder passwordEncoder;
    private final UserRepository userRepository;

    public UserService(PasswordEncoder passwordEncoder, UserRepository userRepository) {
        this.passwordEncoder = passwordEncoder;
        this.userRepository = userRepository;
    }

    public void registerUser(CreateUserRequest request) {
        User user = new User();
        user.setUsername(request.username());
        // ✅ Hash password — never store plaintext
        user.setPasswordHash(passwordEncoder.encode(request.password()));
        userRepository.save(user);
    }

    public boolean verifyPassword(String rawPassword, String storedHash) {
        return passwordEncoder.matches(rawPassword, storedHash);
    }
}
```

### Environment-Based Secret Management

```yaml
# application.yml — ✅ Use environment variable placeholders
spring:
  datasource:
    url: ${DB_URL}
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: ${JWT_ISSUER_URI}
```

```java
// ❌ NEVER do this (S2068 Blocker)
String apiKey = "sk-abc123secret";

// ✅ Use environment variables
String apiKey = System.getenv("API_KEY");

// ✅ Or use @Value with Spring
@Value("${api.key}")
private String apiKey;
```

---

## 3. SAST/DAST Integration

### SonarQube Security Hotspot Rules

Key security hotspot categories to review in SonarQube:

| Category | Rule IDs | Action |
|----------|----------|--------|
| Credentials | S2068, S6418 | Move to env vars or vault |
| Injection | S2077, S5131, S5145 | Use parameterized queries, sanitize output |
| Cryptography | S3329, S4426, S5547 | Use strong algorithms, unique IVs |
| XML Processing | S2755 | Disable XXE in all XML parsers |
| SSRF | S5144 | Validate and allowlist URLs |

### SpotBugs with Find-Sec-Bugs Plugin

```groovy
// build.gradle
plugins {
    id 'com.github.spotbugs' version '6.1.2'
}

dependencies {
    spotbugsPlugins 'com.h3xstream.findsecbugs:findsecbugs-plugin:1.13.0'
}

spotbugs {
    effort = 'max'
    reportLevel = 'low'
    excludeFilter = file("$rootDir/config/spotbugs-exclude.xml")
}
```

### OWASP Dependency-Check Gradle Plugin

```groovy
// build.gradle
plugins {
    id 'org.owasp.dependencycheck' version '10.0.4'
}

dependencyCheck {
    failBuildOnCVSS = 7.0f          // Fail build on HIGH+ vulnerabilities
    formats = ['HTML', 'JSON']
    suppressionFile = "$rootDir/config/owasp-suppressions.xml"
    analyzers {
        assemblyEnabled = false      // Disable .NET analyzer
    }
}
```

```bash
# Run dependency check
./gradlew dependencyCheckAnalyze
```

### ZAP (DAST) Integration in CI

```yaml
# .github/workflows/dast.yml
name: DAST Scan
on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly Monday 2am

jobs:
  zap-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Start application
        run: docker compose up -d app

      - name: OWASP ZAP Baseline Scan
        uses: zaproxy/action-baseline@v0.14.0
        with:
          target: 'http://localhost:8080'
          rules_file_name: 'zap-rules.tsv'
          fail_action: 'warn'

      - name: Upload ZAP Report
        uses: actions/upload-artifact@v4
        with:
          name: zap-report
          path: report_html.html
```

---

## 4. Dependency Security

### Gradle Dependency Verification

```bash
# Generate verification metadata
./gradlew --write-verification-metadata sha256,pgp
```

This creates `gradle/verification-metadata.xml` with checksums for all dependencies, preventing supply chain attacks.

### Lock File Usage

```groovy
// settings.gradle
dependencyResolutionManagement {
    repositories {
        mavenCentral()
    }
}

// build.gradle — activate dependency locking
dependencyLocking {
    lockAllConfigurations()
}
```

```bash
# Generate/update lock files
./gradlew dependencies --write-locks
```

### SBOM Generation with CycloneDX Gradle Plugin

```groovy
// build.gradle
plugins {
    id 'org.cyclonedx.bom' version '1.10.0'
}

cyclonedxBom {
    includeConfigs = ["runtimeClasspath"]
    outputFormat = "json"
    outputName = "sbom"
    destination = file("$buildDir/reports/sbom")
}
```

```bash
# Generate SBOM
./gradlew cyclonedxBom
```

> [!TIP]
> Integrate SBOM generation into your CI pipeline and store SBOMs alongside release artifacts for supply chain transparency.
