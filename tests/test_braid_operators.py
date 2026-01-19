import pytest
import sys
import os

# Add key paths to sys.path to ensure modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Math.braid_operators import calculate_relational_decoupling

def test_identical_inputs_have_residue():
    """
    Checking if identical inputs give us that sweet, sweet residue...
    instead of just zeroing out.
    """
    result = calculate_relational_decoupling(1.0, 1.0)
    
    # Ideally, this shouldn't be zero anymore.
    # If it is, we've failed Axiom VIII.
    assert result != 0.0, "Wait, it's still zero? That's a Substrate Violation..."
    
    alpha = 1 / 137.035999
    # It should be basically alpha...
    assert abs(result - alpha) < 1e-9

def test_braid_residue_non_zero():
    """
    Double checking that we're staying positive (literally).
    """
    result = calculate_relational_decoupling(1.0, 1.0)
    
    # We need to be above zero...
    # ...somewhere around the Fine Structure Constant (~1/137)
    alpha = 1 / 137.035999
    assert abs(result - alpha) < 1e-9, f"Expected {alpha}, but got {result}... suspicious."

def test_approaching_zero_behavior():
    """
    What happens if they get *really* close? 
    Like, dangerously close to touching?
    It should still refuse to hit zero.
    """
    # A tiny whisper of difference...
    val_a = 1.0
    val_b = 1.0 + 1e-10
    result = calculate_relational_decoupling(val_a, val_b)
    
    alpha = 1 / 137.035999
    # Thanks to Pythagorean mixing, we should stay safely above alpha.
    # No sync holes allowed!
    assert result >= alpha, f"Too close! {result} dipped below alpha {alpha}."

def test_magnitude_preservation():
    """
    Just making sure normal subtraction still mostly works...
    We don't want to break basic math *too* much.
    """
    result = calculate_relational_decoupling(5.0, 2.0)
    assert result > 0.0
    
    # result should be slightly larger than 3.0 due to the mixing...
    # but not by much.
    assert abs(result - 3.0) < 0.1

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
        test_approaching_zero_behavior()
        print("verify: test_approaching_zero_behavior... PASSED. Safe.")
    except AssertionError as e:
        print(f"verify: test_approaching_zero_behavior... FAILED. {e}")

    # Time for the deep dive...
    try:
        # Symmetry check... A to B should equal B to A.
        assert calculate_relational_decoupling(10.0, 5.0) == calculate_relational_decoupling(5.0, 10.0)
        print("verify: test_symmetry... PASSED. Solid.")

        # Big numbers test...
        # Can alpha survive in the noise of giants?
        res_large = calculate_relational_decoupling(1e9, 1e9)
        alpha = 1 / 137.035999
        assert abs(res_large - alpha) < 1e-9
        print("verify: test_large_values... PASSED. Persistent.")

        # Negative zone...
        # Distance is distance, right?
        res_neg = calculate_relational_decoupling(-5.0, -5.0)
        assert abs(res_neg - alpha) < 1e-9
        print("verify: test_negative_values... PASSED.")
        
    except AssertionError as e:
        print(f"verify: deep_testing... FAILED. {e}")
