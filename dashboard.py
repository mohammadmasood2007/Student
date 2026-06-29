from datetime import date, timedelta

import pandas as pd
import streamlit as st

import goal_manager


def load_data():
    goal_manager.load_goals(silent=True)


def get_goal_rows(goals):
    rows = []

    for item in goals:
        rows.append({
            "Goal Name": item["name"],
            "Progress": item["progress"],
            "Status": item["status"],
            "Study Hours": item["study_hours"],
            "Created Date": item["created_date"],
            "Target Date": item["target_date"]
        })

    return rows


def get_goal_dataframe(goals):
    goal_data = pd.DataFrame(get_goal_rows(goals))

    if goal_data.empty:
        return goal_data

    goal_data["Created Date"] = pd.to_datetime(goal_data["Created Date"], errors="coerce")
    goal_data["Target Date"] = pd.to_datetime(goal_data["Target Date"], errors="coerce")
    goal_data["Progress"] = goal_data["Progress"].astype(int)
    goal_data = goal_data.sort_values("Target Date", kind="stable").reset_index(drop=True)

    return goal_data


def highlight_overdue_goal(row):
    target_date = row["Target Date"]

    if (
        pd.notna(target_date)
        and target_date.date() < date.today()
        and row["Status"] != "Completed"
    ):
        return ["background-color: #fff1f2; color: #991b1b"] * len(row)

    return [""] * len(row)


def show_goal_dataframe(goals, height=320):
    goal_data = get_goal_dataframe(goals)

    if goal_data.empty:
        return False

    styled_data = goal_data.style.apply(highlight_overdue_goal, axis=1).format({
        "Progress": "{:.0f}%",
        "Created Date": lambda value: value.strftime("%d %b %Y") if pd.notna(value) else "",
        "Target Date": lambda value: value.strftime("%d %b %Y") if pd.notna(value) else ""
    })

    st.dataframe(styled_data, use_container_width=True, height=height)
    return True


def get_dashboard_stats():
    goals = goal_manager.goals
    total_goals = len(goals)
    completed_goals = sum(1 for item in goals if item["status"] == "Completed")
    pending_goals = total_goals - completed_goals
    overdue_goals = goal_manager.get_overdue_goals()
    due_soon_goals = goal_manager.get_due_soon_goals()
    low_progress_goals = [
        item for item in goals
        if item["progress"] < 30 and item["status"] != "Completed"
    ]
    total_progress = sum(item["progress"] for item in goals)
    total_study_hours = sum(item["study_hours"] for item in goals)
    average_progress = total_progress / total_goals if total_goals > 0 else 0
    completed_percentage = (completed_goals / total_goals) * 100 if total_goals > 0 else 0

    highest_progress = max((item["progress"] for item in goals), default=0)
    lowest_progress = min((item["progress"] for item in goals), default=0)

    return {
        "total_goals": total_goals,
        "completed_goals": completed_goals,
        "pending_goals": pending_goals,
        "overdue_goals": overdue_goals,
        "due_soon_goals": due_soon_goals,
        "low_progress_goals": low_progress_goals,
        "average_progress": average_progress,
        "total_study_hours": total_study_hours,
        "completed_percentage": completed_percentage,
        "highest_progress": highest_progress,
        "lowest_progress": lowest_progress
    }


def get_recommendation_reason(goal):
    if goal is None:
        return "Add a goal first so the Study Coach can recommend a focus area."

    target_date = date.fromisoformat(goal["target_date"])
    days_left = (target_date - date.today()).days

    if days_left < 0:
        return "This goal is overdue, so it should be handled first."

    if days_left <= 3:
        return "This goal is close to its deadline."

    if goal["progress"] < 30:
        return "This goal has low progress and needs attention."

    if goal["progress"] < 50:
        return "This goal still needs steady progress."

    return "This goal is the best active goal to continue next."


