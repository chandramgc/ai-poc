# Java Best Practices Reference Sheet

This guide serves as a practical, everyday cheat-sheet for developers working with Java 17+ in our codebase.

---

## 1. Null Safety Checklist

To prevent the most common runtime error (`NullPointerException`), follow these rules:

### Never Return Null
Always return empty collections or optional wrappers:
```java
// ❌ AVOID
public List<User> getUsers() {
    return null; 
}

// ✅ PREFER
public List<User> getUsers() {
    return Collections.emptyList();
}
```

### Validate Inbound Parameters
Check parameters for null at method entry points using `java.util.Objects`:
```java
public UserService(UserRepository repo) {
    this.repo = Objects.requireNonNull(repo, "UserRepository must not be null");
}
```

### Map Optional Fields
Avoid using `.get()` directly on `Optional`. Use `orElse`, `orElseThrow`, or functional maps instead:
```java
// ❌ AVOID
User user = optUser.get();

// ✅ PREFER
User user = optUser.orElseThrow(() -> new UserNotFoundException(userId));
```

---

## 2. Collections and Stream Processing

### Leverage Immutable Collections
Create read-only lists and maps where possible using modern Java factories:
```java
List<String> roles = List.of("ADMIN", "DEVELOPER", "GUEST");
Map<String, String> config = Map.of("timeout", "5000", "retry", "3");
```

### Streams over Imperative Loops
Use streams for processing collections (filtering, transforming, collecting):
```java
// Transform a list of users to active user names
List<String> activeNames = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .collect(Collectors.toList());
```

---

## 3. String Concatenation and Formatting

### Avoid System.out Logging
Never use string concatenation in log messages. Use SLF4J curly-brace placeholders to save memory:
```java
// ❌ AVOID
log.debug("User " + name + " logged in with status " + status);

// ✅ PREFER
log.debug("User {} logged in with status {}", name, status);
```

### String Builder for Loops
When building large strings inside cycles or loops, use `StringBuilder`:
```java
StringBuilder sb = new StringBuilder();
for (String part : parts) {
    sb.append(part).append(",");
}
String result = sb.toString();
```

---

## 4. Resource Allocation (Try-With-Resources)

Ensure all streams, sockets, and reader instances are closed properly to prevent memory leaks. The compiler will automatically handle closure when wrapped in a try-with-resources statement:
```java
// Database connection handles, file streams, HTTP client connections
try (BufferedReader br = new BufferedReader(new FileReader("data.txt"))) {
    String line = br.readLine();
} catch (IOException e) {
    log.error("Failed to read file", e);
}
```

---

## 5. Security & Sensitive Configurations

### Secrets Outside Code
Never store API keys, tokens, or passwords in plain-text config files or variables:
```java
// ❌ AVOID
private String dbPassword = "password123";

// ✅ PREFER
@Value("${app.database-password}")
private String dbPassword;
```

### Parameterized SQL Queries
Prevent SQL injection by binding variables to prepared statements:
```java
String sql = "SELECT * FROM orders WHERE user_id = ?";
PreparedStatement ps = connection.prepareStatement(sql);
ps.setString(1, userId);
ResultSet rs = ps.executeQuery();
```
