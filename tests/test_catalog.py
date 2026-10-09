"""Platform authority boundary; fixtures are not runtime-generated capabilities."""
import unittest
from workbench.catalog import check_result
from workbench.model import RunError


class CatalogBoundaries(unittest.TestCase):
    def setUp(self):
        self.record = {"id": "clean_rows", "version": 2, "input_fields": ["rows"],
                       "active": True, "tested": True, "permissions": ["compute"]}
        self.entry = {"id": "clean_rows", "version": 2, "input_fields": ["rows"], "terms": ["clean"]}

    def test_selection_cannot_resurrect_old_or_disabled_versions(self):
        old = {**self.record, "version": 1, "active": False}
        check_result([old, self.record], {"index": [self.entry], "matches": ["clean_rows"]}, ["rows"])
        with self.assertRaises(RunError):
            check_result([old, self.record], {"index": [{**self.entry, "version": 1}], "matches": []}, [])
        with self.assertRaises(RunError):
            check_result([{**self.record, "active": False}], {"index": [self.entry], "matches": ["clean_rows"]}, [])

    def test_helper_cannot_rewrite_interfaces_or_grant_permissions(self):
        with self.assertRaises(RunError):
            check_result([self.record], {"index": [{**self.entry, "input_fields": ["password"]}], "matches": []}, [])
        with self.assertRaises(RunError):
            check_result([{**self.record, "permissions": ["compute", "network"]}], {"index": [self.entry], "matches": []}, [])
        with self.assertRaises(RunError):
            check_result([self.record], {"index": [self.entry], "matches": ["clean_rows"]}, ["unknown"])

    def test_no_missing_duplicate_or_invented_entries(self):
        for output in [{"index": [], "matches": []},
                       {"index": [self.entry, self.entry], "matches": []},
                       {"index": [self.entry], "matches": ["made_up"]}]:
            with self.assertRaises(RunError):
                check_result([self.record], output, [])


if __name__ == "__main__":
    unittest.main()
