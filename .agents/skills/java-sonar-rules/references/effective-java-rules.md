# Effective Java — Key Rules Quick Reference

A condensed reference of the most impactful rules from *Effective Java* (3rd Ed, Joshua Bloch)
relevant to SonarQube compliance and modern Java best practices.

---

## Item 1 — Static Factory Methods over Constructors
```java
// ❌ Avoid
new Boolean(true);

// ✅ Prefer
Boolean.valueOf(true);
```
**Why**: Factory methods have names, can return cached instances, and can return subtypes.

---

## Item 6 — Avoid Creating Unnecessary Objects
```java
// ❌ Creates a new String every time
String s = new String("hello");

// ✅ Reuses the string pool
String s = "hello";

// ❌ Auto-boxing in a loop
Long sum = 0L;
for (long i = 0; i < 1_000_000; i++) sum += i;

// ✅ Use primitives
long sum = 0L;
```

---

## Item 9 — Prefer try-with-resources over try-finally
```java
// ❌ Old style — resource may not close on exception
BufferedReader br = new BufferedReader(new FileReader(path));
try {
    return br.readLine();
} finally {
    br.close();
}

// ✅ Modern — guaranteed close
try (BufferedReader br = new BufferedReader(new FileReader(path))) {
    return br.readLine();
}
```

---

## Item 17 — Minimize Mutability
- Declare fields `final` by default
- Don't provide setters unless required
- Ensure exclusive access to mutable components

---

## Item 22 — Interfaces Only for Types
```java
// ❌ Constant interface anti-pattern
public interface PhysicalConstants {
    static final double BOLTZMANN_CONSTANT = 1.380_649e-23;
}

// ✅ Utility class with private constructor
public final class PhysicalConstants {
    private PhysicalConstants() {}
    public static final double BOLTZMANN_CONSTANT = 1.380_649e-23;
}
```

---

## Item 28 — Prefer Lists over Arrays
```java
// ❌ Arrays are covariant — runtime type errors
Object[] strings = new String[1];
strings[0] = 1; // throws ArrayStoreException at runtime

// ✅ Generics fail at compile time
List<String> strings = new ArrayList<>();
strings.add(1); // compile error
```

---

## Item 51 — Design Method Signatures Carefully
- Keep parameter count ≤ 4 (Sonar: ≤ 7 as MAJOR rule S107)
- Break up parameter lists with helper classes (parameter objects)
- Prefer interfaces over classes for parameter types

---

## Item 57 — Minimize Scope of Local Variables
- Declare where first used, not at top of block
- Initialize at point of declaration
- Prefer `for` loops over `while` for loop variables

---

## Item 64 — Refer to Objects by Interface
```java
// ❌ Tied to implementation
ArrayList<String> list = new ArrayList<>();

// ✅ Program to interface
List<String> list = new ArrayList<>();
```

---

## Item 69 — Use Exceptions Only for Exceptional Conditions
```java
// ❌ Using exceptions for flow control — extremely slow
try {
    int i = 0;
    while (true) array[i++].climb();
} catch (ArrayIndexOutOfBoundsException e) {}

// ✅ Normal loop
for (Mountain m : range) m.climb();
```

---

## Item 76 — Strive for Failure Atomicity
- Failing methods should leave objects in their prior state
- Check parameters before modifying state
- Use defensive copies for mutable inputs
