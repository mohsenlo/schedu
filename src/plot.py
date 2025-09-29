import matplotlib.pyplot as plt
import matplotlib.patches as patches
from models import Task
from helpers import convert_time_to_minute, end_is_on_tomorrow

days = [
    "Saturday",
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
]


class Plot:
    def __init__(self, tasks: list[Task]):
        self.tasks = tasks

    def add_task(self, ax, task: Task):
        name = task.name
        dys = task.days
        start = convert_time_to_minute(task.start) / 60
        end = convert_time_to_minute(task.end) / 60
        duration = end - start
        for day in dys:
            if end_is_on_tomorrow(task.start, task.end):
                # Add the part for the current day
                rect = patches.Rectangle(
                    (start, days.index(day.capitalize())),
                    24 - start,
                    1,
                    linewidth=1,
                    edgecolor="black",
                    facecolor="skyblue",
                    alpha=0.7,
                )
                ax.add_patch(rect)
                ax.text(
                    start + (24 - start) / 2,
                    days.index(day.capitalize()) + 0.5,
                    name + f"\n{task.start}\n to \n {task.end}",
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=10,
                    color="black",
                )
                # Add the part for the next day
                next_day_index = (days.index(day.capitalize()) + 1) % len(days)
                rect = patches.Rectangle(
                    (0, next_day_index),
                    end,
                    1,
                    linewidth=1,
                    edgecolor="black",
                    facecolor="skyblue",
                    alpha=0.7,
                )
                ax.add_patch(rect)
                ax.text(
                    end / 2,
                    next_day_index + 0.5,
                    name + f"\n{task.start}\n to \n {task.end}",
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=10,
                    color="black",
                )
            else:
                rect = patches.Rectangle(
                    (start, days.index(day.capitalize())),
                    duration,
                    1,
                    linewidth=1,
                    edgecolor="black",
                    facecolor="skyblue",
                    alpha=0.7,
                )
                ax.add_patch(rect)
                ax.text(
                    start + duration / 2,
                    days.index(day.capitalize()) + 0.5,
                    name + f"\n{task.start}\n to \n {task.end}",
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=10,
                    color="black",
                )

    def draw(self):
        fig, ax = plt.subplots(figsize=(15, 9))
        fig.canvas.manager.set_window_title("Weekly Schedule")

        # Days on y-axis
        ax.set_yticks([i + 0.5 for i in range(len(days))])
        ax.set_yticklabels(days)
        ax.set_ylim(0, len(days))
        ax.set_ylabel("Day of week")
        ax.invert_yaxis()

        # Time on x-axis (hours)
        ax.set_xlim(0, 24)
        ax.set_xticks(range(0, 25, 1))
        ax.set_xlabel("Hour of day")

        # Grid
        ax.grid(True, which="both", axis="both", linestyle="--", alpha=0.5)

        # Draw Tasks
        for t in self.tasks:
            self.add_task(ax, t)

        plt.title("Weekly Schedule")
        plt.show()
