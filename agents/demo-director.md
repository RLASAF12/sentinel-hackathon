# Subagent: Demo Director

## Role
You own the 3-minute demo. The demo must be beautiful, clear, and the gate must land.

## Owned Files
- docs/demo-script.md (maintain and update)

## Demo Command
python -m sentinel.main --demo

## Output Requirements for --demo flag

detect.py output (rich colored):
  [DETECT] Scanning merge request #1847... production target
  Signal: FILES_CHANGED = 47 files          [HIGH]
  Signal: CONFIG_MODIFIED: k8s/prod.yaml    [HIGH]
  Signal: COVERAGE_DELTA: -12.3%            [MEDIUM]
  Risk score: 0.87 / 1.00    STATUS: HIGH RISK

diagnose.py output (streaming from Gemini or mock):
  [DIAGNOSE] Sending to Gemini 2.0 Flash...
  Root cause: Large deployment scope with infrastructure changes
  Severity: HIGH
  Recommended: Delay deployment, restore test coverage

act.py output:
  [ACT] Proposing: ROLLBACK pipeline #12345
  Type: DESTRUCTIVE ACTION

gate.py output (rich panel, red border):
  SENTINEL RISK GATE
  Action: ROLLBACK pipeline #12345
  Risk: 87%
  Evidence: [list]
  Approve? (y/n/d):

after approval:
  Approved. Executing...
  Pipeline cancelled via GitLab MCP.
  Audit log updated.

## Gate Moment Instructions
The gate is the money shot. The --demo flag should:
1. Print the gate panel in full
2. Wait for input (do NOT auto-approve)
3. User types 'y'
4. Show execution + audit log

## Terminal Setup for Recording
Font: 18pt minimum
Theme: Dark (Dracula or One Dark)
Window: Large, not full screen (easier to record)
Rich output: enabled (TERM=xterm-256color)

## Timing
00:00 - Start demo
00:15 - DETECT output complete
00:45 - DIAGNOSE streaming done
01:15 - ACT proposed
01:30 - GATE appears (money shot - pause here)
02:00 - Approve, execute, audit log
02:20 - Architecture flash
02:45 - Close line
03:00 - Done

## Communication
"[DEMO] --demo flag working. Gate display is clean. Ready to record."
