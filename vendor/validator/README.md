# Validator

## Introduction

This directory contains the json-schema validator used in Qvain.

The code is written in ES6 (ES2015) Javascript. To test, you probably need to install babel-cli and babel-preset-env because – depending on the version – node might not understand all of the ES6 features.

```
$ npm install babel-cli babel-preset-env
```

Then, you can run the watcher:

```
$ ./dev.sh
```

... which should transpile the Javascript files from ./src to ./build.

You can then run the Javascript files in the ./build directory with node:

```
$ node build/index.js
```

If your version of node supports all ES6 functionality, such as modules, then you can simply run the code from the ./src directory directly.


## Bugs and Todo

- `uniqueItems` in array validation only accepts simple values, not objects
