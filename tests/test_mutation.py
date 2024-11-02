import unittest
import tempfile
import os
import re
from unittest.mock import Mock

from pfuzz.mutation.mutation import Mutation
from pfuzz.mutation.mutation import Assembly_mutation, RISCV_INSTRUCTIONS


def count_differences(chrom_a: dict[str, str], chrom_b: dict[str, str]) -> int:
    return sum(1 for key in chrom_a if chrom_a[key] != chrom_b[key])


class TestMutation(unittest.TestCase):
    def setUp(self) -> None:
        self.mutation = Mutation()

        self.chrom1 = {"gene1": "1", "gene2": "2", "gene3": "3"}
        self.chrom2 = {"gene1": "4", "gene2": "5", "gene3": "5"}

        self.template_config = {
            "gene1": range(1, 5),
            "gene2": range(1, 5),
            "gene3": range(1, 5),
        }

        self.func_generate = Mock()
        self.func_run = Mock()

    def test_crossover_func(self) -> None:
        child1, child2 = self.mutation.crossover_func(self.chrom1, self.chrom2)

        self.assertLessEqual(count_differences(child1, self.chrom1), 1)
        self.assertLessEqual(count_differences(child2, self.chrom2), 1)

        self.assertEqual(set(child1.keys()), set(self.chrom1.keys()))
        self.assertEqual(set(child2.keys()), set(self.chrom2.keys()))

    def test_mutation_func(self) -> None:
        child1 = self.mutation.mutation_func(self.chrom1, self.template_config)
        child2 = self.mutation.mutation_func(self.chrom2, self.template_config)

        self.assertLessEqual(count_differences(child1, self.chrom1), 1)
        self.assertLessEqual(count_differences(child2, self.chrom2), 1)

        self.assertEqual(set(child1.keys()), set(self.chrom1.keys()))
        self.assertEqual(set(child2.keys()), set(self.chrom2.keys()))

    def test_fitness_func(self) -> None:
        self.func_run.return_value = 8
        desired_output = 10

        fitness = self.mutation.fitness_func(
            self.chrom1, self.func_generate, self.func_run, desired_output
        )
        self.assertAlmostEqual(fitness, 1.0 / abs(8 - 10), places=4)

        self.func_run.return_value = 10
        fitness = self.mutation.fitness_func(
            self.chrom1, self.func_generate, self.func_run, desired_output
        )
        self.assertEqual(fitness, 1.0)

    def test_population_sort(self) -> None:
        population = [
            ({"gene1": "1"}, 0.1),
            ({"gene1": "2"}, 0.5),
            ({"gene1": "3"}, 0.2),
            ({"gene1": "4"}, 0.7),
        ]
        sorted_population = self.mutation.population_sort(population, 2)
        self.assertEqual(
            sorted_population, [({"gene1": "4"}, 0.7), ({"gene1": "2"}, 0.5)]
        )

    def test_mutation(self) -> None:
        population = [
            ({"gene1": "1", "gene2": "2", "gene3": "3"}, 0.0),
            ({"gene1": "4", "gene2": "5", "gene3": "6"}, 0.0),
        ]
        self.mutation.mutation(population, self.template_config, 1)
        self.assertEqual(len(population), 3)

    def test_crossover(self) -> None:
        population = [
            ({"gene1": "1", "gene2": "2", "gene3": "3"}, 0.0),
            ({"gene1": "4", "gene2": "5", "gene3": "6"}, 0.0),
        ]
        self.mutation.crossover(population, 1)
        self.assertEqual(len(population), 4)

    def test_genetic_func(self) -> None:
        population = [
            ({"gene1": "1", "gene2": "2", "gene3": "3"}, 0.0),
            ({"gene1": "4", "gene2": "5", "gene3": "6"}, 0.0),
        ]

        self.func_run.return_value = 10
        desired_output = 10

        result_population = self.mutation.genetic_func(
            population,
            self.template_config,
            iterations=10,
            alive=1,
            reproduce=2,
            func_generate=self.func_generate,
            func_run=self.func_run,
            desired_output=desired_output,
        )

        self.assertEqual(result_population[0][1], 1.0)
        self.assertEqual(len(result_population), 1)


class TestAssemblyMutation(unittest.TestCase):

    def setUp(self) -> None:
        self.assembly_mutation = Assembly_mutation()

        self.temp_file1 = tempfile.NamedTemporaryFile(delete=False, mode="w+")
        self.temp_file2 = tempfile.NamedTemporaryFile(delete=False, mode="w+")

        self.temp_file1.writelines(
            [
                "main:\n",
                "    add x1, x2, x3\n",
                "loop:\n",
                "    beq x1, x2, end\n",
                "    addi x1, x1, 1\n",
                "end:\n",
                "    xor x4, x5, x6\n",
            ]
        )

        self.temp_file2.writelines(
            [
                "start:\n",
                "    lw x1, 0(x2)\n",
                "    sw x3, 0(x4)\n",
                "next:\n",
                "    bne x1, x2, start\n",
                "finish:\n",
                "    sub x3, x3, x4\n",
            ]
        )

        self.temp_file1.close()
        self.temp_file2.close()

    def tearDown(self) -> None:
        os.remove(self.temp_file1.name)
        os.remove(self.temp_file2.name)

    def test_find_labels_and_jumps(self) -> None:
        labels = self.assembly_mutation.find_labels_and_jumps(self.temp_file1.name)
        expected_lines = [0, 2, 3, 5]
        self.assertEqual(labels, expected_lines)

    def test_assembly_crossover(self) -> None:

        labels1 = self.assembly_mutation.find_labels_and_jumps(self.temp_file1.name)
        labels2 = self.assembly_mutation.find_labels_and_jumps(self.temp_file2.name)

        generation_number = 1
        child_number = 1

        child_file_path = self.assembly_mutation.assembly_crossover(
            self.temp_file1.name,
            self.temp_file2.name,
            labels1,
            labels2,
            generation_number,
            child_number,
        )

        self.assertTrue(os.path.exists(child_file_path))

        with open(child_file_path, "r") as child:
            child_content = child.read()
            self.assertNotEqual(child_content, "")

        os.remove(child_file_path)

    def test_assembly_mutate(self) -> None:
        generation_number = 1
        child_number = 2
        max_mutations = 2

        child_file_path = self.assembly_mutation.assembly_mutate(
            self.temp_file1.name, max_mutations, generation_number, child_number
        )

        self.assertTrue(os.path.exists(child_file_path))

        with open(child_file_path, "r") as child:
            child_content = child.readlines()

        with open(self.temp_file1.name, "r") as original:
            original_content = original.readlines()

        mutation_count = sum(
            1
            for orig_line, mut_line in zip(original_content, child_content)
            if orig_line != mut_line and mut_line.split()[0] in RISCV_INSTRUCTIONS
        )

        self.assertLessEqual(mutation_count, max_mutations)

        os.remove(child_file_path)
