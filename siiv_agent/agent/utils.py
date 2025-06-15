def print_orange(message):
    ORANGE = "\033[38;5;208m"
    RESET = "\033[0m"
    print(f"{ORANGE}{message}{RESET}")

def print_green(message):
    GREEN = "\033[38;5;76m"
    RESET = "\033[0m"
    print(f"{GREEN}{message}{RESET}")
