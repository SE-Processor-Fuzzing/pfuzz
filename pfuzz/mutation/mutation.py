import random
import re
import os
from typing import Callable
from typing import List


class Mutation:
    def __init__(self) -> None:
        pass

    def crossover_func(
        self, chrom1: dict[str, str], chrom2: dict[str, str]
    ) -> tuple[dict[str, str], dict[str, str]]:
        child1 = chrom1.copy()
        child2 = chrom2.copy()
        random_key = random.choice(list(chrom1.keys()))
        child1[random_key], child2[random_key] = child2[random_key], child1[random_key]
        return child1, child2

    def mutation_func(
        self, chromosome: dict[str, str], template_config: dict[str, range]
    ) -> dict[str, str]:
        child = chromosome.copy()
        random_key = random.choice(list(chromosome.keys()))
        child[random_key] = str(random.choice(template_config[random_key]))
        return child

    def fitness_func(
        self,
        chromosome: dict[str, str],
        func_generate: Callable[[dict[str, str]], None],
        func_run: Callable[[], int],
        desired_output: float,
    ) -> float:
        func_generate(chromosome)
        result = func_run()
        if result != desired_output:
            fitness = 1.0 / abs(result - desired_output)
        else:
            fitness = 1.0
        return fitness

    def population_sort(
        self, population: list[tuple[dict[str, str], float]], amount: int
    ) -> list[tuple[dict[str, str], float]]:
        sorted_list = sorted(population, key=lambda x: x[1], reverse=True)
        return sorted_list[:amount]

    def mutation(
        self,
        population: list[tuple[dict[str, str], float]],
        template_config: dict[str, range],
        amount: int,
    ) -> None:
        random_chromosomes = random.sample(population, amount)
        for element in random_chromosomes:
            result = self.mutation_func(element[0], template_config)
            population.append((result, 0.0))

    def crossover(
        self, population: list[tuple[dict[str, str], float]], amount: int
    ) -> None:
        random_chromosomes = random.sample(population, amount)
        for element in random_chromosomes:
            element2 = random.choice(random_chromosomes)
            child1, child2 = self.crossover_func(element[0], element2[0])
            population.append((child1, 0.0))
            population.append((child2, 0.0))

    def genetic_func(
        self,
        population: list[tuple[dict[str, str], float]],
        template_config: dict[str, range],
        iterations: int,
        alive: int,
        reproduce: int,
        func_generate: Callable[[dict[str, str]], None],
        func_run: Callable[[], int],
        desired_output: float,
    ) -> list[tuple[dict[str, str], float]]:

        for index, item in enumerate(population):
            result = self.fitness_func(item[0], func_generate, func_run, desired_output)
            population[index] = (item[0], result)

        for i in range(iterations):
            population = self.population_sort(population, alive)
            if population[0][1] == 1.0:
                print(i + 1)
                break
            self.crossover(population, reproduce)
            self.mutation(population, template_config, reproduce)
            for index, item in enumerate(population[-alive:]):
                result = self.fitness_func(
                    item[0], func_generate, func_run, desired_output
                )
                population[-alive + index] = (item[0], result)
        return population


RISCV_INSTRUCTIONS = [
    "add",
    "sub",
    "and",
    "or",
    "xor",
    "sll",
    "srl",
    "sra",
    "addi",
    "andi",
    "ori",
    "xori",
    "beq",
    "bne",
    "blt",
    "bge",
    "bltu",
    "bgeu",
    "lw",
    "sw",
]


class Assembly_mutation:
    def __init__(self) -> None:
        pass

    def find_labels_and_jumps(self, path: str) -> List[int]:
        label_jump_lines = []
        label_pattern = re.compile(r"^\s*\w+:\s*")
        jump_pattern = re.compile(r"^\s*(j|jal|beq|bne|blt|bge|bltu|bgeu)")

        with open(path, "r") as file:
            for line_number, line in enumerate(file):
                if label_pattern.match(line) or jump_pattern.match(line):
                    label_jump_lines.append(line_number)

        return label_jump_lines

    def assembly_crossover(
        self,
        path1: str,
        path2: str,
        labels1: List[int],
        labels2: List[int],
        generation_number: int,
        child_number: int,
    ) -> str:

        if len(labels1) < 2 or len(labels2) < 2:
            return "Малое количество базовых блоков для скрещивания"

        num1 = random.randint(0, len(labels1) - 2)
        num2 = random.randint(0, len(labels2) - 2)

        directory = os.path.dirname(path1)
        name, ext = os.path.splitext(path1)
        child_name = "-".join((str(generation_number), str(child_number)))
        child_file_path = os.path.join(directory, child_name + ext)

        with open(path1, "r") as parent, open(path2, "r") as parent2, open(
            child_file_path, "w+"
        ) as child:

            for line_number, line in enumerate(parent, start=0):
                child.write(line)
                if line_number >= labels1[num1]:
                    break

            for line_number, line in enumerate(parent2):
                if line_number >= labels2[num2 + 1]:
                    break
                if line_number >= labels2[num2] + 1:
                    child.write(line)

            for line_number, line in enumerate(parent):
                if line_number >= labels1[num1 + 1] - labels1[num1] - 1:
                    child.write(line)
        return child_file_path

    def assembly_mutate(
        self, path: str, max_mutatings: int, generation_number: int, child_number: int
    ) -> str:

        directory = os.path.dirname(path)
        name, ext = os.path.splitext(path)
        child_name = "-".join((str(generation_number), str(child_number)))
        child_file_path = os.path.join(directory, child_name + ext)

        count = max_mutatings

        with open(path, "r") as parent, open(child_file_path, "w+") as child:

            for line in parent:

                split_line = line.split()

                if (
                    not split_line
                    or split_line[0].startswith("#")
                    or split_line[0].startswith(".")
                    or re.compile(r"^\s*\w+:\s*").match(line)
                ):
                    child.write(line)
                else:
                    if count > 0 and random.random() > 0.3:
                        split_line[0] = random.choice(RISCV_INSTRUCTIONS)
                        child.write("\t" + " ".join(split_line) + "\n")
                        count -= 1
                    else:
                        child.write(line)
        return child_file_path
