import m5
from dataclasses import dataclass
from typing import Dict, List


class Tick_statistics:
    def __init__(self) -> None:
        pass

    """
    Class containing all the neccessary tools
    to gather O3 pipeline statistics
    """

    @dataclass
    class _Tick:
        """
        Dataclass for storing information regarding a tick, such as its number,
        how many instructions were executed during this tick and up to this tick
        """

        tick_number: int = 0
        fetched_during_this_tick: int = 0
        decoded_during_this_tick: int = 0
        renamed_during_this_tick: int = 0
        dispatched_during_this_tick: int = 0
        issued_during_this_tick: int = 0
        completed_during_this_tick: int = 0
        retired_during_this_tick: int = 0
        stored_during_this_tick: int = 0

        fetched_so_far: int = 0
        decoded_so_far: int = 0
        renamed_so_far: int = 0
        dispatched_so_far: int = 0
        issued_so_far: int = 0
        completed_so_far: int = 0
        retired_so_far: int = 0
        stored_so_far: int = 0

    def update_so_far_stages_numbers(
        self, ticks: Dict[str, _Tick], tick_number: str
    ) -> None:
        ticks[tick_number].fetched_so_far = ticks["so_far"].fetched_so_far
        ticks[tick_number].decoded_so_far = ticks["so_far"].decoded_so_far
        ticks[tick_number].renamed_so_far = ticks["so_far"].renamed_so_far
        ticks[tick_number].dispatched_so_far = ticks["so_far"].dispatched_so_far
        ticks[tick_number].issued_so_far = ticks["so_far"].issued_so_far
        ticks[tick_number].completed_so_far = ticks["so_far"].completed_so_far
        ticks[tick_number].retired_so_far = ticks["so_far"].retired_so_far
        ticks[tick_number].stored_so_far = ticks["so_far"].stored_so_far

    def proccess_stage(
        self, stage: str, ticks: Dict[str, _Tick], current_tick: str
    ) -> str:
        stage = stage.removeprefix("O3PipeView:")
        prefix = stage[0:3]
        tick_number = (
            stage.split(":")[1].rstrip()
            if stage.split(":")[1].rstrip() != "0"
            else current_tick
        )

        if tick_number not in ticks:
            ticks[tick_number] = self._Tick()

        if prefix == "fet":
            ticks[tick_number].tick_number = int(tick_number)
            ticks[tick_number].fetched_during_this_tick += 1
            ticks["so_far"].fetched_so_far += 1
        elif prefix == "dec":
            ticks[tick_number].tick_number = int(tick_number)
            ticks[tick_number].decoded_during_this_tick += 1
            ticks["so_far"].decoded_so_far += 1
        elif prefix == "ren":
            ticks[tick_number].tick_number = int(tick_number)
            ticks[tick_number].renamed_during_this_tick += 1
            ticks["so_far"].renamed_so_far += 1
        elif prefix == "dis":
            ticks[tick_number].tick_number = int(tick_number)
            ticks[tick_number].dispatched_during_this_tick += 1
            ticks["so_far"].dispatched_so_far += 1
        elif prefix == "iss":
            ticks[tick_number].tick_number = int(tick_number)
            ticks[tick_number].issued_during_this_tick += 1
            ticks["so_far"].issued_so_far += 1
        elif prefix == "com":
            ticks[tick_number].tick_number = int(tick_number)
            ticks[tick_number].completed_during_this_tick += 1
            ticks["so_far"].completed_so_far += 1
        elif prefix == "ret":
            ticks[tick_number].tick_number = int(tick_number)
            ticks[tick_number].retired_during_this_tick += 1
            ticks["so_far"].retired_so_far += 1

            retire_tick = tick_number
            self.update_so_far_stages_numbers(ticks, retire_tick)

            tick_number = (
                stage.split(":")[3].rstrip()
                if stage.split(":")[3].rstrip() != "0"
                else retire_tick
            )

            if tick_number not in ticks:
                ticks[tick_number] = self._Tick()

            ticks[tick_number].tick_number = int(tick_number)
            ticks[tick_number].stored_during_this_tick += 1
            ticks["so_far"].stored_so_far += 1

        self.update_so_far_stages_numbers(ticks, tick_number)
        return tick_number

    def get_tick_statistics_list(self, path_to_trace: str) -> List[_Tick]:
        """
        Function for aquiring the information for each tick from a given trace
        in a form of a dictionary of instances of Tick dataclass

        :path_to_trace: path to where the examined trace is stored
        :return: dictionary with Tick dataclass instances containing information for each tick from trace
        """
        ticks = {}
        ticks["so_far"] = self._Tick()

        with open(path_to_trace, "r") as trace:

            lines = trace.readlines()
            current_tick = "0"

            for line in lines:
                old_tick = current_tick
                current_tick = self.proccess_stage(line, ticks, old_tick)

        tick_list = list(ticks.values())
        tick_list.sort(key=lambda x: x.tick_number)
        return tick_list

    def get_longest_tick_sequence_without_retired(
        self,
        ticks_list: List[_Tick],
    ) -> List[int]:
        count, count_max = 0, 0
        tick_sequence, longest_tick_sequence = [], []

        for tick in ticks_list:
            if tick.retired_during_this_tick == 0:
                count += 1
                tick_sequence.append(tick.tick_number)
            else:
                if count >= count_max:
                    count = count_max
                    longest_tick_sequence = tick_sequence
                    tick_sequence = []
                    count = 0
        longest_tick_sequence.reverse()
        return longest_tick_sequence

    def get_stats_for_certain_ticks_exclusively(self, ticks: List[int]) -> None:
        """Function to be put into simulation to generate stats for each
        tick exclusively in stats.txt (not commulative stats)"""
        for tick in ticks:
            while True:
                if m5.curTick() == tick - 1000:
                    m5.stats.reset()
                if m5.curTick() == tick:
                    m5.stats.dump()
                    break
                m5.simulate(1000)
