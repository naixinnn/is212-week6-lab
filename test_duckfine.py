import unittest

from duckfine import DuckFine


class TestDuckFineInit(unittest.TestCase):

    def test_stores_member_id(self):
        fine = DuckFine("M001")
        self.assertEqual(fine.member_id, "M001")

    def test_new_account_owes_nothing(self):
        fine = DuckFine("M001")
        self.assertEqual(fine.total_owed, 0.0)


class TestDuckFineGracePeriod(unittest.TestCase):

    def setUp(self):
        self.fine = DuckFine("M001")

    def test_on_time_return_is_free(self):
        self.assertEqual(self.fine.charge(0), 0.0)

    def test_one_day_late_is_forgiven(self):
        self.assertEqual(self.fine.charge(1), 0.0)

    def test_two_days_late_is_forgiven(self):
        # Boundary: last day of the grace period
        self.assertEqual(self.fine.charge(2), 0.0)

    def test_deluxe_within_grace_period_is_free(self):
        self.assertEqual(self.fine.charge(2, deluxe=True), 0.0)


class TestDuckFineStandardFees(unittest.TestCase):

    def setUp(self):
        self.fine = DuckFine("M001")

    def test_three_days_late_charges_one_day(self):
        # Boundary: first chargeable day
        self.assertAlmostEqual(self.fine.charge(3), 0.50)

    def test_five_days_late_charges_three_days(self):
        self.assertAlmostEqual(self.fine.charge(5), 1.50)

    def test_twelve_days_late_hits_cap_exactly(self):
        # 10 chargeable days * 0.50 = 5.00
        self.assertAlmostEqual(self.fine.charge(12), 5.00)

    def test_thirteen_days_late_is_capped(self):
        # 11 chargeable days * 0.50 = 5.50, capped to 5.00
        self.assertAlmostEqual(self.fine.charge(13), 5.00)

    def test_very_late_return_is_capped(self):
        self.assertAlmostEqual(self.fine.charge(365), 5.00)


class TestDuckFineDeluxeFees(unittest.TestCase):

    def setUp(self):
        self.fine = DuckFine("M001")

    def test_deluxe_doubles_the_daily_fee(self):
        self.assertAlmostEqual(self.fine.charge(3, deluxe=True), 1.00)

    def test_deluxe_five_days_late(self):
        self.assertAlmostEqual(self.fine.charge(5, deluxe=True), 3.00)

    def test_deluxe_seven_days_late_hits_cap_exactly(self):
        # 5 chargeable days * 0.50 * 2 = 5.00
        self.assertAlmostEqual(self.fine.charge(7, deluxe=True), 5.00)

    def test_deluxe_eight_days_late_is_capped(self):
        # 6 chargeable days * 0.50 * 2 = 6.00, capped to 5.00
        self.assertAlmostEqual(self.fine.charge(8, deluxe=True), 5.00)

    def test_deluxe_false_by_default(self):
        self.assertAlmostEqual(self.fine.charge(3), self.fine.charge(3, deluxe=False))


class TestDuckFineInvalidInput(unittest.TestCase):

    def setUp(self):
        self.fine = DuckFine("M001")

    def test_negative_days_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.fine.charge(-1)

    def test_negative_days_does_not_change_total(self):
        with self.assertRaises(ValueError):
            self.fine.charge(-1)
        self.assertEqual(self.fine.total_owed, 0.0)


class TestDuckFineAccumulation(unittest.TestCase):

    def setUp(self):
        self.fine = DuckFine("M001")

    def test_charge_adds_fee_to_total(self):
        self.fine.charge(5)
        self.assertAlmostEqual(self.fine.total_owed, 1.50)

    def test_multiple_charges_accumulate(self):
        self.fine.charge(5)                 # 1.50
        self.fine.charge(3, deluxe=True)    # 1.00
        self.assertAlmostEqual(self.fine.total_owed, 2.50)

    def test_forgiven_charge_does_not_change_total(self):
        self.fine.charge(2)
        self.assertEqual(self.fine.total_owed, 0.0)

    def test_total_can_exceed_single_fine_cap(self):
        # The cap applies per fine, not to the account total
        self.fine.charge(20)
        self.fine.charge(20)
        self.assertAlmostEqual(self.fine.total_owed, 10.00)

    def test_accounts_are_independent(self):
        other = DuckFine("M002")
        self.fine.charge(5)
        self.assertEqual(other.total_owed, 0.0)


if __name__ == "__main__":
    unittest.main()