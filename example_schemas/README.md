# Example schemas

These are schemas that I used to figure out how JSON validation schemas work.

### test1_validator_schema.json

This is as basic as it gets. This was just for me to get in my mind how a validation schema works.

#### Test files:

test1_demo1.json  
test1_demo2.json


### test2_validator_schema.json

Here I'm introducing the "if"/"then" statement.

#### Test files:

test2_demo1.json  
test2_demo2.json  
test2_demo3.json


### test3_validator_schema.json

Here I'm introducing a compound "if" statement; in other words, "if condition1 and condition2 then..."

#### Test files:

test3_demo1.json  
test3_demo2.json  
test3_demo3.json


### test4_validator_schema.json

Another compound "if" statement, except this time I'm negating one of the conditions.

#### Test files:

test4_demo1.json  
test4_demo2.json  
test4_demo3.json  
test4_demo4.json


I used [ajv-cli](https://github.com/jessedc/ajv-cli) on Windows 10 as the validation tool.  I had to install
[Node.js](https://nodejs.org/en/download/) first, and it seem happiest installing and running out of a git bash shell.


### test_regex.json

Regex pattern matching. I used this with the Python jsonchema module, but in order to work you have to install it with the format setuptools extra.

pip install jsonschema(format)

See the "Validating Formats" section of this document: https://buildmedia.readthedocs.org/media/pdf/python-jsonschema/latest/python-jsonschema.pdf

#### Test files:

test_regex_demo1.json  
test_regex_demo2.json


### test_regex_nocase.json

Regex pattern matching that ignores case for very specific values.  Clunky, but apparently JSON validation schemas don't support ignore case flags (or at least I couldn't get it to work).

#### Use case:

We have true/false columns in csv files that we need to validate. The values in these columns can be either string values or Boolean values depending on what software was used to create them.  If they are string values, they could be any mix of case (True, true, TRUE, TrUe, etc.), but at the end of the day we don't care about the case, we just care whether the answer is true or false.  We would also like to be able to validate the file "in place", i.e. not have to run a preprocessor on it.

I would seriously discourage ignoring case in other situations without some deep thinking about possible unintended consequences.  This is especially true if you're doing any kind of analysis on the data.

#### Test files:

test_regex_nocase_demo1.json  
test_regex_nocase_demo2.json  
test_regex_nocase_demo3.json  
test_regex_nocase_demo4.json  
