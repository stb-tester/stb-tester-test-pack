Test-pack
=========

This is an Stb-tester test-pack suitable for running on the Stb-tester
appliances.

Writing tests
-------------

Tests should be put in the `tests/` directory where they will be found by the
test-runner.  There is an example in there which may be deleted once you have
written your own tests.

See ["Write a new test case"] in the Stb-tester manual for more help.

["Write a new test case"]: http://stb-tester.com/manual/getting-started#write-a-new-test-case

Remote-control configuration
----------------------------

Infrared remote control configuration belongs in the `config/remote-control/`
directory. See ["Configuration files"] in the Stb-tester manual for details.

Once you have added your own remote control configurations you can delete the
examples from the `config/remote-control/` directory.

["Configuration files"]: http://stb-tester.com/manual/advanced-configuration#configuration-files

Choosing the stb-tester version to use
--------------------------------------

Stb-tester test-packs put you in control of which version of the Stb-tester
Python API to use, allowing you to upgrade to new releases in a controlled
manner. When a new version of Stb-tester is available, update the configuration
key `test_pack.stbt_version` in `config/stbt.conf`. See the
[Stb-tester manual][stbt-conf] for details.

[stbt-conf]: http://stb-tester.com/manual/advanced-configuration#stbt-conf
