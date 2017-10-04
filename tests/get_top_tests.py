import unittest
import methods


class TestGetTopMethods(unittest.TestCase):

    def test_simple_order(self):
        var = [('first', 6), ('second', 5), ('third', 4), ('fourth', 3), ('fifth', 2), ('sixth', 1),
               ('seventh', 0)]
        msg = methods.get_top._create_top(var)
        s = [x for x in msg.split('\n') if x]
        self.assertEqual(len(s), 7)
        print(msg)

    def test_duplicate_last(self):
        var = [('first', 6), ('second', 5), ('third', 4), ('fourth', 3), ('fifth', 3), ('sixth', 1),
               ('seventh', 0)]
        msg = methods.get_top._create_top(var)
        s = [x for x in msg.split('\n') if x]
        self.assertEqual(len(s), 7)
        print(msg)

    def test_duplicate_fourth(self):
        var = [('first', 6), ('second', 5), ('third', 4), ('fourth', 4), ('fifth', 3), ('sixth', 1),
               ('seventh', 0)]
        msg = methods.get_top._create_top(var)
        s = [x for x in msg.split('\n') if x]
        self.assertEqual(len(s), 7)
        print(msg)

    def test_duplicate_several(self):
        var = [('first', 6), ('second', 6), ('third', 5), ('fourth', 5), ('fifth', 3), ('sixth', 1),
               ('seventh', 0)]
        msg = methods.get_top._create_top(var)
        s = [x for x in msg.split('\n') if x]
        self.assertEqual(len(s), 7)
        print(msg)

    def test_duplicate_first_and_last(self):
        var = [('first', 6), ('second', 6), ('third', 5), ('fourth', 4), ('fifth', 4), ('sixth', 1),
               ('seventh', 0)]
        msg = methods.get_top._create_top(var)
        s = [x for x in msg.split('\n') if x]
        self.assertEqual(len(s), 7)
        print(msg)


if __name__ == '__main__':
    unittest.main()
