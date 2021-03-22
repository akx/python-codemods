# python-codemods

A collection of Python codemods

## fixit_rewrite_asserts.py

This is a [Fixit](http://github.com/instagram/Fixit/) custom rule
that rewrites `assert X` assertions into `if not X: raise AssertionError("X")`.

## rtype_codemod.py

This is a [libCST](https://github.com/Instagram/LibCST/) codemod that rewrites
`:rtype:` and `:type:` docstring comments into real annotations.

