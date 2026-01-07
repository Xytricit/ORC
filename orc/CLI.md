# ORC CLI – v1 Command Reference

ORC is a static analysis tool focused on detecting dead / unused code and mapping code structure.
All commands are deterministic and non-interactive unless explicitly stated.

---

## 1. `orc analyse`

Analyse the entire codebase.

### What it does
- Parses all source files
- Builds dependency and call graphs
- Detects dead / unused code
- Assigns stable IDs to findings

### Usage
```bash
orc analyse
```

### Options

```bash
orc analyse --file <file-name>
```

Example:

```bash
orc analyse --file src/main.py
```

---

## 2. `orc dead`

Show dead / unused code.

### Usage

```bash
orc dead
```

### Options

```bash
orc dead --unused
```

### Output example

```
[D-12] src/utils/legacy_math.py
[D-19] function oldScoreCalc()
```

### Finding IDs

* `D` = Dead code
* Number = internal finding identifier

IDs are used for explain, delete, and ignore commands.

---

## 3. `orc delete`

Delete dead code (explicit action).

### Usage

```bash
orc delete
```

### Examples

```bash
orc delete --unused
orc delete D-12
orc delete --safe-only
```

### Rules

* Only deletes DEAD code
* Never deletes ignored code
* Requires confirmation unless `--yes` is used

Example:

```bash
orc delete D-12 --yes
```

---

## 4. `orc explain <id>`

Explain a single finding.

### Usage

```bash
orc explain D-12
```

### Output example

```
File src/utils/legacy_math.py is unused.
Reason:
- No imports detected
- No dynamic references
```

This command explains **why** a finding exists.
It does not suggest changes.

---

## 5. `orc ignore <id | path>`

Ignore code permanently.

### Usage

```bash
orc ignore D-12
orc ignore src/experimental/*
```

Ignored items:

* Are excluded from future analyses
* Are stored in `.orcrc`

---

## 6. `orc init`

Create an ORC configuration file.

### Usage

```bash
orc init
```

### Output

Creates a `.orcrc` file in the project root.

Example:

```yaml
ignore:
  - src/experimental/*
dynamic_patterns:
  - eval
  - reflection
```

---

## 7. `orc config`

View or modify ORC configuration.

### Usage

```bash
orc config show
orc config add ignore src/tmp/*
orc config add dynamic eval
```

Purpose:

* Manage ignore rules
* Define dynamic usage patterns
* Avoid manual config editing

---

## Notes

* `orc analyse` must be run before `dead`, `delete`, or `explain`
* ORC does not modify code unless `orc delete` is explicitly used
* All actions are deterministic and reproducible

---

End of v1 CLI specification.