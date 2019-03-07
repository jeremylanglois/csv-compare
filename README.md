<h2 align="center">CSV Compare</h2>

<p align="center">
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

This is a CLI tool allowing comparaison of two csv files.

Table of Contents
-----------------

  * [Usage](#usage)
  * [Technical documentation](#technical)

Definition
----------

An [OpenAPI 2.0](https://www.openapis.org) JSON definition is available at /swagger.json


Usage
-----

### Parameters ###

| ParametersEnvironment   | Service Definition                                         | Swagger UI |
|:--------------|:-----------------------------------------------------------|:----------------------------------------------|
| `SourceFile`  | <http://guru.gem.myengie.com/python_service_name/swagger.json>      | [Production](http://guru.gem.myengie.com/python_service_name)   |
| `TargetFile`  | <http://10.22.218.199/python_service_name-acceptance/swagger.json>  | [Acceptance](http://10.22.218.199/python_service_name-acceptance)   |

### Options ###

| Short option | Long option | Description       | Default Value |
|:-------------|:------------|:------------------|:--------------|
| `-v` | `--verbose` | Increase output verbosity. | False   |
| `-o` | `--output_directory` | Directory where the output of the comparison should be stored. | Current Working Directory |
| `-k` | `--key_list` | List of keys to be used to compare both files. Value of the header of the csv file. | None |
| `-e` | `--exclusion_list` | List of columns to exclude from comparison (blacklist). For instance, to ignore a know difference. Cannot be used in combination with columns_list option. | None  |
| `-c` | `--columns_to_compare_list` | List of columns to strictly use for comparison (whitelist). Cannot be used in combination with exclusion_list option. | None |
| `-i` | `--index_list` | Specify a list of column which contain few different values. Used to speed up the comparison. | None |
| `-m` | `--comparison_method` | Method used to compare both files ("one_to_one", "one_to_many", "many_to_one" or "many_to_many"). | one_to_one |

### Outputs ###

Contributing
------------

Everyone is free to contribute on this project.

Before creating an issue please make sure that it was not already reported.

Project follow "Black" code formatting: https://black.readthedocs.io/en/stable/

To integrate it within Pycharm: https://black.readthedocs.io/en/stable/editor_integration.html#pycharm

To add the pre-commit hook, after the installation run: **pre-commit install**

Support-And-Migration
---------------------

### Infrastructure ###

Service is hosted on Azure using [this infrastrure](https://wiki.gem.myengie.com/display/ETRM/Azure+infrastructure%3A+InfrastructureAsCode+and+Continuous+Deployment) (DockerFile of this project can be consulted for details on this specific service).

### Information Security ###

#### Confidentiality ####

TODO: Fill this section

#### Integrity ####

TODO: Fill this section

License
-------

Copyright 2018 Engie

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

[More information](https://opensource.org/licenses/MIT)
