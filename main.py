
from plan import run_plan_if_need

VERSION = '0.0.2'
DEV_VER = '2024-09121118'

def main():
    print(f"\n単語を覚えろう　version:{VERSION}-{DEV_VER}\n")
    run_plan_if_need()

if __name__ == "__main__":
    main()
