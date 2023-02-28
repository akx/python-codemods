# python-codemods

A collection of Python codemods

## no_assert_codemod.py

This is a [libCST](https://github.com/Instagram/LibCST/) codemod that rewrites
`assert X` assertions into `if not X: raise AssertionError("X")`.

### Usage

```
python -m libcst.tool codemod no_assert_codemod.RewriteAssertToIfRaise ...py
```

## rtype_codemod.py

This is a [libCST](https://github.com/Instagram/LibCST/) codemod that rewrites
`:rtype:` and `:type:` docstring comments into real annotations.

