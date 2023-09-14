/*
We're using requirejs library because open edx uses this library to add internal or external modules.
Check the doc here: https://requirejs.org/
It's necessary to use this because all modules of this lib won't work as expected. So this is
adding our modules to the window object that has all modules in the CMS, check this:
https://github.com/openedx/edx-platform/blob/7e23feeb33861c0de3572364cd103c3929bb0588/common/static/js/RequireJS-namespace.js#L3
*/
(function (require) {
  require.config({
    paths: {
      jsMind: "https://unpkg.com/jsmind@latest/es6/jsmind"
    },
  });
}).call(this, require || RequireJS.require);
