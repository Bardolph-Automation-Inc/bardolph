import logging
from pathlib import Path
from typing import Self

from bardolph.lib.job_control import Job
from bardolph.parser.parse import Parser
from bardolph.vm.machine import Machine, MachineState


class ScriptJob(Job):
    def __init__(self):
        super().__init__()
        self._program = None
        self._parser = Parser()
        self._machine = Machine()

    @staticmethod
    def from_string(script: str) -> Self:
        new_instance = ScriptJob()
        new_instance.load_string(script)
        return new_instance

    @staticmethod
    def from_path(path: Path) -> Self:
        new_instance = ScriptJob()
        new_instance.load_file(path)
        return new_instance

    def execute(self) -> None:
        if self._program is not None:
            self._machine.reset()
            self._machine.run(self._program)

    def request_stop(self) -> None:
        self._machine.stop()

    def load_file(self, path: Path):
        if self._parser.parse_file(path):
            self._program = self._parser.get_program()
        else:
            logging.error("{}, {}".format(path.name, self._parser.get_errors()))
            self._program = []
        return self._program

    def load_string(self, input_string):
        if self._parser.parse(input_string):
            self._program = self._parser.get_program()
        else:
            logging.error(self._parser.get_errors())
            self._program = []
        return self._program

    @property
    def program(self):
        return self._program

    @property
    def compile_errors(self):
        return self._parser.get_errors()

    def get_machine_state(self) -> MachineState:
        return self._machine.get_state()
