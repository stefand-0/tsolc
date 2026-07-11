// ============================================================
// Sol Showcase — Complete Language Feature Tour
// ============================================================

struct Point
    float x
    float y

struct Person
    string name
    int age
    float height

add(int a, int b) out int
    return a + b

print_greeting(string name)
    out("Hello, ")
    out(name)
    out("!\n")

factorial(int n) out int
    if n <= 1
        return 1
    return n * factorial(n - 1)

distance(float x1, float y1, float x2, float y2) out float
    float dx -> x2 - x1
    float dy -> y2 - y1
    return dx + dy

main() out int
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
    int flag -> 1
    long lng -> 1234567890
    short shrt -> 30000
    byte byt -> 200

    string msg -> "Hello from Sol!"
    string multiline -> "Line 1\nLine 2\tTabbed"

    int[] nums -> [10, 20, 30, 40, 50]
    float[] floats -> [1, 2, 3]

    count -> 100
    pi -> 6.28
    flag -> 0

    int sum -> 10 + 20
    int diff -> 50 - 15
    int prod -> 6 * 7
    int quot -> 100 / 4
    int rem -> 17 % 5

    int neg -> -sum
    int inverted -> !flag

    int counter -> 0
    counter++
    counter++

    int eq -> 5 == 5
    int ne -> 5 != 3
    int lt -> 3 < 5
    int le -> 5 <= 5
    int gt -> 10 > 5
    int ge -> 10 >= 10

    int and_test -> 1 && 1
    int or_test -> 0 || 1
    int complex -> (count > 50) && (pi < 10.0) || (counter == 2)

    string sign -> count > 0 ? "positive" : "non-positive"
    int abs_val -> neg < 0 ? -neg : neg

    int score -> 85
    string grade -> score >= 90 ? "A" : score >= 80 ? "B" : score >= 70 ? "C" : score >= 60 ? "D" : "F"

    out("=== Sol Showcase ===\n")
    out("count = ")
    C -> "printf(\"%d\", count);"
    out("\n")
    out("pi = ")
    C -> "printf(\"%.2f\", pi);"
    out("\n")
    out("grade = ")
    out(grade)
    out("\n")

    string username -> "Sol Developer"
    out("Welcome, ")
    out(username)
    out("\n")

    if count > 50
        out("count is greater than 50\n")
    elseif count == 50
        out("count equals 50\n")
    else
        out("count is less than 50\n")

    if flag
        out("flag is true\n")
        if counter > 0
            out("counter is also positive\n")

    out("Counting 0 to 4: ")
    for int i -> 0; i < 5; i++
        C -> "printf(\"%d \", i);"
    out("\n")

    out("Counting 10 to 14: ")
    for int j -> 10; j < 15; j++
        C -> "printf(\"%d \", j);"
    out("\n")

    int k
    out("Counting 20 to 24: ")
    for k -> 20; k < 25; k++
        C -> "printf(\"%d \", k);"
    out("\n")

    int w -> 0
    out("While loop: ")
    while w < 5
        C -> "printf(\"%d \", w);"
        w++
    out("\n")

    out("Break at 3: ")
    for int n -> 0; n < 10; n++
        if n == 3
            break
        C -> "printf(\"%d \", n);"
    out("\n")

    out("Skip evens: ")
    for int p -> 0; p < 6; p++
        if p % 2 == 0
            continue
        C -> "printf(\"%d \", p);"
    out("\n")

    int add_result -> add(10, 20)
    out("add(10, 20) = ")
    C -> "printf(\"%d\", add_result);"
    out("\n")

    int fact_result -> factorial(5)
    out("factorial(5) = ")
    C -> "printf(\"%d\", fact_result);"
    out("\n")

    print_greeting("World")

    Point origin
    origin.x -> 0.0
    origin.y -> 0.0
    out("Point origin: (")
    C -> "printf(\"%.1f, %.1f\", origin.x, origin.y);"
    out(")\n")

    Point p2
    p2.x -> 3.5
    p2.y -> 7.2
    out("Point p2: (")
    C -> "printf(\"%.1f, %.1f\", p2.x, p2.y);"
    out(")\n")

    Person alice
    alice.name -> "Alice"
    alice.age -> 30
    alice.height -> 1.65
    out("Person: ")
    out(alice.name)
    out(" is ")
    C -> "printf(\"%d\", alice.age);"
    out(" years old, ")
    C -> "printf(\"%.2f\", alice.height);"
    out(" m tall\n")

    out("nums[0] = ")
    C -> "printf(\"%d\", nums[0]);"
    out(", nums[2] = ")
    C -> "printf(\"%d\", nums[2]);"
    out(", nums[4] = ")
    C -> "printf(\"%d\", nums[4]);"
    out("\n")

    nums[2] -> 99
    out("After nums[2] -> 99: nums[2] = ")
    C -> "printf(\"%d\", nums[2]);"
    out("\n")

    C -> "// This comment was injected from Sol"
    C -> "int injected_var = 777;"
    out("injected_var = ")
    C -> "printf(\"%d\", injected_var);"
    out("\n")

    return 0

maybe_print(int should_print, string msg)
    if !should_print
        return
    out(msg)
    out("\n")

clamp(int val, int min_val, int max_val) out int
    return val < min_val ? min_val : val > max_val ? max_val : val

is_even(int n) out int
    return n % 2 == 0

fizzbuzz(int max)
    for int i -> 1; i <= max; i++
        if i % 15 == 0
            out("FizzBuzz\n")
        elseif i % 3 == 0
            out("Fizz\n")
        elseif i % 5 == 0
            out("Buzz\n")
        else
            C -> "printf(\"%d\", i);"
            out("\n")