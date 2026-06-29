from goal_manager import (
    add_goal,
    analytics,
    dashboard,
    delete_goal,
    load_goals,
    save_goals,
    search_goal,
    update_progress,
    view_goals,
)
from study_coach_agent import StudyCoachAgent


def get_menu_choice():
    try:
        return int(input("Enter Your Choice: "))
    except ValueError:
        print("Please enter a valid number!")
        return None


def main():
    load_goals()
    study_coach = StudyCoachAgent()

    while True:
        print("\n===== AI LEARNING TRACKER =====")
        print("1. Add Goal")
        print("2. View Goals")
        print("3. Update Progress")
        print("4. Search Goal")
        print("5. Delete Goal")
        print("6. Save Goals")
        print("7. Load Goals")
        print("8. Dashboard")
        print("9. Analytics")
        print("10. Exit")
        print("11. Study Coach Agent")

        choice = get_menu_choice()

        if choice == 1:
            add_goal()

        elif choice == 2:
            view_goals()

        elif choice == 3:
            update_progress()

        elif choice == 4:
            search_goal()

        elif choice == 5:
            delete_goal()

        elif choice == 6:
            save_goals()

        elif choice == 7:
            load_goals()

        elif choice == 8:
            dashboard()

        elif choice == 9:
            analytics()

        elif choice == 10:
            save_goals(silent=True)
            print("Thank You!")
            break

        elif choice == 11:
            study_coach.start()

        else:
            print("Invalid Choice!")


if __name__ == "__main__":
    main()
