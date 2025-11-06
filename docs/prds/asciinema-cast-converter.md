# PRD: Asciinema Cast File Converter

**Status**: ✅ Implemented
**Version**: 1.0
**Created**: 2025-11-05
**Author**: Product Team
**Implementation PR**: [#TBD](https://github.com/pbooth01/cli2ansible/pull/new/feature/asciinema-cast-converter)

---

## Executive Summary

Add the ability to parse asciinema `.cast` terminal recording files and convert them into human-readable JSON format. This enables developers and users to inspect terminal session recordings in a structured, searchable format without needing specialized tools.

## Problem Statement

### Current State
- Asciinema `.cast` files are in a specialized JSON-lines format that's difficult to read and analyze manually
- Users need to install asciinema tools just to inspect recording contents
- Terminal session data is opaque and not easily queryable
- No programmatic way to extract specific events or commands from recordings

### Pain Points
1. **Inspection Difficulty**: `.cast` files contain escape sequences, terminal control codes, and timestamps that make manual inspection challenging
2. **Tool Dependency**: Requires asciinema CLI to view recordings
3. **Analysis Friction**: Hard to extract specific commands or filter events programmatically
4. **Integration Gaps**: Cannot easily integrate recording data with other analysis tools

### Success Metrics
- Parse 100% of valid v2 and v3 asciinema format files
- Convert recordings to JSON with <1 second latency for typical files (< 1MB)
- 95%+ test coverage for parser code
- Zero critical security vulnerabilities

## Goals & Non-Goals

### Goals
✅ Parse asciinema v2 and v3 format `.cast` files
✅ Convert recordings to human-readable JSON with structured events
✅ Provide CLI tool for conversion
✅ Provide Makefile command for developer convenience
✅ Implement security controls (file size limits, event count limits)
✅ Achieve >95% test coverage
✅ Follow hexagonal architecture patterns

### Non-Goals
❌ Real-time streaming of terminal sessions
❌ Recording terminal sessions (only parsing existing files)
❌ Video playback or terminal emulation
❌ Editing or modifying `.cast` files
❌ Web UI for visualization (CLI-only for v1)
❌ Format conversion to other recording formats (VHS, ttyrec, etc.)

## User Stories

### Story 1: Developer Inspecting Test Recording
**As a** developer debugging a failed terminal automation test
**I want to** view the contents of a `.cast` recording as structured JSON
**So that** I can identify which commands failed and what output they produced

**Acceptance Criteria**:
- Can convert `.cast` file to JSON via CLI
- JSON includes timestamp, event type, data, and sequence number for each event
- Output is readable without special characters being escaped incorrectly
- Can save to file or view on stdout

### Story 2: DevOps Engineer Analyzing Session History
**As a** DevOps engineer reviewing terminal session logs
**I want to** extract all input commands from a recording
**So that** I can audit what commands were executed during an incident

**Acceptance Criteria**:
- Can parse large recordings (up to 10MB)
- Can filter events by type (input vs output)
- JSON output is searchable with standard tools (jq, grep)
- Performance is acceptable for batch processing

### Story 3: Security Auditor Reviewing Session Data
**As a** security auditor
**I want to** convert `.cast` files without exposing the system to security risks
**So that** I can safely analyze recordings from untrusted sources

**Acceptance Criteria**:
- Parser has file size limits to prevent DoS
- Parser has event count limits to prevent memory exhaustion
- No shell execution or arbitrary code execution
- Comprehensive error handling for malformed files

## Functional Requirements

### FR-1: Asciinema Format Support
**Priority**: P0 (Must Have)

Support parsing of asciinema format versions 2 and 3:
- Parse JSON header with metadata (version, terminal dimensions, timestamp, environment)
- Parse event lines with format: `[timestamp, event_type, data]`
- Support event types: `"i"` (input), `"o"` (output), `"x"` (exit code)
- Handle both integer and float timestamps
- Parse events regardless of line order (sort by timestamp)

**Technical Details**:
- Header: Single line JSON object with `version`, `term`, `timestamp`, `env` fields
- Events: One JSON array per line: `[float, string, string]`
- Exit events: `[float, "x", exit_code]` where exit_code may be omitted (defaults to "0")

### FR-2: JSON Output Format
**Priority**: P0 (Must Have)

Convert parsed events to clean JSON structure:
```json
[
  {
    "timestamp": 1.0,
    "event_type": "o",
    "data": "command output",
    "sequence": 0
  }
]
```

**Fields**:
- `timestamp`: Float (relative time in seconds from start)
- `event_type`: String ("i", "o", or "x")
- `data`: String (event payload)
- `sequence`: Integer (0-indexed sequential order)

**Output Requirements**:
- Pretty-printed with 2-space indentation
- UTF-8 encoding
- Exclude internal fields (session_id)
- Events sorted by timestamp
- Sequence numbers assigned after sorting

### FR-3: CLI Interface
**Priority**: P0 (Must Have)

Provide command-line interface:
```bash
# Output to stdout
python -m cli2ansible.cli convert-cast file.cast

# Output to file
python -m cli2ansible.cli convert-cast file.cast -o output.json
```

**Requirements**:
- Subcommand: `convert-cast`
- Positional argument: path to `.cast` file
- Optional flag: `-o/--output` for file output
- Help text with usage examples
- Exit codes: 0 (success), 1 (error)
- Error messages to stderr

### FR-4: Makefile Integration
**Priority**: P1 (Should Have)

Add `make convert-cast` command:
```bash
make convert-cast CAST_FILE=recording.cast [OUTPUT=output.json]
```

**Requirements**:
- Validate CAST_FILE is provided
- Show usage if CAST_FILE missing
- Support optional OUTPUT variable
- Use Poetry to run CLI tool

### FR-5: Input Validation
**Priority**: P0 (Must Have)

Comprehensive validation:
- ✅ UTF-8 encoding validation
- ✅ JSON syntax validation
- ✅ Header structure validation (must be object)
- ✅ Version validation (only v2, v3 supported)
- ✅ Event structure validation (must be array with 2-3 elements)
- ✅ Type validation for all fields (timestamp: number, event_type: string, data: string)
- ✅ Event type whitelist (only "i", "o", "x" allowed)
- ✅ Clear error messages with line numbers

## Non-Functional Requirements

### NFR-1: Performance
**Priority**: P0 (Must Have)

- Parse files up to 10MB within 5 seconds
- Memory usage proportional to file size (no >10x amplification)
- Linear time complexity O(n) where n = number of events
- Sorting overhead O(n log n) acceptable

### NFR-2: Security
**Priority**: P0 (Must Have)

**File Size Limits**:
- Default: 10MB maximum file size
- Configurable via parameter
- Check size before reading file into memory

**Event Count Limits**:
- Default: 100,000 events maximum
- Configurable via parameter
- Enforced during parsing loop

**Input Safety**:
- No shell execution
- No eval() or exec()
- Safe JSON parsing only (json.loads)
- Path traversal prevention for file operations

**Error Handling**:
- No stack traces exposed to users
- Error messages don't leak system paths
- Sensitive data warnings in documentation

### NFR-3: Code Quality
**Priority**: P0 (Must Have)

- Type hints on all functions (mypy compliance)
- 95%+ test coverage for new code
- Docstrings on all public functions
- Follow existing code style (ruff + black)
- Zero linting errors

### NFR-4: Architecture Compliance
**Priority**: P0 (Must Have)

- Implement `CapturePort` interface from domain layer
- Use existing `Event` domain model
- No direct dependencies on HTTP, database, or external services
- Parser is a pure adapter (outbound)
- CLI is a separate concern

### NFR-5: Documentation
**Priority**: P1 (Should Have)

- Inline code documentation (docstrings)
- CLI help text with examples
- Makefile help text
- Error messages that guide users
- Security warnings about sensitive data in recordings

## Technical Design

### Architecture

```
┌─────────────────────────────────────────────────┐
│                   CLI Layer                     │
│  (cli.py - User Interface)                      │
│  - Argument parsing                             │
│  - File I/O coordination                        │
│  - Output formatting                            │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│              Domain Layer                       │
│  (models.py - Business Objects)                 │
│  - Event dataclass                              │
│  - CapturePort interface                        │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│              Adapter Layer                      │
│  (asciinema_parser.py - Implementation)         │
│  - AsciinemaParser implements CapturePort       │
│  - Parse .cast file format                      │
│  - Validate and transform to Event objects      │
└─────────────────────────────────────────────────┘
```

### Class Design

**AsciinemaParser**
```python
class AsciinemaParser(CapturePort):
    def parse_events(
        self,
        recording_data: bytes,
        max_events: int = 100_000
    ) -> list[Event]:
        """Parse .cast file bytes into Event objects."""
        # 1. Decode UTF-8
        # 2. Validate header (v2/v3)
        # 3. Parse event lines
        # 4. Validate event structure
        # 5. Create Event objects
        # 6. Sort by timestamp
        # 7. Assign sequence numbers
        # 8. Return list
```

**Helper Functions**
```python
def parse_cast_file(
    file_path: str,
    session_id: UUID | None = None,
    max_file_size: int = 10 * 1024 * 1024
) -> list[Event]:
    """Convenience function for file parsing."""
    # 1. Validate file size
    # 2. Read file
    # 3. Call parser
    # 4. Override session_id if provided
    # 5. Return events
```

### Data Flow

```
.cast file → read_file() → bytes
    ↓
    validate_size() → ValueError if too large
    ↓
    parse_events() → decode UTF-8
    ↓
    validate_header() → ValueError if invalid
    ↓
    for each line:
        parse_event() → validate structure
        create Event() → append to list
    ↓
    sort_by_timestamp()
    ↓
    assign_sequence_numbers()
    ↓
    return list[Event]
```

### Error Handling Strategy

| Error Type | HTTP Status | Response | Recovery |
|------------|-------------|----------|----------|
| File not found | N/A (CLI) | "Error: File not found: {path}" | Exit code 1 |
| Invalid UTF-8 | N/A | "Error: Invalid UTF-8 encoding" | Exit code 1 |
| Invalid JSON | N/A | "Error: Invalid JSON on line {n}" | Exit code 1 |
| Unsupported version | N/A | "Error: Unsupported version {v}" | Exit code 1 |
| File too large | N/A | "Error: File size exceeds {max}MB" | Exit code 1 |
| Too many events | N/A | "Error: Event count exceeds {max}" | Exit code 1 |

## Implementation Plan

### Phase 1: Core Parser ✅
- [x] Create AsciinemaParser class
- [x] Implement parse_events() method
- [x] Add UTF-8 validation
- [x] Add JSON parsing with error handling
- [x] Implement header validation (v2/v3)
- [x] Implement event parsing loop
- [x] Add event structure validation
- [x] Add type validation
- [x] Implement timestamp sorting
- [x] Implement sequence number assignment

### Phase 2: Security Hardening ✅
- [x] Add file size limit (10MB)
- [x] Add event count limit (100K)
- [x] Add file size check in parse_cast_file()
- [x] Add event count check in parse_events()
- [x] Document security considerations

### Phase 3: CLI Tool ✅
- [x] Create cli.py module
- [x] Implement convert_cast_to_json() function
- [x] Add argparse with convert-cast subcommand
- [x] Add -o/--output flag
- [x] Implement stdout output
- [x] Implement file output
- [x] Add error handling and exit codes
- [x] Add help text with examples

### Phase 4: Developer Experience ✅
- [x] Add Makefile command
- [x] Move demo.cast to test fixtures
- [x] Add usage examples to help text
- [x] Test with real .cast files

### Phase 5: Testing ✅
- [x] Unit tests for AsciinemaParser (26 tests)
- [x] Unit tests for parse_cast_file() (6 tests)
- [x] Unit tests for CLI (16 tests)
- [x] Integration tests with demo.cast (7 tests)
- [x] Test coverage: 97% parser, 100% CLI

### Phase 6: Quality Assurance ✅
- [x] Security review (SecurityAgent)
- [x] Code formatting (black + ruff)
- [x] Linting (ruff)
- [x] Type checking (mypy)
- [x] All tests passing

## Test Strategy

### Unit Tests
**Parser Tests** (26 tests):
- Valid v2 and v3 format parsing
- Empty file handling
- Invalid UTF-8 handling
- Invalid JSON handling
- Unsupported version handling
- Header validation
- Event structure validation
- Type validation
- Event type validation
- Sorting behavior
- Empty line handling
- Exit event handling

**File Helper Tests** (6 tests):
- File reading success
- FileNotFoundError
- session_id override
- Invalid format handling
- Empty file handling
- Unicode handling

**CLI Tests** (16 tests):
- stdout output
- File output
- File not found error
- Invalid format error
- Pretty printing
- Field exclusion
- Help text
- Error messages

### Integration Tests
**End-to-End Tests** (7 tests):
- Parse real demo.cast fixture
- Validate structure
- Validate event types
- Validate commands
- Validate output
- Validate timestamp ordering
- Validate session_id override

### Coverage Goals
- Parser: 97% achieved ✅
- CLI: 100% achieved ✅
- Overall: 73% (new code brings average up)

## Security Considerations

### Threat Model

**Threat**: Denial of Service via Large Files
- **Mitigation**: 10MB file size limit
- **Status**: ✅ Implemented

**Threat**: Memory Exhaustion via Event Bomb
- **Mitigation**: 100K event count limit
- **Status**: ✅ Implemented

**Threat**: Command Injection
- **Mitigation**: No shell execution, safe JSON parsing only
- **Status**: ✅ Not vulnerable

**Threat**: Path Traversal (output files)
- **Mitigation**: CLI tool - user has filesystem access already
- **Risk**: Low (future consideration if exposing via API)
- **Status**: ⚠️ Documented

**Threat**: Sensitive Data Exposure
- **Mitigation**: Documentation warnings
- **Risk**: Medium (recordings may contain passwords/keys)
- **Status**: ⚠️ Documented, future encryption consideration

### Security Review Summary
- **Critical**: 0 findings
- **High**: 0 findings
- **Medium**: 2 findings (addressed with limits)
- **Low**: 1 finding (documented for future)
- **Info**: 1 finding (documentation added)

## Dependencies

### New Dependencies
None - uses only Python standard library:
- `json` - JSON parsing
- `sys` - CLI argument handling, exit codes
- `pathlib` - File path operations
- `argparse` - CLI argument parsing
- `uuid` - Session ID generation
- `os` - File size checking

### Existing Dependencies
- `cli2ansible.domain.models.Event` - Domain model
- `cli2ansible.domain.ports.CapturePort` - Interface

## Deployment Plan

### Rollout Strategy
1. ✅ Merge to `release-1.0.0` branch
2. ✅ Include in v1.0.0 release
3. Document in CHANGELOG.md
4. Update README.md with usage examples
5. No breaking changes - purely additive feature

### Rollback Plan
- Feature is isolated (new files only)
- Can be removed without affecting existing functionality
- No database migrations
- No API changes

## Success Metrics

### Quantitative Metrics
- ✅ **Test Coverage**: 97% for parser, 100% for CLI (Target: 95%)
- ✅ **Parse Success Rate**: 100% for valid v2/v3 files (Target: 100%)
- ✅ **Security Vulnerabilities**: 0 Critical/High (Target: 0)
- ⏳ **Usage Adoption**: TBD after release (Target: 10+ uses in first month)

### Qualitative Metrics
- ✅ Code review approval
- ✅ Architecture compliance
- ✅ Documentation completeness
- ⏳ User feedback positive (TBD after release)

## Future Enhancements

### v1.1 Potential Features
- **Format conversion**: Convert to other recording formats
- **Event filtering**: CLI flags to filter by event type
- **Time range extraction**: Extract events within time window
- **Command extraction**: Smart parsing of input events into full commands
- **Sanitization**: Remove sensitive data from recordings
- **Compression**: Compress/decompress .cast files

### v2.0 Considerations
- **API endpoint**: HTTP endpoint for conversion (requires auth)
- **Web UI**: Visual playback and inspection
- **Real-time streaming**: Parse streams instead of files
- **Advanced analytics**: Command frequency, session duration stats
- **At-rest encryption**: Encrypt stored recordings

## Open Questions

### Resolved
- ✅ Q: Should we support version 1 format?
  - A: No, v1 is deprecated. Only v2 and v3.

- ✅ Q: What file size limit is appropriate?
  - A: 10MB default (typical recordings are 100KB-2MB)

- ✅ Q: Should we filter sensitive data?
  - A: No in v1.0 - document the risk instead

- ✅ Q: CLI tool or Python API first?
  - A: Both - CLI for users, Python function for programmatic use

### Outstanding
- ⏳ Q: Should we add format validation warnings (e.g., suspiciously large gaps in timestamps)?
  - A: Defer to v1.1 based on user feedback

- ⏳ Q: Should we support piped input (stdin)?
  - A: Defer to v1.1 - add if users request it

## Appendix

### Example .cast File (v3)
```json
{"version":3,"term":{"cols":80,"rows":24},"timestamp":1234567890,"env":{"SHELL":"/bin/bash"}}
[0.021, "o", "$ "]
[1.234, "i", "echo"]
[1.456, "i", " "]
[1.678, "i", "hello"]
[2.000, "i", "\r"]
[2.050, "o", "hello\r\n"]
[2.100, "o", "$ "]
[3.000, "x", "0"]
```

### Example Converted JSON Output
```json
[
  {
    "timestamp": 0.021,
    "event_type": "o",
    "data": "$ ",
    "sequence": 0
  },
  {
    "timestamp": 1.234,
    "event_type": "i",
    "data": "echo",
    "sequence": 1
  },
  {
    "timestamp": 1.456,
    "event_type": "i",
    "data": " ",
    "sequence": 2
  },
  {
    "timestamp": 1.678,
    "event_type": "i",
    "data": "hello",
    "sequence": 3
  },
  {
    "timestamp": 2.0,
    "event_type": "i",
    "data": "\r",
    "sequence": 4
  },
  {
    "timestamp": 2.05,
    "event_type": "o",
    "data": "hello\r\n",
    "sequence": 5
  },
  {
    "timestamp": 2.1,
    "event_type": "o",
    "data": "$ ",
    "sequence": 6
  },
  {
    "timestamp": 3.0,
    "event_type": "x",
    "data": "0",
    "sequence": 7
  }
]
```

### References
- [Asciinema Format Documentation](https://github.com/asciinema/asciinema/blob/develop/doc/asciicast-v2.md)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Project Architecture Docs](../architecture/hexagonal-architecture.md)

---

**Document Status**: ✅ Complete (Retrospective)
**Last Updated**: 2025-11-05
**Next Review**: After v1.0.0 release feedback
