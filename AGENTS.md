These are test scripts written in Python (3.10) using the Stb-tester Python API. They are used to automate testing of Set-top box (STB) applications. The tests run on a device that captures the STB screen over HDMI and simulates remote-control key presses.

The `stbt` package lets the test scripts analyze captured frames using image processing and OCR, and simulate remote-control key presses. See https://stb-tester.com/manual/python-api for the Python API reference documentation.

When editing or adding code, prefer the existing page-object patterns in this repository over inventing new abstractions.

Key rules
---------

Whatever you're doing:

- NEVER use `time.sleep`. Wait for the device with `stbt.wait_until` or `stbt.press_and_wait`.

**When writing test scripts** (see "Test scripts" below):

- Drive the app only through page objects; NEVER call `stbt.match`, `stbt.ocr`, or other image-processing functions directly from a test.
- Make assertions with the plain `assert` statement.
- The current page object should be stored in a variable named `page`, and updated whenever the page changes.

**When writing or editing page objects** (see "Page objects" below):

- **Verify against real frames.** You cannot see the STB screen, so don't guess: after writing or changing a page object, run it against captured frames using the objrepo MCP tools (see "Developing and verifying page objects") and confirm the output before considering the work done. Never declare success without running it.
- Inside a property, ALWAYS pass `frame=self._frame` to any `stbt` function you call.
- Properties MUST be pure functions of `self._frame`: NEVER call `stbt.press`, `stbt.get_frame`, `stbt.wait_until`, or anything else with side effects inside a property.
- A method that changes what's on screen MUST return a new page object rather than mutating `self`.
- Do NOT invent `stbt.Region` coordinates or reference-image filenames. Coordinates come from the debug tooling and captured screenshots; reference images (e.g. `settings-icon.png`) are crops of real captured frames saved next to the page object — create them from a real screenshot, don't fabricate the code that uses them.

Directory structure
-------------------

The directory structure is as follows:

    tests/
        appletv/
            pages/
                home/
                    home.py
                    __init__.py
                settings/
                    settings.py
                    settings-icon.png
                    __init__.py
                __init__.py
            __init__.py
            tests.py
            more_tests.py
        bbc_iplayer/
            ...
        __init__.py
    ai/
        is_visible/
            training/
                appletv/
                    Home/
                        2026-03-11_15.30.00Z.jpg
                        ...
    selftest/
        screenshots/
            appletv/
                Home/
                    2026-03-11_15.30.00Z-012345.png
                    2026-03-11_15.30.00Z-012345.png.conf
                    ...
    config/
        remote_control/
            Example.lircd.conf
            Example.svg
        stbt.conf
        test-farm/
            stb-tester-012345678901.conf
            ...

tests/ is a python package (it contains an __init__.py file).  The test code for each application is contained in its own subdirectory (app1, app2, etc.).  Directly under that are test scripts and a pages/ subdirectory containing page object classes (see "Page objects" below).

config/ contains configuration files for stb-tester.  See https://stb-tester.com/manual/configuration for details.

Page objects
------------

Each application subdirectory contains a `pages/` subdirectory that contains page object classes representing different screens/pages of the application. For example `tests/appletv/pages/home/home.py` contains a Home class that represents the home screen of the Apple TV app. These page objects encapsulate the logic for extracting information from the screen and interacting with UI elements.  Page objects inherit from the `stbt.FrameObject` class provided by the Stb-tester Python API.

The `stbt.FrameObject` class provides a `self._frame` attribute that represents a captured frame from the STB which is captured when the page object is instantiated.  The page object can use this frame to locate UI elements and extract information.

The truthiness of a `FrameObject` indicates whether the page is currently displayed on the screen. `stbt.FrameObject` implements this in the base class using AI, which allows tests to wait for a page to appear with `stbt.wait_until(PageObjectClass)`.  The `is_visible` AI training material can be found under `ai/is_visible/training/{app}/{classname}/*.jpg`. Where the AI `is_visible` model is not sufficient it can be implemented on the page object class.

Each extracted UI element should correspond to a property of the page object.

A complete page object typically looks like this. It represents the Apple TV home screen — a horizontal row of app icons — and shows the conventional properties (`focus`, `focus_region`) and navigation methods (`launch`, `navigate_to`):

