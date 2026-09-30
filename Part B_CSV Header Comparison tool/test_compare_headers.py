import os
import tempfile
import unittest

from compare_headers import HeaderError, compare_headers, main, read_headers


def write(content):
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    with open(path, "w") as f:
        f.write(content)
    return path


class CompareLogicTests(unittest.TestCase):
    def test_identical_headers(self):
        r = compare_headers(["a", "b"], ["a", "b"])
        self.assertEqual(r["only_in_expected"], [])
        self.assertEqual(r["only_in_actual"], [])
        self.assertEqual(r["common"], ["a", "b"])
        self.assertTrue(r["same_order"])

    def test_missing_header(self):
        r = compare_headers(["a", "b", "c"], ["a", "c", "d"])
        self.assertEqual(r["only_in_expected"], ["b"])
        self.assertEqual(r["only_in_actual"], ["d"])
        self.assertEqual(r["common"], ["a", "c"])

    def test_different_order(self):
        r = compare_headers(["a", "b", "c"], ["c", "a", "b"])
        self.assertFalse(r["same_order"])
        self.assertEqual(sorted(r["common"]), ["a", "b", "c"])

    def test_extra_spaces_are_trimmed(self):
        path = write("  a ,b  , c\n1,2,3\n")
        self.assertEqual(read_headers(path), ["a", "b", "c"])

    def test_windows_line_endings(self):
        fd, path = tempfile.mkstemp(suffix=".csv"); os.close(fd)
        with open(path, "wb") as f:
            f.write(b"a,b,c\r\n1,2,3\r\n")
        self.assertEqual(read_headers(path), ["a", "b", "c"])

    def test_sample_files(self):
        here = os.path.dirname(os.path.abspath(__file__))
        exp = read_headers(os.path.join(here, "expected_orders.csv"))
        act = read_headers(os.path.join(here, "actual_orders.csv"))
        r = compare_headers(exp, act)
        self.assertEqual(r["only_in_expected"], ["amount", "created_at", "country"])
        self.assertEqual(r["only_in_actual"], ["total_amount", "processed_at", "country_code"])
        self.assertEqual(r["common"], ["order_id", "customer_id", "currency", "status"])
        self.assertTrue(r["same_order"])


class ErrorTests(unittest.TestCase):
    def test_missing_argument(self):
        self.assertEqual(main(["only_one.csv"]), 2)
        self.assertEqual(main([]), 2)

    def test_file_not_found(self):
        with self.assertRaisesRegex(HeaderError, "not found"):
            read_headers("definitely_missing.csv")
        self.assertEqual(main(["missing1.csv", "missing2.csv"]), 1)

    def test_empty_file(self):
        with self.assertRaisesRegex(HeaderError, "empty"):
            read_headers(write(""))

    def test_no_valid_headers(self):
        for content in [",,,\n", "   \n", " , , \n"]:
            with self.assertRaisesRegex(HeaderError, "no valid headers"):
                read_headers(write(content))


if __name__ == "__main__":
    unittest.main()
