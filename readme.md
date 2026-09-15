# Usage

The command-line utility can be executed by running the `run.sh` program, as specified in the specs: 

- `sh run.sh <usql file>`  
or 
- `sh run.sh --o <usql file>`
  
since the system is installoing new dependencies, the output will be logged into `log.txt`  
Please note that the system requires the full path to be specified relative to the folder containing `run.sh`.  
This means that both the command `sh run.sh <--o> <path to usql file from the directory>` and the csv file to be used in the load instruction of the `usql program` need an appropriate path from the directory.
  
# Examples

The `examples` folder has been provided to show how inequality and functional dependencies have been implemented.  
`test.usql` is a simple that that can be executed and it reflects the program mentioned in the specs.

# Tests

## Automated testing

to run the automated tests, first please run the program at least once as it will install all the needed dependencies.  
please open VsCode in the `src` folder.  
Type in the search bar: `>Python: Select interpreter`  make sure that the `global python interpreter` is selected.   
Install the `Python` extension in vscode and click on the testing icon in the left toolbar. 
Type in the search bar: `>Python: Configure tests` and select the `pytest` option and the `tests` folder.    
Once the tests are detected, click on run to run them all.

## Manual Tests

To run manual tests, run the following command for each file in `src/tests/manual_tests/`  
`sh run.sh --o src/tests/manual_tests/<usql file>`

## Approval
The upload of this project has been approved by Mr Adam Barwell.