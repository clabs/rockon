from __future__ import annotations

from django.test import SimpleTestCase

from rockon.library.federal_states import FederalState


class FederalStateTests(SimpleTestCase):
    def test_has_sixteen_states_plus_non_german_option(self):
        self.assertEqual(len(FederalState.choices), 17)

    def test_non_german_option_is_present(self):
        self.assertIn(('XX', 'Nicht in Deutschland'), FederalState.choices)

    def test_values_are_unique(self):
        values = [value for value, _label in FederalState.choices]
        self.assertEqual(len(values), len(set(values)))
