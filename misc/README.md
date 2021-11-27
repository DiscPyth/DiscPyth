# This directory contains miscellaneous files

## These are in 2 categories
1. Dev
2. Tests

## ./dev

Some bad code here. Mainly snippets repatedly used for some sort of work in the development process.

## ./tests

> **WARNING:** Test files prexied with `r_` and `w_` maybe/are API abuse, these are mainly to test how the library handles cases.

`./test` contains files/code used to test the library.

### These files are divided into 3 categories based on their perfix.

1. `l_` - Library Abuse :^). These files test how certain attributes and methods can be manipulated/abused to break functionality. They may partially abuse the API.
2. `w_` - These are tests related to the Discord Gateway aka WebSocket, they are API abuse and it is not recommended that you perform these tests.
3. `r_` - These tests are related to Discord's RESTful API, these are also API abuse and hence are not recommended to be performed.

> **NOTE**: Not all tests are API abuse, but in general they are things you shouldn't do

> **NOTE**: If you are doing Gateway or REST tests; make sure to keep a reasonable enough interval between tests, any form or ban fron the service is your matter, do not cause a scene here for getting your self/bot banned due to API Abuse