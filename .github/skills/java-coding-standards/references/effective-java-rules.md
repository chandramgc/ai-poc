# Effective Java (Joshua Bloch) Key Rules Reference

This guide summarizes critical software engineering principles adapted from *Effective Java* (3rd Edition) for this project's code review process.

---

## 1. Creating and Destroying Objects

### Item 1: Consider static factory methods instead of constructors
Static factories have distinct names, do not require creating a new object on every invocation, and can return subtype instances.
```java
// Prefer:
Boolean value = Boolean.valueOf(true);
```

### Item 2: Consider a builder when faced with many constructor parameters
Use builders to prevent constructors with long lists of optional arguments. This increases readability and maintains immutable states.
```java
Order order = new Order.Builder()
    .productId("P100")
    .quantity(2)
    .build();
```

### Item 3: Enforce the singleton property with a private constructor or an Enum
Prefer using single-element Enum types to implement Singletons as they provide serialization and thread safety out of the box.

### Item 4: Enforce noninstantiability with a private constructor
Utility classes (classes containing only static methods/fields) must not be instantiable. Document this with an empty private constructor.
```java
public class StringUtils {
    private StringUtils() {
        throw new AssertionError("Utility class noninstantiable");
    }
}
```

---

## 2. Methods Common to All Objects

### Item 10: Obey the general contract when overriding `equals`
Ensure equivalence relations: reflexive, symmetric, transitive, consistent, and null-safe. Override `hashCode` whenever you override `equals` (Item 11).

### Item 12: Always override `toString`
Provide clean, informative representations of object properties to help with debugging and logging.

### Item 14: Consider implementing `Comparable`
If a class represents a value with a natural ordering, implement `Comparable` to make it compatible with sorted collections.

---

## 3. Classes and Interfaces

### Item 15: Minimize the accessibility of classes and members
Make elements private by default, and expose them only when necessary. This separates APIs from internal implementations.

### Item 17: Minimize mutability
Immutable classes are simpler to design, thread-safe, and can be shared freely. Follow these rules:
1. Don't provide methods that modify state (mutators).
2. Ensure the class cannot be extended (declare class `final`).
3. Make all fields `final` and `private`.
4. Prevent clients from obtaining references to mutable components.

### Item 18: Favor composition over inheritance
Inheritance breaks encapsulation because a subclass depends on the implementation details of its superclass. Use wrapper classes instead.

---

## 4. Generics & Collections

### Item 26: Don't use raw types
Using raw types (e.g. `List` instead of `List<String>`) bypasses compile-time type safety and causes runtime exceptions.

### Item 28: Prefer lists to arrays
Arrays are covariant and reified (type checks at runtime); generics are invariant and erased (type checks at compile time). Use `List` to catch errors early.

---

## 5. Methods

### Item 49: Check parameters for validity
Validate parameters at the start of a method. Catch violations quickly and throw appropriate exceptions (e.g., `NullPointerException`, `IllegalArgumentException`).

### Item 54: Return empty arrays or collections, not nulls
Returning `null` instead of an empty collection forces the caller to write null-checking boilerplate and increases the risk of NullPointerExceptions.

---

## 6. General Programming

### Item 57: Minimize the scope of local variables
Declare local variables where they are first used, and initialize them immediately.

### Item 59: Know and use the libraries
Leverage standard APIs (e.g. `java.util.concurrent`, `java.util.Objects`, Stream API) rather than rolling your own custom utility classes.

### Item 60: Avoid float and double if exact answers are required
Use `BigDecimal`, `int`, or `long` for monetary calculations; float and double are designed for scientific calculations.

---

## 7. Exceptions

### Item 72: Favor the use of standard exceptions
Reuse built-in runtime exceptions:
- `IllegalArgumentException`: Parameter value is inappropriate.
- `IllegalStateException`: Object state is inappropriate for method call.
- `NullPointerException`: Parameter value is null when prohibited.
- `IndexOutOfBoundsException`: Index parameter is out of range.

### Item 73: Throw exceptions appropriate to the abstraction
Catch lower-level exceptions and throw custom higher-level exceptions (Exception Translation) to maintain API purity.