def build_learning_summary(stats, recommended_goal):
    if stats["total_goals"] == 0:
        return "No goals have been added yet. Start by adding one learning goal."

    summary = (
        "You have completed "
        + str(stats["completed_goals"])
        + " out of "
        + str(stats["total_goals"])
        + " goals. Your average progress is "
        + str(round(stats["average_progress"], 2))
        + "%, with "
        + str(stats["total_study_hours"])
        + " planned study hours."
    )

    if len(stats["overdue_goals"]) > 0:
        summary += " You have overdue goals, so focus on them first."
    elif recommended_goal is not None:
        summary += " A good next focus is " + recommended_goal["name"] + "."
    else:
        summary += " All goals are completed."

    return summary


def show_header():
    with st.container():
        st.title("🎓 AI Learning Tracker")
        st.caption("A polished student-friendly dashboard for tracking learning goals, progress, and study time.")

        st.divider()


def show_sidebar():
    with st.sidebar:
        st.header("Navigation")
        st.caption("Use the main tabs to move through the dashboard.")
        st.divider()

        st.write("Today's date")
        st.caption(date.today().strftime("%d %b %Y"))
        st.divider()

        if st.button("Reload", use_container_width=True):
            if goal_manager.load_goals():
                st.success("Goals reloaded.")
            else:
                st.warning("No saved goals were loaded.")


def show_metric_cards(stats):
    st.subheader("📊 Dashboard")

    metric_row = st.columns(7, gap="medium")

    metric_row[0].metric("Total", stats["total_goals"])
    metric_row[1].metric("Completed", stats["completed_goals"])
    metric_row[2].metric("Pending", stats["pending_goals"])
    metric_row[3].metric("Overdue", len(stats["overdue_goals"]))
    metric_row[4].metric("Due Soon", len(stats["due_soon_goals"]))
    metric_row[5].metric("Avg Progress", str(round(stats["average_progress"], 2)) + "%")
    metric_row[6].metric("Study Hours", stats["total_study_hours"])


def show_goal_table():
    st.subheader("🎯 Goals")

    if not show_goal_dataframe(goal_manager.goals):
        st.info("No goals found. Add a goal from Goal Actions.")


def show_progress_section(stats):
    st.subheader("Goal Progress")

    if stats["total_goals"] == 0:
        st.info("Progress charts will appear after you add goals.")
        return

    progress_col, goal_col = st.columns([1, 2], gap="large")

    with progress_col:
        st.write("Overall progress")
        st.progress(int(stats["average_progress"]))
        st.metric("Average Progress", str(round(stats["average_progress"], 2)) + "%")

    with goal_col:
        st.write("Individual goal progress")
        for item in goal_manager.goals:
            label_col, value_col = st.columns([4, 1])
            label_col.caption(item["name"])
            value_col.caption(str(item["progress"]) + "%")
            st.progress(item["progress"])


