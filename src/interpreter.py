from parser import *
from datetime import date
import argparse
from models import Task
from plot import Plot
from helpers import *
from copy import deepcopy

# Constant
WEEK_DAY = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


class Interpreter:
    def __init__(self):
        # Key: task name, Value: task model
        self.tasks = {}

        # This store all tasks times to specific format, for handle conflicts.
        self.reserved = {
            "saturday": [],
            "sunday": [],
            "monday": [],
            "tuesday": [],
            "wednesday": [],
            "thursday": [],
            "friday": [],
        }

    def execute(self, statement):
        if isinstance(statement, TaskSt):
            if statement.update:
                self.update_task(statement)
            else:
                self.add_task(statement)
        elif isinstance(statement, RenameTask):
            self.rename_task(statement)
        elif isinstance(statement, Print):
            self.print(statement)
        elif isinstance(statement, Draw):
            self.draw()
        else:
            raise RuntimeError("Invalid statement!")

    def add_task(self, task_stmt: TaskSt):
        # TODO check conflict of task
        task = self.parse_task(task_stmt)
        if self.validate_task(task):
            self.tasks[task.name] = task
            self.fill_reserved(task)

    def update_task(self, task_stmt: TaskSt):
        """for update there is 4 possible way:
        * Update time only (start and end)
        * Update time only (duration and after specific event)
        * Update day only
        * Update time and day together"""
        # Check task is exists?
        task = self.tasks.get(task_stmt.name)
        old_task = deepcopy(task)

        if task is None:
            raise SystemError(f"Task {task_stmt.name} is not defined!!!")

        updated_task = None
        if task_stmt.time is not None:
            # use parse_task to get start and end time from different structure of statement(from _ to _ , at _ duration _ , duration _ after event_name)
            updated_task = self.parse_task(task_stmt)
            task.start = updated_task.start
            task.end = updated_task.end
            if task_stmt.time.after is not None:
                task.days = updated_task.days

        if task_stmt.days is not None and len(task_stmt.days) > 0:
            task.days = task_stmt.days

        # update reserved, if task wasn't valid, it will raise error
        self.clear_reserved(old_task)
        if self.validate_task(task, True):
            self.fill_reserved(task)

    def rename_task(self, rename_stmt: RenameTask):
        # Check Task exists?
        task = self.tasks.get(rename_stmt.old)
        if task is None:
            raise SystemError(f"Task {rename_stmt.old} is not defined!!!")
        # Check new name of task is unique?
        if self.tasks.get(rename_stmt.new) is not None:
            raise SystemError(f"Task {rename_stmt.new} is not UNIQUE!!!")

        task.name = rename_stmt.new
        self.tasks.pop(rename_stmt.old)
        self.tasks[task.name] = task

    def print(self, print_stmt: Print):
        if print_stmt.today:
            today = get_today()
            for task in self.tasks.values():
                if today.lower() in task.days:
                    print(task)
        else:
            task = self.tasks.get(print_stmt.target_name)
            if task is None:
                raise SystemError(f"Task {print_stmt.target_name} is not defined!!!")
            print(task)

    def parse_task(self, stmt: TaskSt) -> Task:
        """This convert a task statement to main task model.
        There is 3 way to set time for a task:
        * From .. : .. to .. : ..
        * At .. : .. Duration .. : ..
        * Duration .. : .. after task_name

        Error: If time of Task is None (may happen in updating tasks), Runtime error will raise.
        """
        name = stmt.name
        start = stmt.time.start
        end = stmt.time.end
        days = stmt.days
        # if start time is not defined, mean this task defined by after keyword (mean structure is :>> task task_name duration _ after _)
        if start is None:
            next_of = self.tasks.get(stmt.time.after)
            if next_of is None:
                raise RuntimeError(f"Task {stmt.time.after} is not defined!!!")
            start = next_of.end
            if days is None:
                # if using "... AFTER event_name" structure for task time, task don't have days (Except when use batch_task for day), should set days based task was before current task.
                # NOTE: this work when time of task on different days are same, if code updated for different time on different days, this section should be updated.
                if end_is_on_tomorrow(next_of.start, next_of.end):
                    days = []
                    for d in next_of.days:
                        # get next day of week
                        days.append(
                            WEEK_DAY[
                                (WEEK_DAY.index(d.capitalize()) + 1) % len(WEEK_DAY)
                            ]
                        )
                else:
                    days = next_of.days

        # if end time is not defined, mean this task defined by duration
        if end is None:
            end = self.get_end_time(start, stmt.time.duration)

        return Task(name, start, end, days)

    def get_end_time(self, start_time: str, duration: str) -> str:
        """* This function also do validating time format.(start, end, duration)"""
        self.validate_time(start_time)
        self.validate_time(duration)
        h1, m1 = split_time(start_time)
        h2, m2 = split_time(duration)
        m3 = m1 + m2
        mr = m3 % 60  # result minute
        hr = (h1 + h2 + int(m3 / 60)) % 24  # result hour
        end = f"{hr:02d}:{mr:02d}"
        self.validate_time(end)
        return end

    def validate_task(self, task: Task, updating: bool = False):
        """This function check a task is valid or not.
        * If updating is True, don't check existence of task."""
        # check task is Unique
        if self.tasks.get(task.name) is not None and not updating:
            raise RuntimeError(f"Task {task.name} is already exists!!!")
        # check conflict
        conflict, day, info = self.check_conflict(task)
        if conflict:
            raise RuntimeError(
                f"'{task.name}' have conflict with {info[2]} in {day} from {convert_minute_to_time(info[0])} to {convert_minute_to_time(info[1])}!!!"
            )
        return True

    def validate_time(self, time: str):
        h, m = split_time(time)
        if 0 > int(h) or int(h) > 23 or 0 > int(m) or int(m) > 59:
            raise RuntimeError(f"Time is invalid!!! got {time}")

    def get_task_in_days(self, days: list[str]) -> list[Task]:
        tasks = []
        for t in self.tasks.values():
            for d in days:
                if d in t.days:
                    tasks.append(t)
                    break
        return tasks

    def fill_reserved(self, task: Task):
        in_tomorrow = end_is_on_tomorrow(task.start, task.end)
        for d in task.days:
            s = convert_time_to_minute(task.start)
            e = convert_time_to_minute(task.end)
            if in_tomorrow:
                # fill today
                self.reserved[d.lower()].append([s, 1440, task.name])  # 1440 = 24*60
                # fill tomorrow
                self.reserved[
                    WEEK_DAY[
                        (WEEK_DAY.index(d.capitalize()) + 1) % len(WEEK_DAY)
                    ].lower()
                ].append([0, e, task.name])
            else:
                self.reserved[d.lower()].append([s, e, task.name])

    def clear_reserved(self, task: Task):
        in_tomorrow = end_is_on_tomorrow(task.start, task.end)
        for d in task.days:
            # remove from day of start task
            for r in self.reserved[d.lower()]:
                if r[2] == task.name:
                    self.reserved[d.lower()].remove(r)
            if in_tomorrow:
                tomorrow = WEEK_DAY[
                    (WEEK_DAY.index(d.capitalize()) + 1) % len(WEEK_DAY)
                ].lower()
                for r in self.reserved[tomorrow]:
                    if r[2] == task.name:
                        self.reserved[tomorrow].remove(r)

    def check_conflict(self, new_task: Task):
        in_tomorrow = end_is_on_tomorrow(new_task.start, new_task.end)

        for d in new_task.days:
            for r in self.reserved[d.lower()]:
                s = convert_time_to_minute(new_task.start)
                e = convert_time_to_minute(new_task.end)
                if in_tomorrow:
                    if s < r[1]:
                        return (True, d, r)
                else:
                    if r[0] <= s < r[1] or r[0] < e <= r[1] or (r[0] > s and e > r[1]):
                        return (True, d, r)

                if in_tomorrow:
                    for r in self.reserved[
                        WEEK_DAY[
                            (WEEK_DAY.index(d.capitalize()) + 1) % len(WEEK_DAY)
                        ].lower()
                    ]:
                        if r[0] < e:
                            return (
                                True,
                                WEEK_DAY[
                                    (WEEK_DAY.index(d.capitalize()) + 1) % len(WEEK_DAY)
                                ].lower(),
                                r,
                            )
        return False, None, None

    def draw(self):
        plot = Plot(self.tasks.values())
        plot.draw()


# =========== Helper functions ===========
def get_today():
    """get today in format day of week"""
    day = date.today().weekday()
    return WEEK_DAY[day]


# REPL
def repl():
    """Read-Eval-Print Loop for the interpreter."""
    interpreter = Interpreter()
    print("Welcome to Schedu REPL!")
    print("Copyright 2025 By Mohsen Lotfi")
    print("Type your commands below (type 'exit' to exit):")
    while True:
        try:
            code = input(">> ")

            if code.strip().lower() == "exit":
                print("Exiting...")
                break

            tokens = tokenize(code)
            parser = Parser(tokens)
            prog = parser.parse_program()
            for p in prog.statements:
                interpreter.execute(p)
        except Exception as e:
            print(f"{e}")


if __name__ == "__main__":
    from lexer import tokenize

    parser = argparse.ArgumentParser(description="Schedu DSL Interpreter")
    parser.add_argument("file", nargs="?", help="Path to the Schedu DSL script file")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()
        tokens = tokenize(code)
        parser = Parser(tokens)
        prog = parser.parse_program()
        interpreter = Interpreter()
        for p in prog.statements:
            interpreter.execute(p)
    else:
        repl()
