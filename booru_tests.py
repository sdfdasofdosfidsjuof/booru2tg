import unittest
import booru


class MyTestCase(unittest.TestCase):
    def test_get_ids_by_tag(self):
        with open("db/niko_%28oneshot%29.txt", mode="r") as file_:
            links = file_.readlines()
        self.assertEqual(
            booru.get_ids_by_tag('niko_%28oneshot%29'),
            links)  # add assertion here

    def test_get_image_link(self):
        self.assertEqual(
            'https://safebooru.org//samples/3499/sample_1ad3cb6d2ed11168be23a9b50ced029410132667.jpg?3640425',
            booru.get_image_link_by_id('3640425'))  # add assertion here


if __name__ == '__main__':
    unittest.main()
