# <<NAME>>

## Should trigger

1. TRIGGER-1 (a <<LANG>> request the skill must load for, without naming it)
2. TRIGGER-2 (a <<LANG>> request the skill must load for, without naming it)
3. TRIGGER-3 (a <<LANG>> request the skill must load for, without naming it)
4. TRIGGER-4 (a <<LANG>> request the skill must load for, without naming it)
5. TRIGGER-5 (a <<LANG>> request the skill must load for, without naming it)
6. TRIGGER-6 (a <<LANG>> request the skill must load for, without naming it)
7. TRIGGER-7 (a <<LANG>> request the skill must load for, without naming it)
8. TRIGGER-8 (a <<LANG>> request the skill must load for, without naming it)
9. TRIGGER-9 (a <<LANG>> request the skill must load for, without naming it)
10. TRIGGER-10 (a <<LANG>> request the skill must load for, without naming it)

## Should NOT trigger

1. NOT-1 (an unrelated request, or a near miss that belongs to another skill)
2. NOT-2 (an unrelated request, or a near miss that belongs to another skill)
3. NOT-3 (an unrelated request, or a near miss that belongs to another skill)
4. NOT-4 (an unrelated request, or a near miss that belongs to another skill)
5. NOT-5 (an unrelated request, or a near miss that belongs to another skill)
6. NOT-6 (an unrelated request, or a near miss that belongs to another skill)
7. NOT-7 (an unrelated request, or a near miss that belongs to another skill)
8. NOT-8 (an unrelated request, or a near miss that belongs to another skill)
9. NOT-9 (an unrelated request, or a near miss that belongs to another skill)
10. NOT-10 (an unrelated request, or a near miss that belongs to another skill)

## Functional

**Wrong stack**
- Given: a project that is not <<LANG>>
- When: asked to build <<LANG>> code
- Then: it stops with a Blocked report and writes no code.

**Missing Python**
- Given: no `python3` on the machine
- When: the skill starts
- Then: it stops with a Blocked report that names `python3`. It does not fall back to searching files by hand.
