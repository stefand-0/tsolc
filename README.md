# tsolc
TSolC - The C transpiler for the Sol language.

> **Sol — Embrace modularity, ease of use, and speed.**

TSol is a lightweight scripting language that compiles to C. It gives you the raw performance of C with a cleaner, more modern syntax — and a module system that actually makes sense.

---

## Why Sol?

C is fast. C is everywhere. But C is also verbose, error-prone, and lacks a sane way to organize code across files.

**Sol fixes that.**

- **Modular by design** — `get("path/to/module.sol")` imports just work, including nested subdirectories
- **Familiar syntax** — C-style types and control flow, minus the footguns
- **Zero-cost abstraction** — transpiles to clean C, then compiles with clang or gcc
- **No build system headaches** — one command compiles and runs

---

## Install

```bash
pip install tsolc
```

Requires Python 3.10+ and a C compiler (clang, gcc, or cc).

---

## Quick Start

**hello.sol**
```sol
main() out int {
    string msg -> "Hello, World!";
    printf("%s\n", msg);
    return 0;
}
```

```bash
tsolc hello.sol --run
```

---

## Language Features

### Types

| Sol | C |
|-----|---|
| `int`, `float`, `double`, `char`, `bool` | Same |
| `string` | `char*` |
| `int8`–`int64`, `uint8`–`uint64` | `int8_t`–`int64_t`, `uint8_t`–`uint64_t` |
| `int[]`, `float[]`, ... | Pointer + compound literal |

### Variables & Assignment

```sol
int count -> 42;
float pi -> 3.14;
string name -> "Sol";
int[] nums -> [1, 2, 3, 4, 5];
```

Assignment uses `->` to avoid confusion with `==`:

```sol
count -> count + 1;
```

### Functions

```sol
pub square(int n) out int {
    return n * n;
}
```

- `pub` marks the function as public (importable from other files)
- `out type` specifies the return type; omit for `void`

### Imports

```sol
get("std/math.sol");
get("utils/helpers.sol");
```

Paths are relative to the importing file. Subdirectories work naturally:

```sol
get("std/io/file.sol");
get("../shared/types.sol");
```

Imports are deduplicated automatically — no header guards needed.

### Control Flow

```sol
if (x > 0) {
    printf("positive\n");
} elseif (x < 0) {
    printf("negative\n");
} else {
    printf("zero\n");
} end

for (int i -> 0; i < 10; i++) {
    printf("%d\n", i);
} end
```

### Structs

```sol
struct Point {
    float x;
    float y;
}
```

---

## Project Structure Example

```
myproject/
├── main.sol
├── std/
│   └── math.sol
└── utils/
    └── string.sol
```

**main.sol**
```sol
get("std/math.sol");
get("utils/string.sol");

main() out int {
    int result -> pow(2, 10);
    printf("2^10 = %d\n", result);
    return 0;
}
```

---

## CLI Usage

```bash
tsolc file.sol           # Compile only
tsolc file.sol --run     # Compile and run
tsolc file.sol --keep-c  # Keep the generated .c file
```

---

## How It Works

1. **Parse** — Sol source is tokenized and parsed into an AST
2. **Resolve** — `get()` imports are recursively resolved and merged
3. **Generate** — Clean C11 code is emitted (structs first, then forward declarations, then definitions)
4. **Compile** — clang/gcc compiles the C to a native executable
5. **Run** — The binary is executed (with `./` prefix and proper permissions on Unix)

---

## License

MIT — see [LICENSE](LICENSE) for details.