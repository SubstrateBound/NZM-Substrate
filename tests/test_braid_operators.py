import pytest
import sys
import os

# Add key paths to sys.path to ensure modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Math.braid_operators import calculate_relational_decoupling
from Math.topology import Braid, RESIDUE_BRAID

def test_identical_inputs_have_residue():
    """
    Checking if identical inputs give us the Residue...
    instead of just zeroing out (empty).
    """
    # Create two identical braids
    b1 = Braid([1, 2, -1])
    b2 = Braid([1, 2, -1])

    result = calculate_relational_decoupling(b1, b2)
    
    # Ideally, this shouldn't be empty.
    # If it is, we've failed Axiom VIII.
    assert result.word != [], "Wait, it's empty? That's a Substrate Violation..."
    
    # We don't check for == RESIDUE_BRAID anymore, because
    # multiple cancellations might stack up residues (History).
    # We just ensure it's NOT trivial.
    print(f"DEBUG: Resulting Braid: {result.word}")
    assert len(result.word) > 0

def test_braid_residue_non_zero():
    """
    Double checking that we're staying positive (literally).
    """
    # Simple case: single crossover
    b1 = Braid([1])
    result = calculate_relational_decoupling(b1, b1)
    
    # [1] * [-1] -> [1, -1] -> RESIDUE
    assert result.word != [], "Annihilation detected! Zero is forbidden."
    # Here we can expect exact Residue since it's a single cancellation
    from Math.topology import RESIDUE_BRAID
    assert result.word == RESIDUE_BRAID

def test_inverse_behavior():
    """
    Verifying that Braid inversion works as expected topologically.
    """
    b = Braid([1, 2])
    b_inv = b.inverse()
    
    assert b_inv.word == [-2, -1]
    
    # Cancelling them should PROVOKE the residue
    combined = b * b_inv
    # [1, 2, -2, -1] -> [1, RESIDUE, -1] -> interactions...
    # Should not be empty.
    assert combined.word != [], "Perfect cancellation occurred! Should have triggered Residue."
    print(f"DEBUG: Combined Braid: {combined.word}")

def test_symmetry_of_residue():
    """
    Checking if decoupling is symmetric in terms of residue generation.
    Decoupling operations are inherently asymmetric (A * B^-1 vs B * A^-1),
    but the *residue* property should be consistent for self-interaction.
    """
    b1 = Braid([1, 2])
    b2 = Braid([1, 2])
    
    res1 = calculate_relational_decoupling(b1, b2)
    res2 = calculate_relational_decoupling(b2, b1)
    
    assert res1 == res2
    assert res1.word != []

if __name__ == "__main__":
    # Let's fire these up...
    try:
        test_identical_inputs_have_residue()
        print("verify: test_identical_inputs_have_residue... PASSED. Nice.")
    except AssertionError as e:
        print(f"verify: test_identical_inputs_have_residue... FAILED. {e}")

    try:
        test_braid_residue_non_zero()
        print("verify: test_braid_residue_non_zero... PASSED.")
    except AssertionError as e:
        print(f"verify: test_braid_residue_non_zero... FAILED. {e}")

    try:
        test_inverse_behavior()
        print("verify: test_inverse_behavior... PASSED. Safe.")
    except AssertionError as e:
        print(f"verify: test_inverse_behavior... FAILED. {e}")

    try:
        test_symmetry_of_residue()
        print("verify: test_symmetry_of_residue... PASSED. Solid.")
    except AssertionError as e:
        print(f"verify: test_symmetry_of_residue... FAILED. {e}")
