import co2114




def main():
    
    print("Hello World")


#################################
## DO NOT EDIT BELOW THIS LINE ##
##   UNLESS YOU KNOW WHAT YOU  ##
##     ARE DOING               ##
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog="co2114_lab01")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    if args.test:
        from co2114.engine import ClockApp
        print("Running Demo Code")
        ClockApp.run_default()
    else:
        main() 