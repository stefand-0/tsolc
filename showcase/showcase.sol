// ============================================================
// Sol Showcase — Complete Language Feature Tour
// ============================================================
// This file demonstrates every feature of the Sol language.
// Run it: tsolc showcase.sol --run
// ============================================================

// ============================================================
// 1. STRUCTS
// ============================================================
// Define custom types with the `struct` keyword.
// Fields use C-style syntax: type name
// Blocks are indentation-based — no braces, no `end`.

struct Point
    float x
    float y

struct Person
    string name
    int age
    float height

// ============================================================
// 2. FUNCTIONS
// ============================================================
// Functions look like C but use `out` for return types.
// Omit `out` entirely for void functions.
// `pub` makes a function visible to other files via `get()`.

// A simple function with a return value
add(int a, int b) out int
    return a + b

// A void function — no `out` keyword
print_greeting(string name)
    out("Hello, %s!\n", name)

// Recursive function
factorial(int n) out int
    if (n <= 1)
        return 1
    return n * factorial(n - 1)

// Multiple parameters, multiple types
distance(float x1, float y1, float x2, float y2) out float
    float dx -> x2 - x1
    float dy -> y2 - y1
    // No sqrt() in stdlib yet — simplified for demo
    return dx + dy

// ============================================================
// 3. MAIN ENTRY POINT
// ============================================================
// Every program needs a `main()` function.
// Return an `int` — 0 means success.

