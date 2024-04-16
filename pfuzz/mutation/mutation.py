import random
from typing import Callable


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
