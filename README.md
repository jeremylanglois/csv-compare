<h2 align="center">CSV Compare</h2>

<p align="center">
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

This is a CLI tool allowing comparaison of two csv files.

Table of Contents
-----------------

  * [Usage](#usage)
  * [Technical documentation](#technical)

Usage
-----

### Parameters ###

| Name          | Description |
|:--------------|:------------|
| `SourceFile`  | Original file.   |
| `TargetFile`  | Destination file   |

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