```python
import stbt


class Home(stbt.FrameObject):
    """The Apple TV home screen: a horizontal row of app icons."""

    # `is_visible` (and therefore truthiness) is provided automatically by
    # the AI model, using the training material under
    # ai/is_visible/training/appletv/Home/. Define it explicitly only when
    # the AI model isn't reliable enough, for example:
    #
    #     @property
    #     def is_visible(self) -> bool:
    #         return bool(stbt.match("home-logo.png", frame=self._frame))

    @property
    def focus_region(self) -> stbt.Region:
        # The focused icon moves as the user navigates, so find it in the
        # frame rather than hard-coding coordinates. Here we diff against a
        # full-frame screenshot of the same screen with nothing focused
        # (home-no-selection.png, stored next to this file); the region that
        # differs is the selection.
        return stbt.find_selection_from_background(
            "home-no-selection.png", max_size=(400, 200),
            frame=self._frame).region

    @property
    def focus(self) -> str:
        return stbt.ocr(frame=self._frame,
                        region=self.focus_region,
                        mode=stbt.OcrMode.SINGLE_LINE)

    @staticmethod
    def launch() -> "Home":
        stbt.press("KEY_HOME")
        page = stbt.wait_until(Home)
        assert page, "Home screen did not appear after KEY_HOME"
        return page

    def navigate_to(self, focus: str) -> "Home":
        """Move the focus to the named app icon and return the new page."""
        return stbt.navigate_1d(focus, self, stbt.Direction.HORIZONTAL)
```

### Common types

These types appear throughout the `stbt` API:

- `stbt.Region(x, y, width=w, height=h)`: A rectangular area of a frame. Has `.x`, `.y`, `.width`, `.height`, `.right`, `.bottom`. `stbt.Region.ALL` means the whole frame.  Regions have a set of methods for combining and manipulating them (e.g. `.above()`, `.below()`, `Region.bounding_box()`, etc.). which should be preferred over manually calculating coordinates.  A `Region` is also a valid mask.
- `stbt.Direction.HORIZONTAL` / `stbt.Direction.VERTICAL`: passed to `stbt.navigate_1d` and `stbt.segment`.
- `stbt.OcrMode`: the OCR page-segmentation mode. Commonly `stbt.OcrMode.SINGLE_LINE` (a single line of text), `stbt.OcrMode.SINGLE_WORD`, or the default `stbt.OcrMode.DEFAULT`.
- `stbt.Color` / hex strings like `"#RRGGBB"`: colors passed to `stbt.find_regions_by_color` and similar.
- `stbt.Frame`: a captured video frame (a numpy image). You get one as `self._frame`.

### Properties

Information extraction should be performed in properties using the `stbt` API.  Each property must be a pure function of `self._frame` and should not have side effects.  This means passing `frame=self._frame` to any `stbt` functions used in the property.  Typically properties will use these APIs provided by the `stbt` module:

- `stbt.ocr(*, frame: stbt.Frame, region: stbt.Region, mode: stbt.OcrMode = stbt.OcrMode.DEFAULT) -> str`: Performs OCR on the given region of the frame and returns the extracted text.
- `stbt.match(image: Image | str, *, frame: stbt.Frame, region: stbt.Region | None = stbt.Region.ALL) -> stbt.MatchResult`: Looks for the image in the given frame and region, and returns a MatchResult which is truthy if a match was found and has a region attribute giving the location of the match.  The image parameter is typically a file path to a reference image stored in the page object's directory.
- `stbt.find_regions_by_color(color: stbt.Color | str, *, frame: stbt.Frame, mask: stbt.Region | stbt.Mask | None = stbt.Region.ALL, min_size: tuple[int, int] | None = (20, 20), max_size: tuple[int, int] | None = None) -> List[stbt.Region]`: Finds regions in the given frame and region that match the given color and returns a list of matching regions. Color is typically a hex color string like `"#RRGGBB"`.
- `stbt.find_selection_from_background(image: Image | str | stbt.Color, max_size: tuple[int, int], *, frame: stbt.Frame, mask: stbt.Region | stbt.Mask | None = stbt.Region.ALL, min_size: tuple[int, int] | None = None) -> FindSelectionFromBackgroundResult`: Given a background color or image, find the region that differs from the background.  The result will be falsey if the differences exceed `max_size`.  The result has a `region` attribute giving the location of the differing region.
- `stbt.segment(frame: stbt.Frame, *, region: stbt.Region | None = stbt.Region.ALL, initial_direction: stbt.Direction, steps: int = 1, narrow: bool = True, light_background: bool = False) -> List[stbt.Region]`: Segments the given region of the frame into sub-regions using an adaptive threshold.  initial_direction indicates whether to segment horizontally or vertically on the first pass and must be provided.  The result is a list of regions representing the segments found.

Verify these properties against captured frames using the objrepo MCP tools — see "Developing and verifying page objects" below.

### Methods

Navigation and other interactions should be implemented as methods on the page object.  These methods should return new page objects representing the resulting page after the interaction.  Typically these will be implemented in terms of these APIs provided by the `stbt` module:

