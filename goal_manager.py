import json
from datetime import date, timedelta
from pathlib import Path


goals = []

DATA_FILE = Path(__file__).with_name("goals.json")
LEGACY_TEXT_FILE = Path(__file__).with_name("goals.txt")


def get_non_empty_input(message):
    while True:
        value = input(message).strip()
        if value != "":
            return value
        print("This field cannot be empty!")


def get_valid_int(message, minimum=None, maximum=None):
    while True:
        value = input(message).strip()
        number = validate_int(value, "Value", minimum, maximum)
        if number is not None:
            return number


def get_valid_date(message):
    while True:
        value = input(message).strip()
        valid_date = validate_date(value, "Date")
        if valid_date is not None:
            return valid_date


def validate_int(value, field_name, minimum=None, maximum=None, show_error=True):
    try:
        number = int(value)
    except (TypeError, ValueError):
        if show_error:
            print(field_name, "must be a number!")
        return None

    if minimum is not None and number < minimum:
        if show_error:
            print(field_name, "must be at least", minimum)
        return None

    if maximum is not None and number > maximum:
        if show_error:
            print(field_name, "must be at most", maximum)
        return None

    return number


def validate_date(value, field_name="Date", show_error=True):
    if isinstance(value, date):
        return value.isoformat()

    try:
        return date.fromisoformat(str(value).strip()).isoformat()
    except (TypeError, ValueError):
        if show_error:
            print(field_name, "must be in YYYY-MM-DD format!")
        return None


def display_goal(item):
    print("----------------------------")
    print("Name:", item["name"])
    print("Progress:", str(item["progress"]) + "%")
    print("Status:", item["status"])
    print("Study Hours:", item["study_hours"])
    print("Created Date:", item["created_date"])
    print("Target Date:", item["target_date"])
    print("----------------------------")


def find_goal(goal_name):
    goal_name = goal_name.strip().lower()

    for item in goals:
        if item["name"].lower() == goal_name:
            return item

    for item in goals:
        if goal_name in item["name"].lower():
            return item

    return None


def find_exact_goal(goal_name):
    goal_name = goal_name.strip().lower()

    for item in goals:
        if item["name"].lower() == goal_name:
            return item

    return None


def search_goals_by_name(goal_name):
    goal_name = goal_name.strip().lower()
    matches = []

    for item in goals:
        if goal_name in item["name"].lower():
            matches.append(item)

    return matches


def add_goal(name=None, study_hours=None, created_date=None, target_date=None, auto_save=True):
    if name is None:
        name = get_non_empty_input("Enter Goal Name: ")
    else:
        name = str(name).strip()

    if name == "":
        print("Goal name cannot be empty!")
        return False

    if find_exact_goal(name) is not None:
        print("A goal with this name already exists!")
        return False

    if study_hours is None:
        study_hours = get_valid_int("Enter Study Hours: ", 1)
    else:
        study_hours = validate_int(study_hours, "Study Hours", 1)
        if study_hours is None:
            return False

    if created_date is None:
        created_date = get_valid_date("Enter Created Date (YYYY-MM-DD): ")
    else:
        created_date = validate_date(created_date, "Created Date")
        if created_date is None:
            return False

    if target_date is None:
        target_date = get_valid_date("Enter Target Date (YYYY-MM-DD): ")
    else:
        target_date = validate_date(target_date, "Target Date")
        if target_date is None:
            return False

    if date.fromisoformat(target_date) < date.fromisoformat(created_date):
        print("Target Date cannot be before Created Date!")
        return False

    goal = {
        "name": name,
        "progress": 0,
        "status": "In Progress",
        "study_hours": study_hours,
        "created_date": created_date,
        "target_date": target_date
    }

    goals.append(goal)

    if auto_save:
        save_goals(silent=True)

    print("Goal Added Successfully!")
    return True


def view_goals():
    if len(goals) == 0:
        print("Nothing Found!")
        return []

    for item in goals:
        display_goal(item)

    return goals


