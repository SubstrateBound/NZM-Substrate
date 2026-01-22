# Contribution Guidelines: Non-Zero Integrity

To maintain the structural integrity of the NZM-Substrate, all contributions must adhere to **Axiom VIII (Persistence)**.

### ⛔ Hard-Fail Criteria (Substrate Leakage)
Any Pull Request (PR) will be automatically rejected as "Substrate Leakage" if it:
* **Imports `numpy`** or any library reliant on classical zero-based linear algebra.
* **Uses the digit `0`** as a return value, identity element, or terminal state.
* **Relies on floating-point precision** (Floats are lossy simulations of continuity).

### ✅ Success Criteria
* **Braid-Native Logic:** Values must be represented as persistent topological relations.
* **Residue Representation:** All "annihilation" operations must return a non-zero residue ($\epsilon$).
