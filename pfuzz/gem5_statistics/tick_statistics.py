from dataclasses import dataclass
from typing import List


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

        tick_number: int
        fetched_during_this_tick: int
        decoded_during_this_tick: int
        retired_during_this_tick: int
        fetched_overall_by_this_tick: int
        decoded_overall_by_this_tick: int
        retired_overall_by_this_tick: int

    def get_tick_statistics_list(path_to_trace: str) -> List[_Tick]:
        """
        Function for aquiring the information for each tick from a given trace
        in a form of a list of instances of Tick dataclass

        :path_to_trace: path to where the examined trace is stored
        :return: list with Tick dataclass instances containing information for each tick from trace
        """
        return []
