# GH-License: Remaining Issues Implementation Plan

## Summary
This plan addresses the remaining open GitHub issues that were not fully implemented in the previous waves.

## Open Issues Status

### From Original Analysis:
- ✅ **#34** - Unit Tests - IMPLEMENTED (pytest infrastructure created)
- ✅ **#47** - Code Refactoring - IMPLEMENTED (modular structure)
- ✅ **#49** - GitHub API License Detection - IMPLEMENTED (uses GitHub API)
- ✅ **#50** - --show filter option - IMPLEMENTED
- ⚠️ **#59** - Search Other Branches - PARTIALLY IMPLEMENTED (GitHub OK, Bitbucket still hardcoded)
- ✅ **#68** - Asyncio Migration - IMPLEMENTED
- ❌ **#41** - Remove Bitbucket API Support - NOT IMPLEMENTED
- ❌ **Rate Limiting** - NOT IMPLEMENTED (was in original plan scope)

### Excluded from Original Plan:
- #19 - ScanCode-Toolkit integration
- #51 - Visual report generation

## Implementation Tasks

### Wave 1: Critical Fixes

#### Task 1: Fix Bitbucket Default Branch Detection (Issue #59 - Partial)
- **Description**: Bitbucket provider still hardcodes "master" instead of detecting the default branch dynamically
- **File**: `ghlicense/providers/bitbucket.py`
- **Expected Outcome**: Use Bitbucket API to get actual default branch name
- **Verification**: Check that `bitbucket.py` no longer has hardcoded "master"

#### Task 2: Implement Rate Limiting with Exponential Backoff
- **Description**: Add automatic retry with exponential backoff for API rate limits
- **Files**: Create `ghlicense/utils/retry.py`, update providers
- **Expected Outcome**: All API calls retry on rate limit with backoff (1s, 2s, 4s, 8s...)
- **Verification**: Test with rate limit simulation

### Wave 2: Cleanup (Optional)

#### Task 3: Remove Bitbucket Support (Issue #41)
- **Description**: Remove bitbucket-api support as requested in issue #41
- **Files**: Remove `ghlicense/providers/bitbucket.py`, update registration
- **Expected Outcome**: Bitbucket provider removed from codebase
- **Verification**: `ghlicense/providers/bitbucket.py` deleted, no Bitbucket references

## Guardrails
- Maintain backward compatibility with CLI interface
- No breaking changes without user confirmation
- Follow existing code patterns and style
- Add tests for new functionality

## Dependencies
- Task 1: Independent
- Task 2: Independent
- Task 3: Should be done after Tasks 1-2 if user confirms

## Success Criteria
- All remaining open issues addressed
- Code passes linting and tests
- No regression in existing functionality
- Documentation updated