def update_progress(goal_name=None, new_progress=None, auto_save=True):
    if len(goals) == 0:
        print("Nothing Found!")
        return False

    if goal_name is None:
        goal_name = get_non_empty_input("Enter Goal Name: ")

    item = find_goal(goal_name)
    if item is None:
        print("Goal Not Found!")
        return False

    if new_progress is None:
        new_progress = get_valid_int("Enter New Progress (0-100): ", 0, 100)
    else:
        new_progress = validate_int(new_progress, "Progress", 0, 100)
        if new_progress is None:
            return False

    item["progress"] = new_progress

    if new_progress == 100:
        item["status"] = "Completed"
    else:
        item["status"] = "In Progress"

    if auto_save:
        save_goals(silent=True)

    print("Updated Successfully!")
    return True


def search_goal(goal_name=None):
    if len(goals) == 0:
        print("Nothing Found!")
        return []

    if goal_name is None:
        goal_name = get_non_empty_input("Enter Goal Name: ")

    matches = search_goals_by_name(goal_name)

    if len(matches) == 0:
        print("Goal Not Found!")
        return []

    for item in matches:
        display_goal(item)

    return matches


def delete_goal(goal_name=None, auto_save=True):
    if len(goals) == 0:
        print("Nothing Found!")
        return False

    if goal_name is None:
        goal_name = get_non_empty_input("Enter Goal Name: ")

    item = find_goal(goal_name)
    if item is None:
        print("Goal Not Found!")
        return False

    goals.remove(item)

    if auto_save:
        save_goals(silent=True)

    print("Goal Deleted Successfully!")
    return True


def clean_loaded_goal(item):
    if not isinstance(item, dict):
        return None

    name = str(item.get("name", "")).strip()
    if name == "":
        return None

    progress = validate_int(item.get("progress", 0), "Progress", 0, 100, show_error=False)
    if progress is None:
        progress = 0

    study_hours = validate_int(item.get("study_hours", 1), "Study Hours", 1, show_error=False)
    if study_hours is None:
        study_hours = 1

    created_date = validate_date(item.get("created_date", date.today().isoformat()), "Created Date", show_error=False)
    if created_date is None:
        created_date = date.today().isoformat()

    target_date = validate_date(item.get("target_date", created_date), "Target Date", show_error=False)
    if target_date is None:
        target_date = created_date

    if date.fromisoformat(target_date) < date.fromisoformat(created_date):
        target_date = created_date

    status = "Completed" if progress == 100 else "In Progress"

    return {
        "name": name,
        "progress": progress,
        "status": status,
        "study_hours": study_hours,
        "created_date": created_date,
        "target_date": target_date
    }


def save_goals(silent=False):
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(goals, file, indent=4)

        if not silent:
            print("Goals Saved Successfully!")

        return True

    except OSError as error:
        print("Unable to save goals:", error)
        return False


def load_legacy_text_goals():
    loaded_goals = []

    try:
        with LEGACY_TEXT_FILE.open("r", encoding="utf-8") as file:
            while True:
                name = file.readline().strip()

                if name == "":
                    break

                progress = file.readline().strip()
                status = file.readline().strip()
                study_hours = file.readline().strip()
                created_date = file.readline().strip()
                target_date = file.readline().strip()

                goal = clean_loaded_goal({
                    "name": name,
                    "progress": progress,
                    "status": status,
                    "study_hours": study_hours,
                    "created_date": created_date,
                    "target_date": target_date
                })

                if goal is not None:
                    loaded_goals.append(goal)

    except OSError:
        return []

    return loaded_goals


def load_goals(silent=False):
    goals.clear()

    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                saved_goals = json.load(file)

            if not isinstance(saved_goals, list):
                print("Saved goal file is not in the correct format!")
                return False

            for item in saved_goals:
                goal = clean_loaded_goal(item)
                if goal is not None:
                    goals.append(goal)

            if not silent:
                print("Goals Loaded Successfully!")

            return True

        except json.JSONDecodeError:
            print("Saved goal file is not valid JSON. Starting with an empty list.")
            return False

        except OSError as error:
            print("Unable to load goals:", error)
            return False

    legacy_goals = load_legacy_text_goals()
    if len(legacy_goals) > 0:
        goals.extend(legacy_goals)
        save_goals(silent=True)

        if not silent:
            print("Old goals.txt data was loaded and saved as goals.json!")

        return True

    if not silent:
        print("No Saved Goals Found!")

    return False


def get_overdue_goals():
    today = date.today()
    overdue_goals = []

    for item in goals:
        target_date = date.fromisoformat(item["target_date"])
        if item["status"] != "Completed" and target_date < today:
            overdue_goals.append(item)

    return overdue_goals


