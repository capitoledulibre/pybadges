import unittest
from pybadges.pybadges import Person, sort_persons_for_printing

class TestSortPersonsForPrinting(unittest.TestCase):
    # def test_sort_8_persons(self):
    #     """Test sorting with 8 persons (2 pages)"""
    #     # Create 8 test persons
    #     persons = [
    #         Person("front.png", "back.png", f"Name {i}", f"Last {i}", f"Soc {i}")
    #         for i in range(0, 8)
    #     ]
        
    #     # Shuffle to ensure sorting works
    #     import random
    #     random.shuffle(persons)
        
    #     # Sort for printing
    #     sorted_persons = sort_persons_for_printing(persons)
        
    #     # Expected order: position 1 across pages, then position 2, etc.
    #     expected_order = [
    #         "Soc 0", "Soc 2","Soc 4", "Soc 6", # Page 1
    #         "Soc 1", "Soc 3", "Soc 5", "Soc 7", # Page 2
    #     ]
        
    #     # Check if the order matches
    #     actual_order = [p.group for p in sorted_persons]
    #     self.assertEqual(actual_order, expected_order)

    # def test_sort_11_persons(self):
    #     """Test sorting with 11 persons (3 pages with last page incomplete)"""
    #     # Create 11 test persons
    #     persons = [
    #         Person("front.png", "back.png", f"Name {i}", f"Last {i}", f"Soc {i}")
    #         for i in range(0, 11)
    #     ]
        
    #     # Shuffle to ensure sorting works
    #     import random
    #     random.shuffle(persons)
        
    #     # Sort for printing
    #     sorted_persons = sort_persons_for_printing(persons)
        
    #     # Expected order: position 1 across pages, then position 2, etc.
    #     expected_order = [
    #         "Soc 0", "Soc 3","Soc 6","Soc 9",    # Page 1,
    #         "Soc 1", "Soc 4", "Soc 7", "Soc 10",  # Page 2
    #         "Soc 2",  "Soc 5", "Soc 8", # Page 3
    #     ]
        
    #     # Check if the order matches
    #     actual_order = [p.group for p in sorted_persons]
    #     self.assertEqual(actual_order, expected_order)

    # def test_sort_23_persons(self):
    #     """Test sorting with 23 persons (6 pages with last page incomplete)"""
    #     # Create 23 test persons
    #     persons = [
    #         Person("front.png", "back.png", f"Name {i}", f"Last {i}", f"Soc {i}")
    #         for i in range(0, 23)
    #     ]
        
    #     # Shuffle to ensure sorting works
    #     import random
    #     random.shuffle(persons)
        
    #     # Sort for printing
    #     sorted_persons = sort_persons_for_printing(persons)
        
    #     # Expected order: position 1 across pages, then position 2, etc.
    #     expected_order = [
    #         "Soc 0", "Soc 6", "Soc 12", "Soc 18",  # Page 1
    #         "Soc 1", "Soc 7", "Soc 13", "Soc 19",  # Page 2
    #         "Soc 2", "Soc 8", "Soc 14", "Soc 20",  # Page 3
    #         "Soc 3", "Soc 9", "Soc 15", "Soc 21",  # Page 4
    #         "Soc 4", "Soc 10", "Soc 16", "Soc 22", # Page 5
    #         "Soc 5", "Soc 11", "Soc 17",           # Page 6
    #     ]
        
    #     # Check if the order matches
    #     actual_order = [p.group for p in sorted_persons]
    #     self.assertEqual(actual_order, expected_order)

    # Create another test with 24 people. Reuse the same group of persons used in previous test but, change the frontside of the Person 0, 7, and 19 to a "front2.png" and Person 1, 2, 3, 4, 5, 6 and 8 to "front3.png"
    def test_sort_24_persons(self):
        """Test sorting with 24 persons (6 pages with an incomplete 6th page)"""
        # Create 24 test persons, but modify some to test sorting by frontside
        persons = [
            Person("front3.png", "back.png", f"Name {i}", f"Last {i}", f"Soc {i}")
            for i in range(24) if i in {1, 2, 3, 4, 5, 6, 8}
        ]
        persons += [
            Person("front2.png", "back.png", f"Name {i}", f"Last {i}", f"Soc {i}")
            for i in range(24) if i in {0, 7, 19}
        ]
        persons += [
            Person("front1.png", "back.png", f"Name {i}", f"Last {i}", f"Soc {i}") for i in range(24)
            if i not in {1, 2, 3, 4, 5, 6, 8, 0, 7, 19}
        ]
        
        # Shuffle to ensure sorting works
        import random
        random.shuffle(persons)
        
        # Sort for printing
        sorted_persons = sort_persons_for_printing(persons)

        # Expected order: position 1 across pages, then position 2, etc.
        expected_order = [
            "Soc 9", "Soc 15", "Soc 22", "Soc 2",  # Page 1
            "Soc 10", "Soc 16", "Soc 23", "Soc 3",  # Page 2
            "Soc 11", "Soc 17", "Soc 0", "Soc 4",  # Page 3
            "Soc 12", "Soc 18", "Soc 7", "Soc 5",  # Page 4
            "Soc 13", "Soc 20", "Soc 19", "Soc 6", # Page 5
            "Soc 14", "Soc 21", "Soc 1", "Soc 8"  # Page 6
        ]
        actual_order = [p.group for p in sorted_persons]
        self.assertEqual(actual_order, expected_order)

