# Example schemas

These are schemas that I used to figure out how JSON validation schemas work.

### test1_validator_schema.json

This is as basic as it gets. This was just for me to get in my mind how a validation schema works.

Test files:

test1_demo1.json

test1_demo2.json


### test2_validator_schema.json

Here I'm introducing the "if"/"then" statement.

Test files:

test2_demo1.json

test2_demo2.json

test2_demo3.json


### test3_validator_schema.json

Here I'm introducing a compound "if" statement; in other words, "if condition1 and condition2 then..."

Test files:

test3_demo1.json

test3_demo2.json

test3_demo3.json


### test4_validator_schema.json

Another compound "if" statement, except this time I'm negating one of the conditions.

Test files:

test4_demo1.json

test4_demo2.json

test4_demo3.json

test4_demo4.json


### test_regex.json

Regex pattern matching. I used this with the Python jsonchema module, but in order to work you have to install it with the format setuptools extra.

pip install jsonschema(format)

See the "Validating Formats" section of this document: https://buildmedia.readthedocs.org/media/pdf/python-jsonschema/latest/python-jsonschema.pdf

Test files:

test_regex_demo1.json

test_regex_demo2.json


I used [ajv-cli](https://github.com/jessedc/ajv-cli) on Windows 10 as the validation tool.  I had to install
[Node.js](https://nodejs.org/en/download/) first, and it seem happiest installing and running out of a git bash shell.
