import unittest
from match import Applicant, Residency, remove_applicant_from_residency, run_match, try_match_applicant_to_residency

class TestMatching(unittest.TestCase):


    def test_try_match_applicant_to_residency(self):
        # Test basic matching
        applicant = Applicant("Alice", ["Hospital A"])
        residency = Residency("Hospital A", ["Alice"], 1)
        
        # Should successfully match
        result = try_match_applicant_to_residency(applicant, residency)
        self.assertIsNone(result) # No one was bumped
        self.assertEqual(applicant.tentative_match, residency)
        self.assertEqual(residency.positions_available, 0)
        self.assertIn("Alice", residency.assigned_applicants)

    def test_remove_applicant_from_residency(self):
        applicant = Applicant("Alice", ["Hospital A", "Hospital B"])
        hospital = Residency("Hospital A", ["Alice"], 1)
        
        # First match them
        try_match_applicant_to_residency(applicant, hospital)
        
        # Then remove
        remove_applicant_from_residency(applicant, hospital)
        
        # Verify applicant state
        self.assertIsNone(applicant.tentative_match)
        self.assertNotIn("Hospital A", applicant.remaining_ranked_residencies)
        
        # Verify residency state
        self.assertEqual(hospital.positions_available, 1)
        self.assertNotIn(applicant.name, hospital.assigned_applicants)

    def test_matching_when_residency_full(self):
        # Test matching when residency is full
        alice = Applicant("Alice", ["Hospital A"])
        bob = Applicant("Bob", ["Hospital A"])
        carol = Applicant("Carol", ["Hospital A"])
        dave = Applicant("Dave", ["Hospital A"])
        
        hospital = Residency("Hospital A", ["Carol", "Bob", "Alice"], 2)
        
        # Match first two applicants
        try_match_applicant_to_residency(bob, hospital)
        try_match_applicant_to_residency(carol, hospital)
        
        self.assertEqual(hospital.positions_available, 0)
        self.assertIn(bob.name, hospital.assigned_applicants)
        self.assertIn(carol.name, hospital.assigned_applicants)

        # Try to match a third - should fail since full with better ranked applicants
        result = try_match_applicant_to_residency(dave, hospital)
        self.assertIsNone(result)
        self.assertNotIn(dave.name, hospital.assigned_applicants)

    def test_basic_matching(self):
        # Create a simple test case with 2 applicants and 2 residencies
        alice = Applicant("Alice", ["Hospital A", "Hospital B"])
        bob = Applicant("Bob", ["Hospital B", "Hospital A"])
        
        hospital_a = Residency("Hospital A", ["Alice", "Bob"], 1)
        hospital_b = Residency("Hospital B", ["Bob", "Alice"], 1)

        applicants = [alice, bob]
        residencies = [hospital_a, hospital_b]

        # Run the matching algorithm
        run_match(applicants, residencies)

        # Verify the matches are stable
        self.assertEqual(alice.tentative_match, hospital_a)
        self.assertEqual(bob.tentative_match, hospital_b)
        
        self.assertIn(alice.name, hospital_a.assigned_applicants)
        self.assertIn(bob.name, hospital_b.assigned_applicants)

        # Verify positions are filled correctly
        self.assertEqual(hospital_a.positions_available, 0)
        self.assertEqual(hospital_b.positions_available, 0)

    def test_matching_with_bump(self):
        # Create a simple test case with 2 applicants and 2 residencies
        alice = Applicant("Alice", ["Hospital A"])
        bob = Applicant("Bob", ["Hospital A"])
        
        hospital_a = Residency("Hospital A", ["Alice", "Bob"], 1)

        applicants = [alice, bob]
        residencies = [hospital_a]

        # Run the matching algorithm
        run_match(applicants, residencies)

        # Verify the matches are stable
        self.assertEqual(alice.tentative_match, hospital_a)
        self.assertEqual(bob.tentative_match, None)
        
        self.assertIn(alice.name, hospital_a.assigned_applicants)

        # Verify positions are filled correctly
        self.assertEqual(hospital_a.positions_available, 0)

    def test_multiple_positions_and_bumping(self):
        # Test where a hospital has multiple positions and lower-ranked candidates get bumped
        alice = Applicant("Alice", ["Hospital A"])
        bob = Applicant("Bob", ["Hospital A"]) 
        charlie = Applicant("Charlie", ["Hospital A"])
        dave = Applicant("Dave", ["Hospital A"])
        
        # Hospital A has 2 positions and prefers candidates in order: Alice > Bob > Charlie > Dave
        hospital_a = Residency("Hospital A", ["Alice", "Bob", "Charlie", "Dave"], 2)

        applicants = [dave, charlie, bob, alice]  # Test order shouldn't matter
        residencies = [hospital_a]

        run_match(applicants, residencies)

        # Alice and Bob should get the spots, Charlie and Dave should be bumped
        self.assertEqual(alice.tentative_match, hospital_a)
        self.assertEqual(bob.tentative_match, hospital_a)
        self.assertIsNone(charlie.tentative_match)
        self.assertIsNone(dave.tentative_match)
        
        self.assertEqual(len(hospital_a.assigned_applicants), 2)
        self.assertIn(alice.name, hospital_a.assigned_applicants)
        self.assertIn(bob.name, hospital_a.assigned_applicants)
        self.assertEqual(hospital_a.positions_available, 0)

    def test_applicant_preference(self):
        alice = Applicant("Alice", ["Mass General", "Mayo Clinic", "Cleveland Clinic"])
        bob = Applicant("Bob", ["Mayo Clinic", "Cleveland Clinic", "Mass General"]) 
        carol = Applicant("Carol", ["Cleveland Clinic", "Mass General", "Mayo Clinic"])
        
        mass_general = Residency("Mass General", ["Bob", "Carol", "Alice"], 1)
        mayo_clinic = Residency("Mayo Clinic", ["Carol", "Alice", "Bob"], 1)
        cleveland_clinic = Residency("Cleveland Clinic", ["Alice", "Bob", "Carol"], 1)

        applicants = [alice, bob, carol]
        residencies = [mass_general, mayo_clinic, cleveland_clinic]

        run_match(applicants, residencies)

        # Verify final stable matching
        self.assertEqual(alice.tentative_match, mass_general)
        self.assertEqual(bob.tentative_match, mayo_clinic)
        self.assertEqual(carol.tentative_match, cleveland_clinic)

    def test_unequal_numbers(self):
        # Test with more applicants than positions
        alice = Applicant("Alice", ["Hospital A"])
        bob = Applicant("Bob", ["Hospital A"])
        charlie = Applicant("Charlie", ["Hospital A"])
        
        hospital_a = Residency("Hospital A", ["Alice", "Bob", "Charlie"], 1)

        applicants = [alice, bob, charlie]
        residencies = [hospital_a]

        run_match(applicants, residencies)

        self.assertEqual(alice.tentative_match, hospital_a)
        self.assertIsNone(bob.tentative_match)
        self.assertIsNone(charlie.tentative_match)
        self.assertEqual(len(hospital_a.assigned_applicants), 1)

    def test_partial_preferences(self):
        # Test where some applicants/residencies only rank a subset
        alice = Applicant("Alice", ["Hospital A", "Hospital B"])
        bob = Applicant("Bob", ["Hospital B"])  # Bob only ranks B
        charlie = Applicant("Charlie", ["Hospital A"])  # Charlie only ranks A
        
        hospital_a = Residency("Hospital A", ["Alice", "Charlie"], 1)  # A doesn't rank Bob
        hospital_b = Residency("Hospital B", ["Alice", "Bob"], 1)

        applicants = [alice, bob, charlie]
        residencies = [hospital_a, hospital_b]

        run_match(applicants, residencies)

        self.assertEqual(alice.tentative_match, hospital_a)
        self.assertEqual(bob.tentative_match, hospital_b)
        self.assertIsNone(charlie.tentative_match)  # Alice gets bumped from both

if __name__ == '__main__':
    unittest.main()
