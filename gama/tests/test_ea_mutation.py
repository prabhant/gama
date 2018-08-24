import unittest

from deap import gp

from gama.configuration.testconfiguration import clf_config
from gama.ea.automl_gp import compile_individual
from gama.ea.mutation import mut_replace_primitive, mut_replace_terminal, find_unmatched_terminal
from gama import GamaClassifier


def mutation_test_suite():
    test_cases = [MutationTestCase]
    return unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase, test_cases))


class MutationTestCase(unittest.TestCase):
    """ Unit Tests for ea/mutation.py

    Functions excluded:
        [ ] random_valid_mutation
    """

    def setUp(self):
        self.gama = GamaClassifier(random_state=0, config=clf_config)

        self.ind_strings = [
            "GaussianNB(data)",
            """RandomForestClassifier(
            FeatureAgglomeration(
                    data,
                    FeatureAgglomeration.linkage='complete',
                    FeatureAgglomeration.affinity='l2'), 
            RandomForestClassifier.n_estimators=100, 
            RandomForestClassifier.criterion='gini', 
            RandomForestClassifier.max_features=0.6000000000000001, 
            RandomForestClassifier.min_samples_split=6, 
            RandomForestClassifier.min_samples_leaf=7, 
            RandomForestClassifier.bootstrap=True)""",
            """LinearSVC(data,
            LinearSVC.penalty='l2',
            LinearSVC.loss='squared_hinge',
            LinearSVC.dual=True,
            LinearSVC.tol=1e-05,
            LinearSVC.C=0.001)"""
        ]

        self.individuals = {
            ind_str: gp.PrimitiveTree.from_string(ind_str, self.gama._pset)
            for ind_str in self.ind_strings
        }

    def tearDown(self):
        self.gama.delete_cache()

    def test_find_unmatched_terminal(self):

        # (data) -> immediately missing
        pruned_ind = self.individuals[self.ind_strings[0]][1:]
        self.assertEqual(find_unmatched_terminal(pruned_ind), 0)

        # FA(data, FA_t1, FA_t2), RFC_t1,...,RFC_tN -> 4
        pruned_ind = self.individuals[self.ind_strings[1]][1:]
        self.assertEqual(find_unmatched_terminal(pruned_ind), 4)

        # RFC(__(data, FA_t1, FA_t2), RFC_t1,...,RFC_tN -> 1
        pruned_ind = self.individuals[self.ind_strings[1]][:1] + self.individuals[self.ind_strings[1]][2:]
        self.assertEqual(find_unmatched_terminal(pruned_ind), 2)

    def test_mut_replace_terminal(self):
        """ Tests if mut_replace_terminal replaces exactly one terminal. """
        ind = self.individuals[self.ind_strings[1]]
        ind_clone = self.gama._toolbox.clone(ind)
        new_ind, = mut_replace_terminal(ind_clone, self.gama._pset)

        replaced_elements = [el1 for el1, el2 in zip(ind, new_ind) if el1.name != el2.name]

        self.assertEqual(len(replaced_elements), 1,
                         "Exactly one component should be replaced. Found {}".format(replaced_elements))
        self.assertTrue(isinstance(replaced_elements[0], gp.Terminal),
                        "Replaced component should be a terminal, is {}".format(type(replaced_elements[0])))
        # Should be able to compile the individual.
        compile_individual(new_ind, self.gama._pset)

    def test_mut_replace_primitive_len_1_no_terminal(self):
        """ Tests if mut_replace_primitive replaces exactly one primitive. """
        ind = self.individuals[self.ind_strings[1]]
        ind_clone = self.gama._toolbox.clone(ind)
        new_ind, = mut_replace_primitive(ind_clone, self.gama._pset)

        replaced_primitives = [el1 for el1, el2 in zip(ind, new_ind) if
                               (el1.name != el2.name and isinstance(el1, gp.Primitive))]

        self.assertEqual(len(replaced_primitives), 1,
                         "Exactly one primitive should be replaced. Found {}".format(replaced_primitives))
        # Should be able to compile the individual.
        compile_individual(new_ind, self.gama._pset)

        ind = self.individuals[self.ind_strings[2]]
        ind_clone = self.gama._toolbox.clone(ind)
        new_ind, = mut_replace_primitive(ind_clone, self.gama._pset)

        replaced_primitives = [el1 for el1, el2 in zip(ind, new_ind) if
                               (el1.name != el2.name and isinstance(el1, gp.Primitive))]

        self.assertEqual(len(replaced_primitives), 1,
                         "Exactly one primitive should be replaced. Found {}".format(replaced_primitives))
        # Should be able to compile the individual.
        compile_individual(new_ind, self.gama._pset)

    def test_mut_replace_primitive_len_2(self):
        """ Tests if mut_replace_primitive replaces exactly one primitive. """
        ind = self.individuals[self.ind_strings[1]]
        ind_clone = self.gama._toolbox.clone(ind)
        new_ind, = mut_replace_primitive(ind_clone, self.gama._pset)

        replaced_primitives = [el1 for el1, el2 in zip(ind, new_ind) if
                               (el1.name != el2.name and isinstance(el1, gp.Primitive))]

        self.assertEqual(len(replaced_primitives), 1,
                         "Exactly one primitive should be replaced. Found {}".format(replaced_primitives))
        try:
            # Should be able to compile the individual.
            compile_individual(new_ind, self.gama._pset)
        except Exception as e:
            self.fail(
                f"""Mutated individual could not be compiled because of error: {str(e)}\n
                Original: {str(ind)}\n
                New: {str(new_ind)}
                """
            )