def show_chart_section(stats):
    st.subheader("Learning Charts")

    if stats["total_goals"] == 0:
        st.info("Charts will appear after you add goals.")
        return

    goal_data = get_goal_dataframe(goal_manager.goals)
    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        st.write("Goal Status")
        status_data = (
            goal_data["Status"]
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Goals")
        )

        st.vega_lite_chart(
            status_data,
            {
                "height": 260,
                "mark": {"type": "arc", "innerRadius": 55, "outerRadius": 110},
                "encoding": {
                    "theta": {"field": "Goals", "type": "quantitative"},
                    "color": {
                        "field": "Status",
                        "type": "nominal",
                        "scale": {"range": ["#2563eb", "#16a34a", "#f59e0b", "#ef4444"]}
                    },
                    "tooltip": [
                        {"field": "Status", "type": "nominal"},
                        {"field": "Goals", "type": "quantitative"}
                    ]
                },
                "view": {"stroke": None}
            },
            use_container_width=True
        )

    with right_col:
        st.write("Study Hours")
        st.vega_lite_chart(
            goal_data,
            {
                "height": 260,
                "mark": {"type": "bar", "cornerRadiusTopLeft": 4, "cornerRadiusTopRight": 4},
                "encoding": {
                    "x": {
                        "field": "Goal Name",
                        "type": "nominal",
                        "sort": "-y",
                        "axis": {"labelAngle": -25, "title": None}
                    },
                    "y": {"field": "Study Hours", "type": "quantitative", "title": "Hours"},
                    "color": {"value": "#0f766e"},
                    "tooltip": [
                        {"field": "Goal Name", "type": "nominal"},
                        {"field": "Study Hours", "type": "quantitative"}
                    ]
                },
                "view": {"stroke": None}
            },
            use_container_width=True
        )

    st.write("Progress")
    st.vega_lite_chart(
        goal_data,
        {
            "height": 280,
            "mark": {
                "type": "line",
                "point": {"filled": True, "size": 70},
                "strokeWidth": 3
            },
            "encoding": {
                "x": {"field": "Target Date", "type": "temporal", "title": "Target Date"},
                "y": {
                    "field": "Progress",
                    "type": "quantitative",
                    "title": "Progress (%)",
                    "scale": {"domain": [0, 100]}
                },
                "tooltip": [
                    {"field": "Goal Name", "type": "nominal"},
                    {"field": "Progress", "type": "quantitative"},
                    {"field": "Target Date", "type": "temporal"}
                ]
            },
            "view": {"stroke": None}
        },
        use_container_width=True
    )


def show_study_coach_panel(stats):
    recommended_goal = goal_manager.get_next_focus_goal()
    closest_deadline = goal_manager.get_closest_deadline_goal()

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        st.write("Today's Recommended Goal")
        if recommended_goal is None:
            st.info("No active goal found.")
        else:
            st.success(recommended_goal["name"])
            st.write("Reason for Recommendation")
            st.write(get_recommendation_reason(recommended_goal))

    with right_col:
        st.write("Closest Deadline")
        if closest_deadline is None:
            st.info("No active deadline found.")
        else:
            st.write(closest_deadline["name"])
            st.write("Deadline:", closest_deadline["target_date"])

    st.divider()

    st.write("Overdue Goals")
    if len(stats["overdue_goals"]) == 0:
        st.info("No overdue goals.")
    else:
        for item in stats["overdue_goals"]:
            st.warning(item["name"] + " was due on " + item["target_date"])

    st.divider()

    st.write("AI Summary of Learning Progress")
    st.info(build_learning_summary(stats, recommended_goal))


def show_study_coach_expander(stats, expanded=False):
    with st.expander("Study Coach", expanded=expanded):
        show_study_coach_panel(stats)


def show_alerts(stats):
    st.subheader("Alerts")

    if stats["total_goals"] == 0:
        st.info("Add goals to start receiving learning alerts.")
        return

    if len(stats["overdue_goals"]) == 0 and len(stats["due_soon_goals"]) == 0 and len(stats["low_progress_goals"]) == 0:
        st.success("No alerts right now.")
        return

    for item in stats["overdue_goals"]:
        st.error(item["name"] + " is overdue. Deadline was " + item["target_date"] + ".")

    for item in stats["due_soon_goals"]:
        st.warning(item["name"] + " is due soon on " + item["target_date"] + ".")

    for item in stats["low_progress_goals"]:
        st.warning(item["name"] + " is below 30% progress.")


