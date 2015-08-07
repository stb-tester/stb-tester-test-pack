Test-pack
=========

This is an stb-tester test-pack suitable for running on the stb-tester
appliances.

Writing tests
-------------

Tests should be put in the `tests/` directory where they will be found by the
test-runner.  There is an example in there which may be deleted once you have
written your own tests.

See the [stb-tester ONE manual][write-a-new-test-case] for more help.

[write-a-new-test-case]: http://stb-tester.com/stb-tester-one/rev2015.1/getting-started#write-a-new-test-case

Remote-control configuration
----------------------------

Infrared remote control configuration belongs in the `config/remote-control/`
directory. See the [stb-tester ONE manual][configuration-files] for details.

Once you have added your own remote control configurations you can delete the
examples from the `config/remote-control` directory.

[configuration-files]: http://stb-tester.com/stb-tester-one/rev2015.1/advanced-configuration#configuration-files

Choosing the stb-tester version to use
--------------------------------------

stb-tester test-packs put you in control of which version of the stb-tester
libraries and runner your tests run against. When a new version of stb-tester
is available and you want to upgrade update the configuration key
`test_pack.stbt_version` in `config/stbt.conf`. See the
[stb-tester ONE manual][stbt-conf] for details.

[stbt-conf]: http://stb-tester.com/stb-tester-one/rev2015.1/advanced-configuration#stbt-conf
