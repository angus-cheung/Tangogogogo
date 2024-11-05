
from plan import PlanManager

VERSION = '0.0.5'
DEV_VER = '2024-10041036'

def main():
    print(f"\n単語を覚えろう　version:{VERSION}-{DEV_VER}\n")
    plan = PlanManager()
    plan.run_plan_if_need()

if __name__ == "__main__":
    main()
