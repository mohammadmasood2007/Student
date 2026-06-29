import re
from datetime import date, timedelta

import goal_manager


class StudyCoachAgent:
    def __init__(self):
        self.tools = {
            "add_goal": goal_manager.add_goal,
            "view_goals": goal_manager.view_goals,
            "search_goal": goal_manager.search_goal,
            "update_progress": goal_manager.update_progress,
            "delete_goal": goal_manager.delete_goal,
            "dashboard": goal_manager.dashboard,
            "analytics": goal_manager.analytics,
            "save_goals": goal_manager.save_goals,
            "load_goals": goal_manager.load_goals
        }

    def start(self):
        print("\n===== STUDY COACH AGENT =====")
        print("Type a command in normal English, or type 'back' to return to the menu.")
        print("Example: Update DSA progress to 60%")

        while True:
            command = input("\nYou: ").strip()

            if command.lower() in ["back", "exit", "menu"]:
                print("Returning to main menu.")
                break

            self.handle_command(command)

    def handle_command(self, command):
        if command.strip() == "":
            print("Please enter a command.")
            return

        lower_command = command.lower()

        if lower_command in ["help", "commands", "what can you do"]:
            self.show_help()
            return

        if self.is_add_goal_command(lower_command):
            self.add_goal_from_command(command)
            return

        if "progress" in lower_command and ("update" in lower_command or "set" in lower_command):
            self.update_progress_from_command(command)
            return

        if lower_command.startswith("delete") or lower_command.startswith("remove"):
            self.delete_goal_from_command(command)
            return

        if any(word in lower_command for word in ["show", "view", "list"]) and "goal" in lower_command:
            self.tools["view_goals"]()
            return

        if lower_command.startswith("find") or lower_command.startswith("search"):
            self.search_goal_from_command(command)
            return

        if "dashboard" in lower_command:
            self.tools["dashboard"]()
            return

        if "analytics" in lower_command:
            self.tools["analytics"]()
            return

        if "save" in lower_command:
            self.tools["save_goals"]()
            return

        if "load" in lower_command:
            self.tools["load_goals"]()
            return

        if "closest" in lower_command and "deadline" in lower_command:
            self.show_closest_deadline()
            return

        if "overdue" in lower_command:
            self.warn_overdue_goals()
            return

        if "summarize" in lower_command or "summary" in lower_command:
            self.summarize_progress()
            return

        if "study today" in lower_command or "focus" in lower_command or "priority" in lower_command:
            self.recommend_study_priority()
            return

        print("I could not understand that command.")
        self.show_help()

    def show_help(self):
        print("\nTry commands like:")
        print("- Add a goal for Python OOP.")
        print("- Show all my goals.")
        print("- Update DSA progress to 60%.")
        print("- Delete the SQL goal.")
        print("- What should I study today?")
        print("- Which goal is closest to its deadline?")
        print("- Summarize my learning progress.")

    def is_add_goal_command(self, lower_command):
        return lower_command.startswith("add") and "goal" in lower_command

    def clean_goal_name(self, name):
        name = re.sub(r"\b(goal|goals)\b", "", name, flags=re.IGNORECASE)
        name = re.sub(r"^(the|my|a|an)\s+", "", name.strip(), flags=re.IGNORECASE)
        return name.strip(" .")

    def add_goal_from_command(self, command):
        name = re.sub(r"^add\s+(a\s+)?goal\s*", "", command, flags=re.IGNORECASE).strip()
        name = re.sub(r"^(for|about|to learn)\s+", "", name, flags=re.IGNORECASE).strip()

        target_date = None
        target_match = re.search(r"\bby\s+(\d{4}-\d{2}-\d{2})", name)
        if target_match:
            target_date = target_match.group(1)
            name = name.replace(target_match.group(0), "").strip()

        study_hours = None
        hours_match = re.search(r"\b(?:for|with)\s+(\d+)\s*(study\s*)?hours?", name, flags=re.IGNORECASE)
        if hours_match:
            study_hours = int(hours_match.group(1))
            name = name.replace(hours_match.group(0), "").strip()

        name = self.clean_goal_name(name)

        if name == "":
            print("Please mention the goal name. Example: Add a goal for Python OOP.")
            return

        if study_hours is None:
            study_hours = 10

        created_date = date.today().isoformat()
        if target_date is None:
            target_date = (date.today() + timedelta(days=7)).isoformat()

        self.tools["add_goal"](name, study_hours, created_date, target_date)

    def update_progress_from_command(self, command):
        match = re.search(r"(update|set)\s+(.+?)\s+progress\s+(to\s+)?(\d+)%?", command, flags=re.IGNORECASE)

        if match is None:
            match = re.search(r"progress\s+of\s+(.+?)\s+(to\s+)?(\d+)%?", command, flags=re.IGNORECASE)
            if match is None:
                print("Please use a command like: Update DSA progress to 60%.")
                return

            goal_name = match.group(1)
            progress = match.group(3)
        else:
            goal_name = match.group(2)
            progress = match.group(4)

        goal_name = self.clean_goal_name(goal_name)
        self.tools["update_progress"](goal_name, progress)

    def delete_goal_from_command(self, command):
        goal_name = re.sub(r"^(delete|remove)\s+", "", command, flags=re.IGNORECASE)
        goal_name = self.clean_goal_name(goal_name)

        if goal_name == "":
            print("Please mention which goal to delete.")
            return

        self.tools["delete_goal"](goal_name)

    def search_goal_from_command(self, command):
        goal_name = re.sub(r"^(find|search)\s+", "", command, flags=re.IGNORECASE)
        goal_name = re.sub(r"^(for)\s+", "", goal_name, flags=re.IGNORECASE)
        goal_name = self.clean_goal_name(goal_name)

        if goal_name == "":
            print("Please mention which goal to search.")
            return

        self.tools["search_goal"](goal_name)

    def warn_overdue_goals(self):
        overdue_goals = goal_manager.get_overdue_goals()

        if len(overdue_goals) == 0:
            print("Good news! You do not have any overdue goals.")
            return

        print("Overdue Goals:")
        for item in overdue_goals:
            print("-", item["name"], "was due on", item["target_date"], "and is", str(item["progress"]) + "% complete")

    def show_closest_deadline(self):
        item = goal_manager.get_closest_deadline_goal()

        if item is None:
            print("No active goals found.")
            return

        print("Closest Deadline Goal:")
        goal_manager.display_goal(item)

    def recommend_study_priority(self):
        if len(goal_manager.goals) == 0:
            print("You do not have any goals yet. Add one first.")
            return

        self.warn_overdue_goals()

        focus_goal = goal_manager.get_next_focus_goal()
        if focus_goal is None:
            print("All goals are completed. Great work!")
            return

        target_date = date.fromisoformat(focus_goal["target_date"])
        days_left = (target_date - date.today()).days

        print("\nStudy Coach Recommendation:")
        print("Focus on:", focus_goal["name"])
        print("Progress:", str(focus_goal["progress"]) + "%")
        print("Deadline:", focus_goal["target_date"])

        if days_left < 0:
            print("Reason: This goal is overdue, so it should be handled first.")
        elif days_left <= 3:
            print("Reason: This goal is close to its deadline.")
        elif focus_goal["progress"] < 50:
            print("Reason: This goal still needs a lot of progress.")
        else:
            print("Reason: This is the best active goal to continue next.")

    def summarize_progress(self):
        if len(goal_manager.goals) == 0:
            print("No goals found to summarize.")
            return

        stats = self.tools["analytics"]()
        dashboard = self.tools["dashboard"]()

        print("\nStudy Coach Summary:")
        print("You have completed", dashboard["completed_goals"], "out of", dashboard["total_goals"], "goals.")
        print("Your average progress is", str(round(dashboard["average_progress"], 2)) + "%.")
        print("Your planned study time is", stats["total_study_hours"], "hours.")

        if dashboard["suggested_focus"] is not None:
            print("Next focus:", dashboard["suggested_focus"])
