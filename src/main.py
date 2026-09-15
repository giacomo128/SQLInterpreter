import runner
import sys

# debug function for dev testing
def debug():
    runner.execute("./src/tests/manual_tests/complex.usql", True)

def new_main():
    """main function
    """

    # check for correct number of arguments
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("")
        print("---- ERROR ----")
        print("Usage: sh run.sh test.usql or sh run.sh --o test.usql")
        print("")
        return
    
    # execute simple query executor
    if len(sys.argv) == 2:

        try:
            runner.execute(sys.argv[1], False)

        except Exception as e:
            print("")
            print("---- ERROR ----")
            print("")
            print(e)

    # execute query optimisation
    else:

        if sys.argv[1] != "--o":
            print("")
            print("---- ERROR ----")
            print("Usage: sh run.sh test.usql or sh run.sh --o test.usql")
            print("")
            return
        
        try:
            runner.execute(sys.argv[2], True)

        except Exception as e:
            print("")
            print("---- ERROR ----")
            print("")
            print(e)

if __name__ == "__main__":
    new_main()