def get_due_soon_goals(days=3):
    today = date.today()
    limit = today + timedelta(days=days)
    due_soon_goals = []

    for item in goals:
        target_date = date.fromisoformat(item["target_date"])
        if item["status"] != "Completed" and today <= target_date <= limit:
            due_soon_goals.append(item)

    return due_soon_goals


def get_closest_deadline_goal():
    active_goals = []

    for item in goals:
        if item["status"] != "Completed":
            active_goals.append(item)

    if len(active_goals) == 0:
        return None

    active_goals.sort(key=lambda item: date.fromisoformat(item["target_date"]))
    return active_goals[0]


def get_next_focus_goal():
    active_goals = []

    for item in goals:
        if item["status"] != "Completed":
            active_goals.append(item)

    if len(active_goals) == 0:
        return None

    today = date.today()

    def priority_score(item):
        target_date = date.fromisoformat(item["target_date"])
        days_left = (target_date - today).days
        overdue_priority = 0 if days_left < 0 else 1
        return (overdue_priority, days_left, item["progress"])

    active_goals.sort(key=priority_score)
    return active_goals[0]


def dashboard():
    print("\n===== AI LEARNING PLATFORM DASHBOARD =====")
    print("Total Goals:", len(goals))

    if len(goals) == 0:
        print("Add your first goal to see dashboard details.")
        return {
            "total_goals": 0,
            "completed_goals": 0,
            "pending_goals": 0,
            "average_progress": 0
        }

    completed_goals = 0
    total_progress = 0
    total_study_hours = 0

    for item in goals:
        if item["status"] == "Completed":
            completed_goals += 1

        total_progress += item["progress"]
        total_study_hours += item["study_hours"]

    pending_goals = len(goals) - completed_goals
    average_progress = total_progress / len(goals)
    overdue_goals = get_overdue_goals()
    due_soon_goals = get_due_soon_goals()
    next_focus_goal = get_next_focus_goal()

    print("Completed Goals:", completed_goals)
    print("Pending Goals:", pending_goals)
    print("Overdue Goals:", len(overdue_goals))
    print("Due Soon Goals:", len(due_soon_goals))
    print("Total Planned Study Hours:", total_study_hours)
    print("Average Progress:", round(average_progress, 2), "%")

    if next_focus_goal is not None:
        print("Suggested Focus:", next_focus_goal["name"])

    return {
        "total_goals": len(goals),
        "completed_goals": completed_goals,
        "pending_goals": pending_goals,
        "overdue_goals": len(overdue_goals),
        "due_soon_goals": len(due_soon_goals),
        "average_progress": average_progress,
        "total_study_hours": total_study_hours,
        "suggested_focus": next_focus_goal["name"] if next_focus_goal is not None else None
    }


def analytics():
    print("\n===== LEARNING ANALYTICS =====")

    if len(goals) == 0:
        print("Nothing Found!")
        return {}

    highest_progress = max(item["progress"] for item in goals)
    lowest_progress = min(item["progress"] for item in goals)
    total_study_hours = sum(item["study_hours"] for item in goals)
    completed_goals = sum(1 for item in goals if item["status"] == "Completed")
    average_study_hours = total_study_hours / len(goals)
    completed_percentage = (completed_goals / len(goals)) * 100

    not_started = sum(1 for item in goals if item["progress"] == 0)
    in_progress = sum(1 for item in goals if 0 < item["progress"] < 100)

    print("Highest Progress:", highest_progress, "%")
    print("Lowest Progress:", lowest_progress, "%")
    print("Total Study Hours:", total_study_hours, "hours")
    print("Average Study Hours:", round(average_study_hours, 2), "hours")
    print("Completed Goals Percentage:", round(completed_percentage, 2), "%")
    print("Not Started Goals:", not_started)
    print("In Progress Goals:", in_progress)
    print("Completed Goals:", completed_goals)

    return {
        "highest_progress": highest_progress,
        "lowest_progress": lowest_progress,
        "total_study_hours": total_study_hours,
        "average_study_hours": average_study_hours,
        "completed_percentage": completed_percentage,
        "not_started": not_started,
        "in_progress": in_progress,
        "completed_goals": completed_goals
    }