main() out int
    // --------------------------------------------------------
    // 4. VARIABLE DECLARATION & TYPES
    // --------------------------------------------------------
    // Declare variables with: type name -> value
    // The `->` is Sol's assignment operator. It avoids
    // confusion between `=` (comparison) and assignment.

    int count -> 42
    int8 small -> 127
    int16 medium -> 32000
    int32 big -> 2000000000
    int64 huge -> 9223372036854775807

    uint8 usmall -> 255
    uint16 umedium -> 65535
    uint32 ubig -> 4294967295
    uint64 uhuge -> 18446744073709551615

    float pi -> 3.14
    double precise -> 2.718281828459045
    char letter -> 'A'
    bool flag -> true
    long lng -> 1234567890
    short shrt -> 30000
    byte byt -> 200

    // --------------------------------------------------------
    // 5. STRINGS
    // --------------------------------------------------------
    // `string` maps to C's `char*`.
    // Escape sequences work: \n for newline, \t for tab

    string msg -> "Hello from Sol!"
    string multiline -> "Line 1\nLine 2\tTabbed"

    // --------------------------------------------------------
    // 6. ARRAYS
    // --------------------------------------------------------
    // Arrays use `[]` syntax. The type is `elementType[]`.
    // Initialize with a compound literal: [1, 2, 3]

    int[] nums -> [10, 20, 30, 40, 50]
    float[] floats -> [1.1, 2.2, 3.3]

    // --------------------------------------------------------
    // 7. REASSIGNMENT
    // --------------------------------------------------------
    // Use `->` to change an existing variable's value.

    count -> 100
    pi -> 6.28
    flag -> false

    // --------------------------------------------------------
    // 8. ARITHMETIC OPERATORS
    // --------------------------------------------------------
    // Standard C operators: + - * / %

    int sum -> 10 + 20
    int diff -> 50 - 15
    int prod -> 6 * 7
    int quot -> 100 / 4
    int rem -> 17 % 5

    // --------------------------------------------------------
    // 9. UNARY OPERATORS
    // --------------------------------------------------------
    // Negation and logical NOT.

    int neg -> -sum
    bool inverted -> !flag

    // --------------------------------------------------------
    // 10. INCREMENT
    // --------------------------------------------------------
    // Postfix increment: variable++

    int counter -> 0
    counter++
    counter++

    // --------------------------------------------------------
    // 11. COMPARISON OPERATORS
    // --------------------------------------------------------
    // == != < <= > >= — same as C

    bool eq -> 5 == 5
    bool ne -> 5 != 3
    bool lt -> 3 < 5
    bool le -> 5 <= 5
    bool gt -> 10 > 5
    bool ge -> 10 >= 10

    // --------------------------------------------------------
    // 12. LOGICAL OPERATORS
    // --------------------------------------------------------
    // && for AND, || for OR

    bool and_test -> true && true
    bool or_test -> false || true
    bool complex -> (count > 50) && (pi < 10.0) || (counter == 2)

    // --------------------------------------------------------
    // 13. GUARD / TERNARY OPERATOR
    // --------------------------------------------------------
    // condition ? true_expr : false_expr
    // This is Sol's ternary operator — works anywhere
    // an expression is expected, including nested.

    string sign -> count > 0 ? "positive" : "non-positive"
    int abs_val -> neg < 0 ? -neg : neg

    // Nested ternary — grade calculator
    int score -> 85
    string grade -> score >= 90 ? "A" : score >= 80 ? "B" : score >= 70 ? "C" : score >= 60 ? "D" : "F"

    // Ternary in function arguments
    out("count is %s\n", count > 0 ? "positive" : "non-positive")

    // --------------------------------------------------------
    // 14. CONSOLE OUTPUT — out()
    // --------------------------------------------------------
    // `out("format", args...)` maps directly to C's printf.
    // Use standard printf format specifiers.

    out("=== Sol Showcase ===\n")
    out("count = %d\n", count)
    out("pi = %.2f\n", pi)
    out("precise = %.15f\n", precise)
    out("letter = %c\n", letter)
    out("flag = %d\n", flag)
    out("msg = %s\n", msg)
    out("counter after ++ = %d\n", counter)
    out("sign = %s\n", sign)
    out("abs_val = %d\n", abs_val)
    out("grade = %s\n", grade)

    // --------------------------------------------------------
    // 15. CONSOLE INPUT — in()
    // --------------------------------------------------------
    // `in(variable)` reads from stdin into the variable.
    // For strings, this currently uses scanf — be careful
    // with buffer overflow on long inputs.

    // Uncomment to test interactive input:
    // string username
    // out("Enter your name: ")
    // in(username)
    // out("Hello, %s!\n", username)

    // For demo purposes, we'll skip interactive input
    // and use a hardcoded value:
    string username -> "Sol Developer"
    out("Welcome, %s!\n", username)

    // --------------------------------------------------------
    // 16. CONTROL FLOW — if / elseif / else
    // --------------------------------------------------------
    // Indentation-based blocks. No braces, no `end`.
    // The block ends when indentation decreases.

    if (count > 50)
        out("count is greater than 50\n")
    elseif (count == 50)
        out("count equals 50\n")
    else
        out("count is less than 50\n")

    // Nested if statements
    if (flag)
        out("flag is true\n")
        if (counter > 0)
            out("counter is also positive\n")

    // Ternary-style conditionals in output
    out("count is %s\n", count > 50 ? "big" : count > 25 ? "medium" : "small")

    // --------------------------------------------------------
    // 17. FOR LOOPS
    // --------------------------------------------------------
    // C-style for loops: for (init; condition; increment)
    // All three parts are optional.

    // Standard counting loop
    out("Counting 0 to 4: ")
    for (int i -> 0; i < 5; i++)
        out("%d ", i)
    out("\n")

    // Loop with var declaration in init
    out("Counting 10 to 14: ")
    for (int j -> 10; j < 15; j++)
        out("%d ", j)
    out("\n")

    // Loop with assignment init (pre-declared variable)
    int k
    out("Counting 20 to 24: ")
    for (k -> 20; k < 25; k++)
        out("%d ", k)
    out("\n")

    // --------------------------------------------------------
    // 18. WHILE LOOPS
    // --------------------------------------------------------
    // Simple while loop with indentation-based block.

    int w -> 0
    out("While loop: ")
    while (w < 5)
        out("%d ", w)
        w++
    out("\n")

    // --------------------------------------------------------
    // 19. BREAK & CONTINUE
    // --------------------------------------------------------
    // `break` exits the loop. `continue` skips to next iteration.

    out("Break at 3: ")
    for (int n -> 0; n < 10; n++)
        if (n == 3)
            break
        out("%d ", n)
    out("\n")

    out("Skip evens: ")
    for (int p -> 0; p < 6; p++)
        if (p % 2 == 0)
            continue
        out("%d ", p)
    out("\n")

    // --------------------------------------------------------
    // 20. FUNCTION CALLS
    // --------------------------------------------------------
    // Call any function declared in the file (or imported).

    int add_result -> add(10, 20)
    out("add(10, 20) = %d\n", add_result)

    int fact_result -> factorial(5)
    out("factorial(5) = %d\n", fact_result)

    print_greeting("World")

    // --------------------------------------------------------
    // 21. STRUCT USAGE
    // --------------------------------------------------------
    // Declare struct variables, then set fields with `->`.
    // Access fields with dot notation: obj.field

    Point origin
    origin.x -> 0.0
    origin.y -> 0.0
    out("Point origin: (%.1f, %.1f)\n", origin.x, origin.y)

    Point p2
    p2.x -> 3.5
    p2.y -> 7.2
    out("Point p2: (%.1f, %.1f)\n", p2.x, p2.y)

    Person alice
    alice.name -> "Alice"
    alice.age -> 30
    alice.height -> 1.65
    out("Person: %s is %d years old, %.2f m tall\n", alice.name, alice.age, alice.height)

    // --------------------------------------------------------
    // 22. ARRAY INDEXING
    // --------------------------------------------------------
    // Access elements with [index]. Arrays are 0-indexed.

    out("nums[0] = %d, nums[2] = %d, nums[4] = %d\n", nums[0], nums[2], nums[4])
    nums[2] -> 99
    out("After nums[2] -> 99: nums[2] = %d\n", nums[2])

    // --------------------------------------------------------
    // 23. RAW C INJECTION — C -> "..."
    // --------------------------------------------------------
    // When Sol can't do something, drop straight to C.
    // The string is emitted verbatim into the generated C file.
    // Use this for includes, macros, or calling C libraries.

    C -> "// This comment was injected from Sol"
    C -> "int injected_var = 777;"
    out("injected_var = %d\n", injected_var)

    // --------------------------------------------------------
    // 24. RETURN
    // --------------------------------------------------------
    // Return a value from a function. For void functions,
    // `return` alone exits early.

    return 0

// ============================================================
// 25. VOID FUNCTIONS & EARLY RETURN
// ============================================================

// A void function with an early return
maybe_print(bool should_print, string msg)
    if (!should_print)
        return
    out("%s\n", msg)

// ============================================================
// 26. MULTIPLE PARAMETERS & COMPLEX LOGIC
// ============================================================

// Clamp a value between min and max
clamp(int val, int min_val, int max_val) out int
    return val < min_val ? min_val : val > max_val ? max_val : val

// Check if a number is even
is_even(int n) out bool
    return n % 2 == 0

// FizzBuzz — demonstrates loops, conditionals, and output
fizzbuzz(int max)
    for (int i -> 1; i <= max; i++)
        if (i % 15 == 0)
            out("FizzBuzz\n")
        elseif (i % 3 == 0)
            out("Fizz\n")
        elseif (i % 5 == 0)
            out("Buzz\n")
        else
            out("%d\n", i)