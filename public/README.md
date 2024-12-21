# Notes
Works with **npm 7.24.2** and **node 14.17.6** (you can use `nvm` to install it).

There are problems with installing dependencies:
`npm WARN <PACKAGE> requires a peer of <ANOTHER_PACKAGE> but none is installed. You must install peer dependencies yourself.`

Last time there were issues to run commands `npm run local/prod:1/2`

This way to install deps solved the problem.
```
npx install-peerdeps --dev @cscenter/eslint-config
npm install --save-dev eslint@^8.8.0
```

The log for fixing problems with dependencies.
```
npm install eslint-plugin-import@^2.25.4 --save-dev
npm install eslint-plugin-react@^7.28.0 --save-dev
npm install eslint-plugin-jsx-a11y@^6.5.1 --save-dev
npm install eslint-config-prettier@^8.1.0 --save-dev
npm install eslint-plugin-prettier@^4.0.
```
For local build swap lines in selector-engine.js

From
```
import { makeArray } from '../util/index';
import { closest, find as findFn, findOne, matches } from './polyfill';
```
To
```
import { closest, find as findFn, findOne, matches } from './polyfill';
import { makeArray } from '../util/index';
```

# Project Structure

```
core/ django related files
docs/ some info how to recreate dev environment
gulp/ gulp tasks and configuration
templates/ <-- html should be places here
design/ - sources for logos and other long-term useful stuff
node_modules/  # Node.js dependencies (ignore it)
src/  # js and css files root directory
webpack/  # webpack configuration
assets/  # XXX: Contains mixed content (static and dynamic). Files inside dist/* are generated, do not edit it directly.
media/  # Put static which not directly related to layout or page (some dynamic stuff)
```



# Run python dev server

```
# Run dev server
$ ./manage.py runserver 8000
# Compile css
$ npm run gulp:[1-2]:build
# Build js with webpack
npm run local:[1-2]
# In iTerm2 you can use `make` command
```

TODO: browserify-incremental
