Test-pack
=========

This is an stb-tester test-pack suitable for running on the stb-tester
appliances.

Writing tests
-------------

Tests should be put in the `tests/` directory where they will be found by the
test-runner.  There is an example in there which may be deleted once you have
written your own tests.

Remote-control configuration
----------------------------

Proper remote control configuration belongs in the `config/remote-control/`.
It consists of:

1. `<name>.lircd.conf` - a LIRC configuration file which provides a mapping of
   key-name to IR code.  This can be created on your desktop using a [RedRat3
   IR tranciever][redrat] and the [RedRat IR Signal Database Utility][irdb]

2. `<name>.svg` - a image which will be displayed in the web-UI for this remote
   control.  This is a standard SVG which can be created using [inkscape], but
   with additional XML attributes.  Add the `key="KEY_NAME"` and `class="key"`
   attributes to the SVG elements which correspond to a particular key.
   stb-tester uses standard Linux key names such as `KEY_A`, `KEY_FASTFORWARD`,
   etc.  For a full list see [linux/input.h].

You can choose between different remote controls based on the filename you
choose.  Once you have added your own controls you can delete the examples from
the `config/remote-control` directory.

[redrat]: http://www.redrat.co.uk/products/index.html
[irdb]: http://www.redrat.co.uk/software/SignalDBUtil/index.html
[inkscape]: http://www.inkscape.org/
[linux/input.h]: http://lxr.free-electrons.com/source/include/linux/input.h

Choosing the stb-tester version to use
--------------------------------------

stb-tester test-packs put you in control of which version of the stb-tester
libraries and runner your tests run against.  When a new version of stb-tester
is available and you want to upgrade update the configuration key
`test_pack.stbt_version` in `config/stbt.conf`.
