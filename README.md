Test-pack
=========

This is an Stb-tester test-pack suitable for running on the
[Stb-tester Platform].

Writing tests
-------------

Tests are Python functions in files under the `tests/` directory. See
`tests/roku.py` for some examples — feel free to delete it once you have
written your own tests.

See [Getting Started] in the Stb-tester manual for more help.

Choosing the stb-tester version to use
--------------------------------------

Changes to the `stbt` core Python API are version-controlled. You can specify
the version you want to use in `config/stbt.conf`. See
[`test_pack.stbt_version`][stbt-conf] in the the Stb-tester manual's
Configuration Reference.

We generally expect that upgrading to new versions will be safe; we strive to
maintain backwards compatibility. But there may be some edge cases that affect
some users, so this mechanism allows you to upgrade in a controlled manner, and
to test the upgrade on a branch first. Any incompatible changes are documented
in the [Release notes].


[Stb-tester Platform]: https://stb-tester.com/solutions
[Getting Started]: https://stb-tester.com/manual/getting-started#writing-testcases
[stbt-conf]: https://stb-tester.com/manual/advanced-configuration#stbt-conf
[Release notes]: https://stb-tester.com/manual/python-api#release-notes
