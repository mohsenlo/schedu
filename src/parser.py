from dataclasses import dataclass

# AST (Abstract Syntax Tree)


@dataclass
class Program:
    statements: list[object]


@dataclass
class TaskTime:
    start: str = None
    end: str = None
    duration: str = None
    after: str = None


@dataclass
class TaskSt:
    """This is a model for tasks statements (create, update, ...)
    * if update = True, mean this is not for creating task, is for update an old task (Default is False)
    """

    name: str
    time: TaskTime
    days: list[str] = None
    update: bool = False


@dataclass
class RenameTask:
    old: str
    new: str


@dataclass
class Print:
    """* if today = True, mean print today events and ignore target_name. (Default is False)"""

    target_name: str
    today: bool = False


@dataclass
class Draw:
    """Represent draw statement"""

    pass


# constant
WEEK_DAYS = (
    "SATURDAY",
    "SUNDAY",
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
    "FRIDAY",
)


# Parser
class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    def peek(self):
        """This return current token name, where parser position is on it.
        when reach end of code, return None"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos][0]
        return None

    def expect(self, kind):
        """This first check parser is on that position we excepted?\n
        if yes, return current token value (not name) and go on next token,\n
        else raise Syntax Error."""
        if self.peek() == kind:
            value = self.tokens[self.pos][1]
            self.pos += 1
            return value
        raise SyntaxError(f"Expected {kind}, got {self.peek()}")

    def parse_program(self):
        """Start point of each statement"""
        statements = []
        while self.peek() is not None:
            kind = self.peek()
            if kind == "TASK":
                statements.append(self.parse_task())
            elif kind == "UPDATE":
                statements.append(self.parse_update())
            elif kind == "RENAME":
                statements.append(self.parse_rename())
            elif kind == "PRINT":
                statements.append(self.parse_print())
            elif kind == "WEEK_DAY":
                statements.extend(self.parse_batch_task_for_days())
            elif kind == "DRAW":
                statements.append(self.parse_draw())
            else:
                raise SyntaxError(f"Unknown statement, Starting with {kind}")
        return Program(statements)

    def parse_task(self, with_day: bool = True):
        """* Should set with_day = False When check batch_task statements, otherwise keep it default (True)"""
        self.expect("TASK")
        name = self.expect("STRING")  # parse name of task
        # parse time of task
        time = None
        days = None
        if self.peek() in ("FROM", "AT", "DURATION"):
            if self.peek() == ("DURATION"):
                # When start define task time with DURATION, dont need day, because statement should have AFTER event_name
                with_day = False
            time = self.parse_task_time()
        else:
            raise SyntaxError("Invalid statement, Expected time for task")

        if with_day:
            if self.peek() == "IN":
                self.expect("IN")
                days = self.parse_day_list()
            else:
                raise SyntaxError("Invalid statement, Excepted days for task")

        return TaskSt(name, time, days)

    def parse_task_time(self):
        """*This only handle when time start with FROM and AT (not handle duration)"""
        if self.peek() == "FROM":
            self.expect("FROM")
            start = self.expect("TIME")
            self.expect("TO")
            end = self.expect("TIME")
            return TaskTime(start, end)
        elif self.peek() == "AT":
            self.expect("AT")
            at = self.expect("TIME")
            self.expect("DURATION")
            duration = self.expect("TIME")
            return TaskTime(at, duration=duration)
        elif self.peek() == "DURATION":
            self.expect("DURATION")
            duration = self.expect("TIME")
            self.expect("AFTER")
            after = self.expect("STRING")
            return TaskTime(duration=duration, after=after)

    def parse_day_list(self):
        days = [self.expect("WEEK_DAY")]  # get first day
        while self.peek() == "AND":
            self.expect("AND")
            days.append(self.expect("WEEK_DAY"))  # append next days
        return days

    def parse_batch_task_for_days(self):
        days = self.parse_day_list()
        self.expect("OPEN_CURLY_BRACKET")  # start block of batch tasks
        tasks = []
        while self.peek() == "TASK":
            task = self.parse_task(with_day=False)
            task.days = days
            tasks.append(task)
            if self.peek() == "CLOSE_CURLY_BRACKET":
                break
        self.expect("CLOSE_CURLY_BRACKET")  # end block of batch tasks
        return tasks

    def parse_update(self):
        self.expect("UPDATE")
        self.expect("TASK")
        name = self.expect("STRING")
        time = None
        days = None
        with_day = True
        have_option = False
        if self.peek() in ("FROM", "AT", "DURATION"):
            if self.peek() == "DURATION":
                with_day = False
            time = self.parse_task_time()
            have_option = True
        if with_day and self.peek() == "IN":
            self.expect("IN")
            days = self.parse_day_list()
            have_option = True
        if not have_option:
            raise RuntimeError("Excepted some option (time or date) for update")
        return TaskSt(name, time, days, True)

    def parse_rename(self):
        self.expect("RENAME")
        self.expect("TASK")
        old = self.expect("STRING")
        self.expect("TO")
        new = self.expect("STRING")
        return RenameTask(old, new)

    def parse_print(self):
        self.expect("PRINT")
        if self.peek() == "TODAY":
            self.expect("TODAY")
            return Print("today", True)
        elif self.peek() == "TASK":
            self.expect("TASK")
            name = self.expect("STRING")
            return Print(name)
        else:
            raise SyntaxError("Invalid print command")

    def parse_draw(self):
        self.expect("DRAW")
        return Draw()
