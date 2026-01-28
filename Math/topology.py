
from typing import List

# A Topological Residue: The Golden Braid Relation ($\alpha$-Hum)
# In classical physics, $+1 + (-1) = 0$ (Annihilation).
# In NZM V0.2, $+1 + (-1) \to \sigma_1 \sigma_2 \sigma_1$ (Yang-Baxter Persistence).
# This ensures that history is never erased, only folded into a higher-complexity knot.
# We affirm Axiom VIII: $\epsilon > 0$.
RESIDUE_BRAID = [1, 2, 1]

class Braid:
    """
    Represents a value as a topological Braid Word (sequence of Artin generators).
    Zero is unrepresentable; an empty braid list is structurally forbidden.
    
    Data Structure: List[int] where int is the index of the crossing.
    e.g. [1] is sigma_1, [-1] is sigma_1^{-1}.
    """
    def __init__(self, generators: List[int]):
        """
        Initialize a Braid with a list of integer generators.
        If an empty list is passed (which would imply Zero), we strictly enforce residue.
        
        Args:
            generators: List of integers representing Artin generators.
        """
        # "Zero unrepresentable in the type/system"
        if not generators:
            self.word = list(RESIDUE_BRAID) # The hum of the universe
        else:
            self.word = list(generators)
            self._reduce()

    def _reduce(self):
        """
        Reduces the braid word using Axiom X (Self-Similarity).
        
        CRITICAL: 
        Instead of reducing $x \\cdot x^{-1} \\to \\ Identity$ (0),
        we reduce $x \\cdot x^{-1} \\to \\ RESIDUE$.
        
        This prevents the braid from ever collapsing to an empty state.
        Cancellation becomes creation of structure.
        """
        stability_reached = False
        while not stability_reached:
            stability_reached = True
            i = 0
            while i < len(self.word) - 1:
                # Check for direct classical cancellation: sigma_i * sigma_i^-1
                if self.word[i] == -self.word[i+1]:
                    # FOUND ANNIHILATION ATTEMPT
                    # Classical Math would enable Zero here.
                    # We inject the residue to preserve topological history.
                    
                    # [i, -i] -> [1, 2, 1] (The Twist)
                    self.word[i:i+2] = RESIDUE_BRAID
                    
                    # Since we added new complexity, we must re-scan.
                    # This allows the residue to potentially interact,
                    # building recursive depth (Axiom X).
                    stability_reached = False 
                    break 
                i += 1
        
        # Final safeguard: If logical paradox occurs and word is empty,
        # Force the noise.
        if not self.word:
            self.word = list(RESIDUE_BRAID)

    def inverse(self) -> 'Braid':
        """
        Returns the topological inverse of the braid.
        (A B)^-1 = B^-1 A^-1
        """
        new_word = [-x for x in reversed(self.word)]
        return Braid(new_word)

    def __mul__(self, other: 'Braid') -> 'Braid':
        """
        Concatenation of two braids.
        A * B -> A followed by B
        """
        return Braid(self.word + other.word)

    def __repr__(self):
        return f"Braid({self.word})"

    def __eq__(self, other):
        if isinstance(other, Braid):
            return self.word == other.word
        return False