- `stbt.press(key: str) -> stbt.Keypress`: Simulates pressing a key on the STB remote control.
- `stbt.press_and_wait(key: str, mask: stbt.Mask | stbt.Region = stbt.Region.ALL) -> stbt.Transition`: Presses a key and waits until the screen changes, and then stops changing.
- `stbt.wait_until(callable_: Callable[..., T]) -> T | None`: Waits until the given callable returns a truthy value, and then returns that value.
- `stbt.wait_for_motion(mask: stbt.Mask | stbt.Region = stbt.Region.ALL)`: Waits until motion is detected in the given region.
- `stbt.wait_for_content_start(*, mask: stbt.Mask | stbt.Region = stbt.Region.ALL, spinner_fn: Callable[[stbt.Frame], bool])`: Waits until content starts playing in the given region.
- `stbt.navigate_1d(target: str, page: stbt.FrameObject, direction: stbt.Direction, *, mask: stbt.Mask | stbt.Region = stbt.Region.ALL) -> Self`: Navigates a horizontal or vertical menu to the target item.  The returned page object represents the page after navigation and will have the .focus property set to the target item.
- `stbt.navigate_grid(target: str, page: stbt.FrameObject, *, mask: stbt.Mask | stbt.Region = stbt.Region.ALL) -> Self`: Navigates a grid menu to the target item.  The returned page object represents the page after navigation and will have the .focus property set to the target item.
- `stbt.Keyboard`: A class that assists typing on an on-screen keyboard.  See https://stb-tester.com/manual/keyboard for details.

### Standard methods and properties

Conventionally each frame object should provide the following methods if applicable:

- `@staticmethod launch()`: A method to navigate to this page from anywhere in the app.
- `@property focus(self) -> str`: A property that returns the name of the currently focused UI element on this page.  Typically this will use OCR based on `self.focus_region`.
- `@property focus_region(self) -> stbt.Region`: A property that returns the region of the screen corresponding to the currently focused UI element on this page.
- `navigate_to(self, focus: str) -> Self`: A method that navigates to the given focusable UI element on this page, and returns a new instance of the page object.  The focus parameter should be one of the values returned by the `focus` property.  This will typically use either the `stbt.navigate_1d` or `stbt.navigate_grid` functions.

### Developing and verifying page objects

You cannot see the STB screen, so you must verify your page objects against real captured frames using the MCP tools. Follow this loop whenever you write or change a page object:

1. Write (or edit) the page object class.
2. Run it against previously captured frames with the `run_object_repository` MCP tool, and check that every property returns the expected value (including that `is_visible` is true on frames where the page is showing and false on frames where it isn't).
3. If a property is wrong, use the `objrepo_debug` MCP tool to inspect detailed logging and visualizations for that property, then fix it.
4. Repeat until the output is correct on all the frames.

Do not consider a page object finished until you have run it against real frames and confirmed its output. Inspect the MCP tools' own descriptions for their exact usage.

Test scripts
------------

Test scripts are typically contained in a `tests.py` file in the application subdirectory, but may be in other files as well (e.g., `more_tests.py`) depending on how the tests are organized.  A test case consists of a python function whose name starts with `test_`.  Stb-tester will run these test functions using pytest.

Test scripts typically use the page objects to interact with the application, and will make assertions about the expected behaviour.  Test scripts should not directly use the image processing functions in `stbt` API.  Instead they should use the page objects to encapsulate the logic for interacting with the application.

Assertions should be made using the standard `assert` statement.

Conventionally a test script will have a `page` variable that represents the current page object.  The test script will navigate through the application by calling methods on the page object, and updating the `page` variable to the returned page object.

### Example test script

```python
import stbt


from tests.appletv.pages.home.home import Home
from tests.youtube.pages.home.home import Home as YouTubeHome


def test_launch_youtube():
    page = Home.launch()
    page = page.navigate_to("YouTube")
    assert page.focus == "YouTube"
    result = stbt.press_and_wait("KEY_OK")
    assert result, "Failed to launch YouTube app"
    print("Time to launch YouTube:", result.duration)

    page = YouTubeHome()
    assert page, "Failed to launch YouTube app"
```

Controlling the STB
-------------------

Stb-tester key names match the Linux input event key codes.  For example:

* KEY_HOME
* KEY_UP
* KEY_DOWN
* KEY_LEFT
* KEY_RIGHT
* KEY_OK
* KEY_BACK
* KEY_MENU
* KEY_PLAYPAUSE
* KEY_STOP
* KEY_FASTFORWARD
* KEY_REWIND
* KEY_GUIDE
* KEY_NETFLIX

Stb-tester provides these functions to control the STB:

- `stbt.press(key: str)`: Simulates pressing a key on the STB remote control.
- `stbt.pressing(key: str)`: Context manager to simulate holding down a key.
- `stbt.press_and_wait(key: str, mask: stbt.Mask | stbt.Region = stbt.Region.ALL)`: Presses a key and waits until the screen changes, and then stops changing.