def show_quick_actions():
    st.subheader("Goal Actions")
    st.caption("These controls call the existing project functions and update goals.json.")

    action = st.selectbox(
        "Choose Action",
        ["Add Goal", "Update Progress", "Delete Goal", "Search Goal", "Save Goals", "Reload Goals"]
    )

    goal_names = [item["name"] for item in goal_manager.goals]

    if action == "Add Goal":
        with st.form("add_goal_form"):
            form_col_1, form_col_2 = st.columns(2)
            name = form_col_1.text_input("Goal Name")
            study_hours = form_col_2.number_input("Study Hours", min_value=1, value=10, step=1)
            created_date = form_col_1.date_input("Created Date", value=date.today())
            target_date = form_col_2.date_input("Target Date", value=date.today() + timedelta(days=7))
            submitted = st.form_submit_button("Add Goal")

        if submitted:
            result = goal_manager.add_goal(
                name,
                study_hours,
                created_date.isoformat(),
                target_date.isoformat()
            )
            if result:
                st.success("Goal added successfully.")
            else:
                st.error("Goal was not added. Please check the input.")

    elif action == "Update Progress":
        if len(goal_names) == 0:
            st.info("Add a goal first.")
        else:
            with st.form("update_progress_form"):
                goal_name = st.selectbox("Goal", goal_names)
                progress = st.slider("New Progress", min_value=0, max_value=100, value=50)
                submitted = st.form_submit_button("Update Progress")

            if submitted:
                result = goal_manager.update_progress(goal_name, progress)
                if result:
                    st.success("Progress updated successfully.")
                else:
                    st.error("Progress was not updated.")

    elif action == "Delete Goal":
        if len(goal_names) == 0:
            st.info("No goals available to delete.")
        else:
            with st.form("delete_goal_form"):
                goal_name = st.selectbox("Goal", goal_names)
                submitted = st.form_submit_button("Delete Goal")

            if submitted:
                result = goal_manager.delete_goal(goal_name)
                if result:
                    st.success("Goal deleted successfully.")
                else:
                    st.error("Goal was not deleted.")

    elif action == "Search Goal":
        with st.form("search_goal_form"):
            keyword = st.text_input("Search by Goal Name")
            submitted = st.form_submit_button("Search")

        if submitted:
            matches = goal_manager.search_goal(keyword)
            if len(matches) == 0:
                st.warning("No matching goals found.")
            else:
                show_goal_dataframe(matches, height=220)

    elif action == "Save Goals":
        if st.button("Save Goals"):
            if goal_manager.save_goals():
                st.success("Goals saved successfully.")
            else:
                st.error("Goals could not be saved.")

    elif action == "Reload Goals":
        if st.button("Reload Goals"):
            if goal_manager.load_goals():
                st.success("Goals reloaded successfully.")
            else:
                st.warning("No saved goals were loaded.")


def show_analytics(stats):
    metric_row = st.columns(5, gap="medium")

    metric_row[0].metric("Highest", str(stats["highest_progress"]) + "%")
    metric_row[1].metric("Lowest", str(stats["lowest_progress"]) + "%")
    metric_row[2].metric("Average", str(round(stats["average_progress"], 2)) + "%")
    metric_row[3].metric("Completed", str(round(stats["completed_percentage"], 2)) + "%")
    metric_row[4].metric("Study Hours", stats["total_study_hours"])


def show_analytics_expander(stats, expanded=False):
    with st.expander("Analytics", expanded=expanded):
        show_analytics(stats)


def main():
    st.set_page_config(
        page_title="AI Learning Tracker",
        page_icon="🎓",
        layout="wide"
    )

    load_data()
    show_sidebar()
    stats = get_dashboard_stats()

    show_header()

    dashboard_tab, goals_tab, analytics_tab, coach_tab = st.tabs([
        "Dashboard",
        "Goals",
        "Analytics",
        "Study Coach"
    ])

    with dashboard_tab:
        with st.container():
            show_metric_cards(stats)

        st.divider()

        with st.container():
            show_alerts(stats)

        st.divider()

        with st.container():
            show_progress_section(stats)

    with goals_tab:
        with st.container():
            show_goal_table()

        st.divider()

        with st.container():
            show_quick_actions()

    with analytics_tab:
        with st.container():
            st.subheader("📈 Analytics")
            show_analytics(stats)

        st.divider()

        with st.container():
            show_chart_section(stats)

    with coach_tab:
        with st.container():
            st.subheader("💡 Study Coach")
            show_study_coach_panel(stats)


if __name__ == "__main__":
    main()
