#!/usr/bin/env python3
"""
QSD Qiskit Simulation Suite -- Core Circuits
=============================================

Three quantum circuits demonstrating QSD predictions on real quantum hardware:

1. Code513Circuit:  [[5,1,3]] syndrome extraction
   - Proper encoding of logical |0>_L and |1>_L codewords
   - Ancilla-based syndrome measurement (5 data + 4 ancilla = 9 qubits)
   - Complete syndrome table: all 15 single-qubit errors -> distinct 4-bit patterns
   - Verification: quantum Hamming bound saturation (2^4 = 1 + 3*5)

2. K4HeisenbergVQE:  Heisenberg antiferromagnet on complete graph K4
   - H = Hb4 * sum_{i<j} S_i . S_j   (4 qubits, 18 Pauli terms)
   - VQE ground state: E0 = -3*Hb4/2 with hardware-efficient ansatz
   - Full spectrum via exact diagonalization
   - S4 irrep decomposition: 16 states = 2 + 9 + 5

3. C5EigenvalueCircuit:  Golden ratio from pentagon spectrum
   - C5 adjacency as XX+YY hopping on 5 qubits (single-excitation sector)
   - VQE eigenvalue extraction with deflation
   - Verification: |lambda_max / lambda_min| = phi^2

All circuits are designed for:
- Aer simulator (statevector + shot-based)
- IBM Quantum hardware (transpiled for real backends)

Requires: qiskit >= 1.0, qiskit-aer >= 0.13, numpy, scipy
Falls back to numpy-only mode if Qiskit unavailable.

Author: M. Hubka
Date: February 2026
"""

from __future__ import annotations

import sys
import warnings
import itertools
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import minimize
from scipy.linalg import expm

# ---------------------------------------------------------------------------
# Import QSD constants
# ---------------------------------------------------------------------------
try:
    from qsd_constants import (
        GOLDEN_RATIO, GOLDEN_RATIO_SQ, LN2, HB4, SIGMA, VARPI,
        ALPHA_INV_QSD, ALPHA_S_QSD, MU_RAD,
        M_HIGGS_QSD, E_SYNDROME_QSD, M_W_QSD,
    )
except ImportError:
    # Inline fallback -- matches qsd_constants.py exactly
    GOLDEN_RATIO     = (1.0 + np.sqrt(5.0)) / 2.0
    GOLDEN_RATIO_SQ  = GOLDEN_RATIO ** 2
    LN2              = np.log(2.0)
    HB4              = 1.0 / (4.0 * LN2)
    SIGMA            = 3.0 / (80.0 * GOLDEN_RATIO_SQ)
    VARPI            = np.pi * GOLDEN_RATIO_SQ
    MU_RAD           = (1.22089e19 / 2**60) * GOLDEN_RATIO_SQ * (1.0 - 6.0 * SIGMA)
    E_SYNDROME_QSD   = MU_RAD * (1.0 + 8.0 * SIGMA)
    M_HIGGS_QSD      = 5.0 * MU_RAD

# ---------------------------------------------------------------------------
# Qiskit availability check
# ---------------------------------------------------------------------------
QISKIT_AVAILABLE = False
AER_AVAILABLE = False

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit.quantum_info import (
        SparsePauliOp, Statevector, Operator, Pauli
    )
    QISKIT_AVAILABLE = True
    try:
        from qiskit_aer import AerSimulator
        AER_AVAILABLE = True
    except ImportError:
        try:
            from qiskit.providers.aer import AerSimulator
            AER_AVAILABLE = True
        except ImportError:
            pass
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Pauli matrices (always available via numpy)
# ---------------------------------------------------------------------------
I2 = np.eye(2, dtype=complex)
SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)
PAULIS = {'I': I2, 'X': SX, 'Y': SY, 'Z': SZ}


def kron_list(ops):
    """Tensor product of a list of operators."""
    result = ops[0]
    for op in ops[1:]:
        result = np.kron(result, op)
    return result


def pauli_string_to_matrix(pstring):
    """Convert Pauli string like 'XZZXI' to 2^n x 2^n matrix."""
    return kron_list([PAULIS[c] for c in pstring])


# ============================================================================
#  MODULE 1:  [[5,1,3]] QUANTUM ERROR-CORRECTING CODE
# ============================================================================

class Code513Circuit:
    """
    Complete implementation of the [[5,1,3]] quantum error-correcting code.

    The [[5,1,3]] code is the unique minimal quantum code that corrects
    arbitrary single-qubit errors on one logical qubit.  It saturates the
    quantum Hamming bound:  2^(n-k) = 2^4 = 16 = 1 + 3n = 1 + 15.

    In QSD, this code IS the vacuum structure of spacetime.  The four
    stabilizer generators define the syndrome space K4 (complete graph
    on 4 vertices), while their Z5 cyclic symmetry defines C5 (the
    pentagon).  Syndromes -- the error-correction signals -- are the
    predicted 28 GeV resonance.

    Stabilizer generators (S1, Definition 2.2):
        g1 = XZZXI
        g2 = IXZZX
        g3 = XIXZZ
        g4 = ZXIXZ

    Logical operators:
        X_L = XXXXX
        Z_L = ZZZZZ

    Circuit layout:
        Qubits 0-4:  data register (5 physical qubits)
        Qubits 5-8:  ancilla register (4 syndrome qubits)
        Classical 0-3: syndrome readout
    """

    # Stabilizer generators as Pauli strings
    STABILIZERS = ['XZZXI', 'IXZZX', 'XIXZZ', 'ZXIXZ']

    # Logical operators
    X_LOGICAL = 'XXXXX'
    Z_LOGICAL = 'ZZZZZ'

    def __init__(self):
        self.n_data = 5
        self.n_ancilla = 4
        self.n_total = 9

        # Build stabilizer matrices (32 x 32)
        self.stabilizer_matrices = [
            pauli_string_to_matrix(s) for s in self.STABILIZERS
        ]
        self.x_logical_matrix = pauli_string_to_matrix(self.X_LOGICAL)
        self.z_logical_matrix = pauli_string_to_matrix(self.Z_LOGICAL)

        # Compute codespace and syndrome table
        self._logical_zero, self._logical_one = self._compute_codewords()
        self._syndrome_table = self._build_syndrome_table()

    # ------------------------------------------------------------------
    # Codespace construction
    # ------------------------------------------------------------------

    def _compute_codewords(self):
        """
        Compute |0>_L and |1>_L by projecting onto the +1 eigenspace
        of all four stabilizers and Z_L.

        |0>_L: +1 eigenstate of g1, g2, g3, g4 AND Z_L
        |1>_L: +1 eigenstate of g1, g2, g3, g4 AND -1 of Z_L
               equivalently: X_L |0>_L
        """
        dim = 2 ** self.n_data  # 32

        # Projector onto +1 eigenspace of all stabilizers
        projector = np.eye(dim, dtype=complex)
        for g in self.stabilizer_matrices:
            projector = projector @ (np.eye(dim) + g) / 2.0

        # Further project onto +1 eigenspace of Z_L for |0>_L
        proj_zl_plus = (np.eye(dim) + self.z_logical_matrix) / 2.0
        proj_0L = projector @ proj_zl_plus

        # The image of proj_0L should be 1-dimensional
        eigenvalues, eigenvectors = np.linalg.eigh(proj_0L)
        # Find the eigenvector with eigenvalue ~1
        idx = np.argmax(eigenvalues.real)
        logical_zero = eigenvectors[:, idx]
        logical_zero = logical_zero / np.linalg.norm(logical_zero)

        # |1>_L = X_L |0>_L
        logical_one = self.x_logical_matrix @ logical_zero
        logical_one = logical_one / np.linalg.norm(logical_one)

        # Verify properties
        for i, g in enumerate(self.stabilizer_matrices):
            ev0 = np.vdot(logical_zero, g @ logical_zero)
            ev1 = np.vdot(logical_one, g @ logical_one)
            assert abs(ev0 - 1.0) < 1e-10, (
                '|0>_L not +1 eigenstate of g%d: got %.6f' % (i+1, ev0))
            assert abs(ev1 - 1.0) < 1e-10, (
                '|1>_L not +1 eigenstate of g%d: got %.6f' % (i+1, ev1))

        zl_0 = np.vdot(logical_zero, self.z_logical_matrix @ logical_zero)
        zl_1 = np.vdot(logical_one, self.z_logical_matrix @ logical_one)
        assert abs(zl_0 - 1.0) < 1e-10, 'Z_L on |0>_L = %.6f' % zl_0
        assert abs(zl_1 + 1.0) < 1e-10, 'Z_L on |1>_L = %.6f' % zl_1

        return logical_zero, logical_one

    # ------------------------------------------------------------------
    # Syndrome table (analytical from symplectic inner product)
    # ------------------------------------------------------------------

    def _build_syndrome_table(self):
        """
        Build the complete syndrome lookup table.

        For each single-qubit Pauli error E on qubit j, the syndrome is
        the 4-bit string (s1, s2, s3, s4) where s_i = 0 if [g_i, E] = 0
        and s_i = 1 if {g_i, E} = 0.

        For Pauli errors, this reduces to the symplectic inner product:
            s_i(X_j) = g_i^Z[j]       (Z-part of stabilizer at position j)
            s_i(Z_j) = g_i^X[j]       (X-part of stabilizer at position j)
            s_i(Y_j) = g_i^X[j] XOR g_i^Z[j]

        Returns dict mapping syndrome integer -> (error_type, qubit_index).
        """
        # Extract X and Z parts of each stabilizer
        stab_x = []  # stab_x[i][j] = 1 if g_i has X at position j
        stab_z = []  # stab_z[i][j] = 1 if g_i has Z at position j
        for s in self.STABILIZERS:
            stab_x.append([1 if c == 'X' else 0 for c in s])
            stab_z.append([1 if c == 'Z' else 0 for c in s])

        table = {0: ('I', -1)}  # syndrome 0 = no error

        for j in range(self.n_data):
            for error_type in ['X', 'Y', 'Z']:
                syndrome_bits = []
                for i in range(4):
                    if error_type == 'X':
                        bit = stab_z[i][j]
                    elif error_type == 'Z':
                        bit = stab_x[i][j]
                    else:  # Y = iXZ, anticommutes iff X-part or Z-part does (XOR)
                        bit = (stab_x[i][j] + stab_z[i][j]) % 2
                    syndrome_bits.append(bit)

                # Convert to integer: s1*8 + s2*4 + s3*2 + s4*1
                syndrome_int = (syndrome_bits[0] * 8 +
                                syndrome_bits[1] * 4 +
                                syndrome_bits[2] * 2 +
                                syndrome_bits[3] * 1)

                table[syndrome_int] = (error_type, j)

        # Verify all 16 values are distinct (Hamming bound saturation)
        assert len(table) == 16, (
            'Expected 16 distinct syndromes, got %d' % len(table))
        assert set(table.keys()) == set(range(16)), (
            'Syndrome table does not cover all 4-bit patterns')

        return table

    # ------------------------------------------------------------------
    # Qiskit circuits
    # ------------------------------------------------------------------

    def syndrome_extraction_circuit(self,
                                    error_type=None,
                                    error_qubit=None):
        """
        Build the full syndrome extraction circuit.

        Layout:
            q[0..4] = data qubits (encode |0>_L)
            q[5..8] = ancilla qubits (measure g1..g4)
            c[0..3] = classical bits (syndrome readout)

        Steps:
            1. Prepare |0>_L on data qubits via initialize
            2. (Optional) Apply error on specified qubit
            3. For each stabilizer g_i, measure via ancilla:
               a. H(ancilla)
               b. Controlled-X_j for each X in g_i (CNOT from ancilla)
               c. Controlled-Z_j for each Z in g_i (CZ)
               d. H(ancilla)
            4. Measure ancilla -> classical register
        """
        if not QISKIT_AVAILABLE:
            raise RuntimeError('Qiskit not available')

        qc = QuantumCircuit(self.n_total, self.n_ancilla,
                            name='513_syndrome')

        # --- Step 1: Encode |0>_L ---
        qc.initialize(self._logical_zero.tolist(), list(range(5)))
        qc.barrier(label='encode')

        # --- Step 2: Inject error ---
        if error_type is not None and error_qubit is not None:
            assert error_qubit in range(5), 'Invalid qubit: %d' % error_qubit
            assert error_type in ('X', 'Y', 'Z'), (
                'Invalid error: %s' % error_type)
            gate_fn = {'X': qc.x, 'Y': qc.y, 'Z': qc.z}
            gate_fn[error_type](error_qubit)
            qc.barrier(label='%s%d' % (error_type, error_qubit))

        # --- Step 3: Syndrome extraction ---
        for anc_idx, stab_str in enumerate(self.STABILIZERS):
            anc_qubit = 5 + anc_idx

            # Prepare ancilla in |+>
            qc.h(anc_qubit)

            # Apply controlled Paulis from ancilla to data
            for data_q, pauli_char in enumerate(stab_str):
                if pauli_char == 'X':
                    qc.cx(anc_qubit, data_q)
                elif pauli_char == 'Z':
                    qc.cz(anc_qubit, data_q)
                # 'I' -> do nothing
                # (No Y in [[5,1,3]] stabilizers)

            # Map ancilla back to computational basis
            qc.h(anc_qubit)

        qc.barrier(label='measure')

        # --- Step 4: Measure ancilla ---
        for i in range(self.n_ancilla):
            qc.measure(5 + i, i)

        return qc

    # ------------------------------------------------------------------
    # Simulation methods
    # ------------------------------------------------------------------

    def run_all_syndromes_statevector(self):
        """
        Test all 15 single-qubit errors using statevector simulation.

        For each error E applied to |0>_L, compute the syndrome by
        measuring the eigenvalue of each stabilizer on E|0>_L.

        This is the gold-standard test: purely numerical, no shot noise.
        """
        results = []
        all_match = True

        for error_type in ['X', 'Y', 'Z']:
            for qubit in range(5):
                # Build error operator
                ops = [I2] * 5
                ops[qubit] = PAULIS[error_type]
                error_op = kron_list(ops)

                # Apply error to |0>_L
                corrupted = error_op @ self._logical_zero

                # Measure each stabilizer eigenvalue
                syndrome_bits = []
                for g_matrix in self.stabilizer_matrices:
                    eigenvalue = np.vdot(corrupted, g_matrix @ corrupted).real
                    bit = 0 if eigenvalue > 0 else 1
                    syndrome_bits.append(bit)

                measured = (syndrome_bits[0] * 8 + syndrome_bits[1] * 4 +
                            syndrome_bits[2] * 2 + syndrome_bits[3] * 1)

                predicted_error = self._syndrome_table[measured]
                match = (predicted_error == (error_type, qubit))

                results.append({
                    'error': '%s%d' % (error_type, qubit),
                    'syndrome_binary': ''.join(str(b) for b in syndrome_bits),
                    'syndrome_int': measured,
                    'predicted_error': (
                        '%s%d' % (predicted_error[0], predicted_error[1])
                        if predicted_error[1] >= 0 else 'none'),
                    'match': match,
                })

                if not match:
                    all_match = False

        return {
            'syndrome_table': {
                k: '%s%d' % (v[0], v[1]) if v[1] >= 0 else 'none'
                for k, v in sorted(self._syndrome_table.items())
            },
            'results': results,
            'all_match': all_match,
            'n_distinct_syndromes': len(self._syndrome_table),
            'hamming_bound': '2^4 = 16 = 1 + 3*5 (SATURATED)',
        }

    def run_all_syndromes_circuit(self, n_shots=4096):
        """
        Test all 15 single-qubit errors using shot-based Aer simulation.
        """
        if not QISKIT_AVAILABLE or not AER_AVAILABLE:
            raise RuntimeError('Qiskit + Aer required for circuit simulation')

        backend = AerSimulator()
        results = []
        all_match = True

        for error_type in ['X', 'Y', 'Z']:
            for qubit in range(5):
                qc = self.syndrome_extraction_circuit(
                    error_type=error_type, error_qubit=qubit)

                qc_t = transpile(qc, backend)
                job = backend.run(qc_t, shots=n_shots)
                counts = job.result().get_counts()

                # Find dominant syndrome (Qiskit bit ordering: MSB first)
                dominant = max(counts, key=counts.get)
                syndrome_int = int(dominant, 2)

                predicted = self._syndrome_table.get(syndrome_int, ('?', -1))
                match = (predicted == (error_type, qubit))

                fidelity = counts.get(dominant, 0) / n_shots

                results.append({
                    'error': '%s%d' % (error_type, qubit),
                    'dominant_syndrome': dominant,
                    'syndrome_int': syndrome_int,
                    'predicted_error': (
                        '%s%d' % (predicted[0], predicted[1])
                        if predicted[1] >= 0 else 'none'),
                    'match': match,
                    'fidelity': fidelity,
                    'n_outcomes': len(counts),
                })

                if not match:
                    all_match = False

        return {
            'results': results,
            'all_match': all_match,
            'n_shots': n_shots,
        }

    def get_codewords(self):
        """Return the logical codewords as state vectors."""
        return {
            'logical_zero': self._logical_zero.copy(),
            'logical_one': self._logical_one.copy(),
        }

    def get_syndrome_table(self):
        """Return the complete syndrome lookup table."""
        return dict(self._syndrome_table)

    def print_syndrome_table(self):
        """Print the syndrome table in a formatted way."""
        print('\n[[5,1,3]] Syndrome Table')
        print('=' * 55)
        print('%10s %8s %8s   %s' % ('Syndrome', 'Binary', 'Error', 'Note'))
        print('-' * 55)
        for syn in range(16):
            error_type, qubit = self._syndrome_table[syn]
            binary = format(syn, '04b')
            if qubit < 0:
                error_str = 'none'
                note = 'no error (codespace)'
            else:
                error_str = '%s%d' % (error_type, qubit)
                note = '%s on physical qubit %d' % (error_type, qubit)
            print('%10d %8s %8s   %s' % (syn, binary, error_str, note))
        print('-' * 55)
        print('Total: %d distinct syndromes '
              '(Hamming bound: 2^4 = 16 = 1 + 3*5)' % len(self._syndrome_table))


# ============================================================================
#  MODULE 2:  HEISENBERG ANTIFERROMAGNET ON K4
# ============================================================================

class K4HeisenbergVQE:
    """
    Variational Quantum Eigensolver for the Heisenberg model on K4.

    H = J * sum_{i<j in K4} S_i . S_j
      = (J/4) * sum_{i<j} (X_i X_j + Y_i Y_j + Z_i Z_j)

    with J = Hb4 = 1/(4 ln 2).  K4 has 6 edges -> 18 Pauli terms.

    Exact spectrum (S1, Theorem 4.1):
        E = -3J/2  (degeneracy 2,  total spin S=0)
        E = -J/2   (degeneracy 9,  S=1 triplet + mixed)
        E = +J/2   (degeneracy 5,  S=2 quintet)

    Total: 2 + 9 + 5 = 16 = 2^4 states.

    S4 representation decomposition (S1, Section 5):
        Edge rep (dim 6) = 1 + 2 + 3
        -> U(1)_Y (dim 1) + SU(2)_L (dim 2) + SU(3)_c (dim 3)
    """

    # All 6 edges of K4
    EDGES = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

    def __init__(self, J=None):
        self.J = J if J is not None else HB4
        self.n_qubits = 4

        self._hamiltonian_matrix = self._build_hamiltonian_matrix()
        self._eigenvalues, self._eigenvectors = np.linalg.eigh(
            self._hamiltonian_matrix)

    def _build_hamiltonian_matrix(self):
        """Build the 16x16 Hamiltonian matrix."""
        dim = 2 ** self.n_qubits
        H = np.zeros((dim, dim), dtype=complex)

        for (i, j) in self.EDGES:
            for pauli in [SX, SY, SZ]:
                ops = [I2] * self.n_qubits
                ops[i] = pauli
                ops[j] = pauli
                H += (self.J / 4.0) * kron_list(ops)

        return H

    def hamiltonian_as_sparse_pauli_op(self):
        """Build as Qiskit SparsePauliOp: 18 terms (XX+YY+ZZ on 6 edges)."""
        if not QISKIT_AVAILABLE:
            raise RuntimeError('Qiskit not available')

        labels = []
        coeffs = []

        for (i, j) in self.EDGES:
            for pp in ['XX', 'YY', 'ZZ']:
                # SparsePauliOp: qubit 0 is RIGHTMOST character
                pauli_str = ['I'] * self.n_qubits
                pauli_str[i] = pp[0]
                pauli_str[j] = pp[1]
                labels.append(''.join(reversed(pauli_str)))
                coeffs.append(self.J / 4.0)

        return SparsePauliOp(labels, coeffs)

    # ------------------------------------------------------------------
    # Exact diagonalization
    # ------------------------------------------------------------------

    def exact_spectrum(self):
        """Full spectrum with degeneracy analysis and S4 decomposition."""
        evals = self._eigenvalues.real

        # Group into distinct energy levels
        levels = []
        tol = 1e-10
        for e in sorted(evals):
            if not levels or abs(e - levels[-1][0]) > tol:
                levels.append([e, 1])
            else:
                levels[-1][1] += 1

        E_ground = -3.0 * self.J / 2.0
        E_middle = -self.J / 2.0
        E_upper  = self.J / 2.0

        return {
            'J': self.J,
            'eigenvalues': evals.tolist(),
            'energy_levels': [(e, d) for e, d in levels],
            'ground_state_energy': evals[0],
            'expected_ground': E_ground,
            'ground_error': abs(evals[0] - E_ground),
            'degeneracies': [d for _, d in levels],
            'expected_degeneracies': [2, 9, 5],
            'total_states': sum(d for _, d in levels),
        }

    # ------------------------------------------------------------------
    # VQE
    # ------------------------------------------------------------------

    def _numpy_ansatz(self, params, n_layers=2):
        """Hardware-efficient ansatz using numpy (always available)."""
        dim = 2 ** self.n_qubits
        state = np.zeros(dim, dtype=complex)
        state[0] = 1.0  # |0000>

        p_idx = 0
        for layer in range(n_layers):
            for q in range(self.n_qubits):
                theta_y = params[p_idx]
                theta_z = params[p_idx + 1]
                p_idx += 2

                ry = np.array([
                    [np.cos(theta_y/2), -np.sin(theta_y/2)],
                    [np.sin(theta_y/2),  np.cos(theta_y/2)]
                ], dtype=complex)
                rz = np.array([
                    [np.exp(-1j*theta_z/2), 0],
                    [0, np.exp(1j*theta_z/2)]
                ], dtype=complex)

                gate = rz @ ry
                ops = [I2] * self.n_qubits
                ops[q] = gate
                state = kron_list(ops) @ state

            # CNOT chain + ring closure
            for ctrl in range(self.n_qubits - 1):
                state = self._apply_cnot(state, ctrl, ctrl + 1)
            state = self._apply_cnot(state, self.n_qubits - 1, 0)

        return state

    def _apply_cnot(self, state, control, target):
        """Apply CNOT to a statevector."""
        dim = len(state)
        n = self.n_qubits
        new_state = state.copy()
        for idx in range(dim):
            bits = format(idx, '0%db' % n)
            if bits[control] == '1':
                t_bit = '0' if bits[target] == '1' else '1'
                new_bits = list(bits)
                new_bits[target] = t_bit
                new_idx = int(''.join(new_bits), 2)
                new_state[new_idx] = state[idx]
                new_state[idx] = 0  # will be overwritten in pair
        # Cleaner approach: swap amplitudes pairwise
        new_state = state.copy()
        for idx in range(dim):
            bits = list(format(idx, '0%db' % n))
            if bits[control] == '1':
                partner_bits = bits.copy()
                partner_bits[target] = '0' if bits[target] == '1' else '1'
                partner_idx = int(''.join(partner_bits), 2)
                if idx < partner_idx:
                    new_state[idx] = state[partner_idx]
                    new_state[partner_idx] = state[idx]
        return new_state

    def hardware_efficient_ansatz(self, params, n_layers=2):
        """Build Qiskit circuit for hardware-efficient ansatz."""
        if not QISKIT_AVAILABLE:
            raise RuntimeError('Qiskit not available')

        qc = QuantumCircuit(self.n_qubits, name='HEA')
        p_idx = 0

        for layer in range(n_layers):
            for q in range(self.n_qubits):
                qc.ry(params[p_idx], q)
                p_idx += 1
                qc.rz(params[p_idx], q)
                p_idx += 1
            for q in range(self.n_qubits - 1):
                qc.cx(q, q + 1)
            qc.cx(self.n_qubits - 1, 0)

        return qc

    def vqe_energy(self, params, n_layers=2):
        """Evaluate <psi|H|psi> using numpy ansatz."""
        state = self._numpy_ansatz(params, n_layers)
        return np.vdot(state, self._hamiltonian_matrix @ state).real

    def run_vqe(self, n_layers=2, n_restarts=5, maxiter=500):
        """Run VQE with multiple random restarts."""
        n_params = self.n_qubits * 2 * n_layers

        best_energy = np.inf
        best_params = None
        all_results = []

        for restart in range(n_restarts):
            np.random.seed(42 + restart)
            x0 = np.random.uniform(0, 2 * np.pi, n_params)

            result = minimize(
                lambda p: self.vqe_energy(p, n_layers),
                x0, method='COBYLA',
                options={'maxiter': maxiter, 'rhobeg': 0.5}
            )

            all_results.append({
                'restart': restart,
                'energy': result.fun,
                'converged': result.success,
                'nfev': result.nfev,
            })

            if result.fun < best_energy:
                best_energy = result.fun
                best_params = result.x.copy()

        exact = self.exact_spectrum()

        return {
            'vqe_ground_energy': best_energy,
            'exact_ground_energy': exact['ground_state_energy'],
            'expected_ground': exact['expected_ground'],
            'vqe_error_abs': abs(best_energy - exact['expected_ground']),
            'vqe_error_percent': (abs(best_energy - exact['expected_ground'])
                                  / abs(exact['expected_ground']) * 100),
            'n_layers': n_layers,
            'n_params': n_params,
            'n_restarts': n_restarts,
            'best_params': best_params.tolist() if best_params is not None
                           else None,
            'all_restarts': all_results,
            'J_coupling': self.J,
        }

    # ------------------------------------------------------------------
    # Time evolution (exact, for validation)
    # ------------------------------------------------------------------

    def time_evolution_exact(self, t_total=10.0, n_steps=200):
        """Exact time evolution from |0000> tracking energy and correlations."""
        dt = t_total / n_steps
        U_dt = expm(-1j * self._hamiltonian_matrix * dt)

        state = np.zeros(16, dtype=complex)
        state[0] = 1.0

        # S0.S1 operator
        s01 = np.zeros((16, 16), dtype=complex)
        for pauli in [SX, SY, SZ]:
            ops = [I2] * 4
            ops[0] = pauli
            ops[1] = pauli
            s01 += kron_list(ops) / 4.0

        times, energies, correlations = [], [], []

        for step in range(n_steps + 1):
            t = step * dt
            E = np.vdot(state, self._hamiltonian_matrix @ state).real
            corr = np.vdot(state, s01 @ state).real

            times.append(t)
            energies.append(E)
            correlations.append(corr)

            if step < n_steps:
                state = U_dt @ state

        return {
            'times': times,
            'energies': energies,
            'correlations_01': correlations,
            'energy_conservation': max(energies) - min(energies),
            'J': self.J,
        }

    # ------------------------------------------------------------------
    # Trotterized time evolution circuit
    # ------------------------------------------------------------------

    def trotter_step_circuit(self, dt):
        """Single first-order Trotter step exp(-i H dt) as Qiskit circuit."""
        if not QISKIT_AVAILABLE:
            raise RuntimeError('Qiskit not available')

        qc = QuantumCircuit(self.n_qubits,
                            name='Trotter(dt=%.4f)' % dt)

        angle = self.J * dt / 2.0

        for (i, j) in self.EDGES:
            qc.rxx(angle, i, j)
            qc.ryy(angle, i, j)
            qc.rzz(angle, i, j)

        return qc

    # ------------------------------------------------------------------
    # S4 symmetry analysis
    # ------------------------------------------------------------------

    def s4_decomposition(self):
        """
        Decompose the K4 edge representation under S4 symmetry.

        The 6 edges of K4 carry a 6-dimensional representation of S4.
        Character analysis:

        Class:        {e}  {(12)}  {(12)(34)}  {(123)}  {(1234)}
        Size:           1      6           3        8         6
        chi_edge:       6      2           2        0         0

        Decomposition:  6 = 1 + 2 + 3
            dim 1 -> U(1)_Y
            dim 2 -> SU(2)_L
            dim 3 -> SU(3)_c
        """
        class_sizes = np.array([1, 6, 3, 8, 6])
        order_s4 = 24

        # S4 irrep character table
        chi_table = np.array([
            [1,  1,  1,  1,  1],   # trivial (dim 1)
            [1, -1,  1,  1, -1],   # sign (dim 1)
            [2,  0,  2, -1,  0],   # standard (dim 2)
            [2,  0, -2, -1,  0],   # sign x standard (dim 2)
            [3,  1, -1,  0, -1],   # perm rep - trivial (dim 3)
        ])

        # Edge representation character
        # Computed by counting edges fixed by representative of each class:
        # {e}: all 6 fixed -> 6
        # (12): {1,2} and {3,4} fixed, rest swap -> 2
        # (12)(34): {1,2} and {3,4} fixed -> 2
        # (123): edges among {1,2,3} cycle, edges to 4 cycle -> 0
        # (1234): 4-cycle on {12,23,34,14}, 2-cycle on {13,24} -> 0
        chi_edge = np.array([6, 2, 2, 0, 0])

        multiplicities = []
        for i in range(5):
            m = np.sum(class_sizes * chi_table[i] * chi_edge) / order_s4
            multiplicities.append(int(round(m.real)))

        irrep_names = ['trivial_1d', 'sign_1d', 'standard_2d',
                        'sign_standard_2d', 'perm_minus_1_3d']
        irrep_dims = [1, 1, 2, 2, 3]

        decomp_parts = []
        for name, dim, mult in zip(irrep_names, irrep_dims, multiplicities):
            if mult > 0:
                decomp_parts.append('%d*%d' % (mult, dim))

        return {
            'edge_character': chi_edge.tolist(),
            'multiplicities': dict(zip(irrep_names, multiplicities)),
            'decomposition': '6 = ' + ' + '.join(decomp_parts),
            'gauge_group_map': {
                'U(1)_Y': 'trivial (dim %d)' % (multiplicities[0] * 1),
                'SU(2)_L': 'standard (dim %d)' % (multiplicities[2] * 2),
                'SU(3)_c': 'perm-1 (dim %d)' % (multiplicities[4] * 3),
            },
            'total_dimension': sum(m * d for m, d in
                                   zip(multiplicities, irrep_dims)),
        }


# ============================================================================
#  MODULE 3:  C5 EIGENVALUE EXTRACTION (GOLDEN RATIO)
# ============================================================================

class C5EigenvalueCircuit:
    """
    Extract eigenvalues of the C5 (pentagon) adjacency matrix via VQE.

    Eigenvalues of C5 adjacency:
        lambda_k = 2 cos(2*pi*k/5)  for k = 0, 1, 2, 3, 4

    Explicitly:
        lambda_0 = 2                           (k=0)
        lambda_1 = lambda_4 = 1/phi ~ 0.618    (k=1,4)
        lambda_2 = lambda_3 = -phi ~ -1.618    (k=2,3)

    QSD prediction (S1, Theorem 6.1):
        |lambda_2| / |lambda_1| = phi / (1/phi) = phi^2

    Qubit encoding: 5 qubits, single-excitation sector.
        H = (1/2) sum_{(i,j) in C5} (X_i X_j + Y_i Y_j)
    """

    EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]

    def __init__(self):
        self.n_qubits = 5
        self.eigenvalues_exact = sorted([
            2.0 * np.cos(2.0 * np.pi * k / 5.0) for k in range(5)
        ])
        self._hamiltonian_matrix = self._build_hamiltonian_matrix()
        self._adjacency_5x5 = self._build_adjacency_5x5()

    def _build_adjacency_5x5(self):
        """Build the 5x5 C5 adjacency matrix."""
        A = np.zeros((5, 5))
        for (i, j) in self.EDGES:
            A[i, j] = 1.0
            A[j, i] = 1.0
        return A

    def _build_hamiltonian_matrix(self):
        """XX+YY hopping Hamiltonian on 5 qubits (32x32)."""
        dim = 2 ** self.n_qubits
        H = np.zeros((dim, dim), dtype=complex)

        for (i, j) in self.EDGES:
            for pauli in [SX, SY]:
                ops = [I2] * self.n_qubits
                ops[i] = pauli
                ops[j] = pauli
                H += kron_list(ops) / 2.0

        return H

    def hamiltonian_as_sparse_pauli_op(self):
        """Build as Qiskit SparsePauliOp (10 terms)."""
        if not QISKIT_AVAILABLE:
            raise RuntimeError('Qiskit not available')

        labels = []
        coeffs = []
        for (i, j) in self.EDGES:
            for pp in ['XX', 'YY']:
                pauli_str = ['I'] * self.n_qubits
                pauli_str[i] = pp[0]
                pauli_str[j] = pp[1]
                labels.append(''.join(reversed(pauli_str)))
                coeffs.append(0.5)

        return SparsePauliOp(labels, coeffs)

    # ------------------------------------------------------------------
    # Exact analysis
    # ------------------------------------------------------------------

    def exact_spectrum(self):
        """Full spectrum analysis: 5x5 adjacency and 32-dim qubit Hamiltonian."""
        evals_5x5 = np.sort(np.linalg.eigvalsh(self._adjacency_5x5))
        evals_32 = np.sort(np.linalg.eigvalsh(self._hamiltonian_matrix).real)

        # Extract single-excitation sector from 32-dim
        single_exc_indices = [2**(self.n_qubits - 1 - k) for k in range(5)]
        H_single = np.zeros((5, 5), dtype=complex)
        for a, idx_a in enumerate(single_exc_indices):
            for b, idx_b in enumerate(single_exc_indices):
                H_single[a, b] = self._hamiltonian_matrix[idx_a, idx_b]
        evals_single = np.sort(np.linalg.eigvalsh(H_single).real)

        phi = GOLDEN_RATIO
        lambda_neg = evals_5x5[0]     # -phi
        lambda_pos = evals_5x5[2]     # 1/phi

        ratio = abs(lambda_neg) / lambda_pos
        expected_ratio = phi ** 2

        return {
            'adjacency_eigenvalues': evals_5x5.tolist(),
            'single_excitation_eigenvalues': evals_single.tolist(),
            'eigenvalues_match': np.allclose(evals_5x5, evals_single),
            'lambda_neg': lambda_neg,
            'lambda_pos': lambda_pos,
            'ratio_magnitude': ratio,
            'phi_squared': expected_ratio,
            'golden_ratio_verified': abs(ratio - expected_ratio) < 1e-12,
            'phi_squared_error': abs(ratio - expected_ratio),
        }

    # ------------------------------------------------------------------
    # VQE in the single-excitation subspace
    # ------------------------------------------------------------------

    def excitation_preserving_ansatz(self, params, initial_qubit=0,
                                     n_layers=2):
        """
        Ansatz preserving single-excitation sector.

        Works in the 5-dim subspace directly with Givens rotations
        between adjacent sites (C5 edge structure).
        """
        state = np.zeros(5, dtype=complex)
        state[initial_qubit] = 1.0

        p_idx = 0
        for layer in range(n_layers):
            for edge_idx, (i, j) in enumerate(self.EDGES):
                if p_idx >= len(params):
                    break
                theta = params[p_idx]
                p_idx += 1

                c = np.cos(theta)
                s = np.sin(theta)
                new_i = c * state[i] - s * state[j]
                new_j = s * state[i] + c * state[j]
                state[i] = new_i
                state[j] = new_j

        return state

    def vqe_eigenvalue(self, target='ground', n_layers=3,
                       n_restarts=10, maxiter=300):
        """
        Find eigenvalues of C5 adjacency via VQE.

        target='ground': find lowest eigenvalue
        target='all': find all distinct eigenvalues via deflation
        """
        n_params = 5 * n_layers
        A = self._adjacency_5x5.copy()

        if target == 'ground':
            return self._vqe_single(A, n_params, n_layers, n_restarts,
                                    maxiter, label='ground')

        elif target == 'all':
            found_eigenvalues = []
            found_eigenvectors = []
            A_deflated = A.copy()

            # 3 distinct eigenvalues for C5: -phi (x2), 1/phi (x2), 2 (x1)
            # Deflation with degeneracy awareness: if we find an eigenvalue
            # we already have, apply stronger penalty to the full subspace
            tol_degenerate = 0.05

            for level in range(5):  # up to 5 attempts for 3 distinct values
                result = self._vqe_single(
                    A_deflated, n_params, n_layers, n_restarts, maxiter,
                    label='level_%d' % level)

                ev = result['eigenvalue']
                evec = result['eigenvector']

                # Check if this is a genuinely new eigenvalue
                is_new = True
                for prev_ev in found_eigenvalues:
                    if abs(ev - prev_ev) < tol_degenerate:
                        is_new = False
                        break

                if is_new:
                    found_eigenvalues.append(ev)
                found_eigenvectors.append(evec)

                # Always deflate the found eigenvector
                penalty = 20.0 * (abs(ev) + 1.0)
                A_deflated = (A_deflated
                              + penalty * np.outer(evec, evec.conj()).real)

                if len(found_eigenvalues) >= 3:
                    break

            exact_distinct = sorted(set([
                round(e, 10) for e in np.linalg.eigvalsh(A).tolist()
            ]))
            found_sorted = sorted(found_eigenvalues)

            # Golden ratio: ratio of distinct non-zero eigenvalue magnitudes
            # We need |lambda_neg| / lambda_pos where lambda_neg < 0 < lambda_pos
            neg_vals = [e for e in found_sorted if e < -0.1]
            pos_vals = [e for e in found_sorted if 0.1 < e < 1.9]
            if neg_vals and pos_vals:
                vqe_ratio = abs(neg_vals[0]) / pos_vals[0]
            else:
                vqe_ratio = None

            return {
                'found_eigenvalues': found_sorted,
                'exact_eigenvalues': exact_distinct,
                'ratio': vqe_ratio,
                'phi_squared': GOLDEN_RATIO_SQ,
            }

    def _vqe_single(self, A, n_params, n_layers, n_restarts, maxiter,
                     label=''):
        """Run VQE for a single eigenvalue."""
        best_energy = np.inf
        best_params = None
        best_state = None
        best_init_q = 0

        for restart in range(n_restarts):
            np.random.seed(137 + restart)
            x0 = np.random.uniform(-np.pi, np.pi, n_params)

            for init_q in range(5):
                def cost(params, iq=init_q):
                    state = self.excitation_preserving_ansatz(
                        params, initial_qubit=iq, n_layers=n_layers)
                    return (state.conj() @ A @ state).real

                result = minimize(cost, x0, method='COBYLA',
                                  options={'maxiter': maxiter})

                if result.fun < best_energy:
                    best_energy = result.fun
                    best_params = result.x.copy()
                    best_init_q = init_q
                    best_state = self.excitation_preserving_ansatz(
                        best_params, initial_qubit=init_q,
                        n_layers=n_layers)

        return {
            'eigenvalue': best_energy,
            'eigenvector': best_state,
            'label': label,
        }

    # ------------------------------------------------------------------
    # Laplacian (Mathieu connection)
    # ------------------------------------------------------------------

    def laplacian_spectrum(self):
        """
        Spectrum of C5 graph Laplacian L = D - A.

        Laplacian eigenvalues:
            mu_k = 2 - 2 cos(2 pi k / 5)

        Ratio of non-zero eigenvalues:
            mu_max / mu_min = (5+sqrt(5))/(5-sqrt(5)) = phi^2

        This determines the Mathieu equation parameters (S3, Section 3).
        """
        A = self._adjacency_5x5
        D = 2.0 * np.eye(5)
        L = D - A

        evals_L = np.sort(np.linalg.eigvalsh(L))

        mu_min = evals_L[1]
        mu_max = evals_L[3]
        ratio = mu_max / mu_min

        mu_min_exact = (5.0 - np.sqrt(5.0)) / 2.0
        mu_max_exact = (5.0 + np.sqrt(5.0)) / 2.0

        return {
            'laplacian_eigenvalues': evals_L.tolist(),
            'mu_min': mu_min,
            'mu_max': mu_max,
            'mu_min_exact': mu_min_exact,
            'mu_max_exact': mu_max_exact,
            'ratio': ratio,
            'phi_squared': GOLDEN_RATIO_SQ,
            'ratio_match': abs(ratio - GOLDEN_RATIO_SQ) < 1e-12,
            'mathieu_connection': (
                'Laplacian eigenvalues set Mathieu potential '
                'V(theta) = V0(1 - cos 5*theta) parameters (S3)'),
        }

    def verify_golden_ratio(self):
        """Complete golden ratio verification using all methods."""
        exact = self.exact_spectrum()
        vqe_all = self.vqe_eigenvalue(target='all', n_layers=3, n_restarts=8)
        lap = self.laplacian_spectrum()

        return {
            'exact_eigenvalues': exact['adjacency_eigenvalues'],
            'exact_ratio': exact['ratio_magnitude'],
            'exact_phi_sq_match': exact['golden_ratio_verified'],
            'vqe_eigenvalues': vqe_all['found_eigenvalues'],
            'vqe_ratio': vqe_all.get('ratio'),
            'laplacian_ratio': lap['ratio'],
            'laplacian_match': lap['ratio_match'],
            'phi_squared': GOLDEN_RATIO_SQ,
        }


# ============================================================================
#  HARDWARE EXECUTION HELPERS
# ============================================================================

@dataclass
class HardwareConfig:
    """Configuration for IBM Quantum hardware execution."""
    use_hardware: bool = False
    backend_name: str = 'ibm_brisbane'
    optimization_level: int = 3
    n_shots: int = 4096
    resilience_level: int = 1

    def get_backend(self):
        if not self.use_hardware:
            if AER_AVAILABLE:
                return AerSimulator()
            raise RuntimeError('Aer not available')
        else:
            try:
                from qiskit_ibm_runtime import QiskitRuntimeService
                service = QiskitRuntimeService()
                return service.backend(self.backend_name)
            except ImportError:
                raise RuntimeError(
                    'qiskit-ibm-runtime required for hardware execution')


# ============================================================================
#  MAIN EXECUTION
# ============================================================================

def run_all(use_hardware=False):
    """Run all three core QSD Qiskit simulations."""
    results = {}
    sep = '=' * 70

    # ------------------------------------------------------------------
    # Module 1: [[5,1,3]] Syndrome Extraction
    # ------------------------------------------------------------------
    print('\n' + sep)
    print('  MODULE 1:  [[5,1,3]] Quantum Error-Correcting Code')
    print(sep + '\n')

    code = Code513Circuit()
    code.print_syndrome_table()

    print('\nStatevector syndrome verification:')
    sv_results = code.run_all_syndromes_statevector()
    results['code513_statevector'] = sv_results

    n_pass = sum(1 for r in sv_results['results'] if r['match'])
    n_total_r = len(sv_results['results'])
    print('  Passed: %d/%d' % (n_pass, n_total_r))
    print('  All match: %s' % sv_results['all_match'])
    print('  Hamming bound: %s' % sv_results['hamming_bound'])

    print('\n  Sample results:')
    for r in sv_results['results'][:6]:
        status = 'OK' if r['match'] else 'FAIL'
        print('    Error %3s: syndrome %s (%2d) -> %3s  %s' % (
            r['error'], r['syndrome_binary'], r['syndrome_int'],
            r['predicted_error'], status))
    print('    ... (%d more)' % (n_total_r - 6))

    if QISKIT_AVAILABLE and AER_AVAILABLE:
        print('\nCircuit-based syndrome verification (Aer, 4096 shots):')
        circ_results = code.run_all_syndromes_circuit(n_shots=4096)
        results['code513_circuit'] = circ_results
        n_pass_c = sum(1 for r in circ_results['results'] if r['match'])
        print('  Passed: %d/%d' % (n_pass_c, len(circ_results['results'])))
        avg_fid = np.mean([r['fidelity'] for r in circ_results['results']])
        print('  Average syndrome fidelity: %.4f' % avg_fid)
    else:
        print('\n  [Qiskit/Aer not available -- circuit test skipped]')

    # ------------------------------------------------------------------
    # Module 2: K4 Heisenberg VQE
    # ------------------------------------------------------------------
    print('\n' + sep)
    print('  MODULE 2:  K4 Heisenberg Antiferromagnet (VQE)')
    print(sep + '\n')

    k4 = K4HeisenbergVQE()

    spec = k4.exact_spectrum()
    results['k4_exact'] = spec

    print('Coupling J = Hb4 = 1/(4 ln 2) = %.12f' % k4.J)
    print('\nExact spectrum:')
    for E, d in spec['energy_levels']:
        print('  E = %+.12f   degeneracy = %d' % (E, d))
    print('\nGround state:')
    print('  Computed:  %.12f' % spec['ground_state_energy'])
    print('  Expected:  %.12f' % spec['expected_ground'])
    print('  Error:     %.2e' % spec['ground_error'])
    print('\nDegeneracies: %s (expected: %s)' % (
        spec['degeneracies'], spec['expected_degeneracies']))

    s4 = k4.s4_decomposition()
    results['k4_s4'] = s4
    print('\nS4 edge representation: %s' % s4['decomposition'])
    for group, irrep in s4['gauge_group_map'].items():
        print('    %10s <- %s' % (group, irrep))

    print('\nRunning VQE (2 layers, 5 restarts)...')
    vqe = k4.run_vqe(n_layers=2, n_restarts=5, maxiter=500)
    results['k4_vqe'] = vqe
    print('  VQE ground:   %.12f' % vqe['vqe_ground_energy'])
    print('  Exact ground:  %.12f' % vqe['exact_ground_energy'])
    print('  VQE error: %.6f%%' % vqe['vqe_error_percent'])

    print('\nTime evolution (t=10, 200 steps)...')
    tevol = k4.time_evolution_exact(t_total=10.0, n_steps=200)
    results['k4_time_evolution'] = tevol
    print('  Energy conservation: max deviation = %.2e' %
          tevol['energy_conservation'])

    # ------------------------------------------------------------------
    # Module 3: C5 Eigenvalue Extraction
    # ------------------------------------------------------------------
    print('\n' + sep)
    print('  MODULE 3:  C5 Pentagon Eigenvalues (Golden Ratio)')
    print(sep + '\n')

    c5 = C5EigenvalueCircuit()

    exact_c5 = c5.exact_spectrum()
    results['c5_exact'] = exact_c5

    print('C5 adjacency eigenvalues:')
    for i, ev in enumerate(exact_c5['adjacency_eigenvalues']):
        print('  lambda_%d = %+.12f' % (i, ev))
    print('\nSingle-excitation match: %s' % exact_c5['eigenvalues_match'])
    print('\nGolden ratio:')
    print('  |lambda_neg|/lambda_pos = %.12f' % exact_c5['ratio_magnitude'])
    print('  phi^2                   = %.12f' % exact_c5['phi_squared'])
    print('  Match (12 dec):           %s' % exact_c5['golden_ratio_verified'])

    lap = c5.laplacian_spectrum()
    results['c5_laplacian'] = lap
    print('\nLaplacian eigenvalues: %s' %
          ['%.6f' % e for e in lap['laplacian_eigenvalues']])
    print('  mu_max/mu_min = %.12f = phi^2 ? %s' % (
        lap['ratio'], lap['ratio_match']))

    print('\nRunning VQE for all eigenvalues (deflation)...')
    vqe_c5 = c5.vqe_eigenvalue(target='all', n_layers=3, n_restarts=8)
    results['c5_vqe'] = vqe_c5
    print('  VQE eigenvalues:  %s' %
          ['%.6f' % e for e in vqe_c5['found_eigenvalues']])
    print('  Exact (distinct): %s' %
          ['%.6f' % e for e in vqe_c5['exact_eigenvalues']])
    if vqe_c5.get('ratio') is not None:
        print('  VQE ratio:  %.6f' % vqe_c5['ratio'])
        print('  phi^2:      %.6f' % vqe_c5['phi_squared'])

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print('\n' + sep)
    print('  SUMMARY')
    print(sep)

    print('\n  [[5,1,3]] Code:')
    print('    Syndrome extraction:  %s' %
          ('PASS' if sv_results['all_match'] else 'FAIL'))
    print('    Hamming bound:        SATURATED (16 = 1 + 3*5)')
    print('    Distinct syndromes:   %d/16' %
          sv_results['n_distinct_syndromes'])

    print('\n  K4 Heisenberg (J = Hb4):')
    print('    Ground E0 = -3J/2:    %.2e error' % spec['ground_error'])
    print('    Degeneracies [2,9,5]: %s' %
          (spec['degeneracies'] == spec['expected_degeneracies']))
    print('    S4: 6 = 1+2+3:       %s' % (s4['total_dimension'] == 6))
    print('    VQE accuracy:         %.6f%%' % vqe['vqe_error_percent'])

    print('\n  C5 Pentagon:')
    print('    phi^2 (adjacency):    %s' % exact_c5['golden_ratio_verified'])
    print('    phi^2 (Laplacian):    %s' % lap['ratio_match'])
    print('    VQE levels found:     %d' % len(vqe_c5['found_eigenvalues']))

    print('\n  QSD Triad:')
    print('    Hb4   = %.12f  (K4 exchange)' % HB4)
    print('    sigma = %.12f  (K4-C5 strain)' % SIGMA)
    print('    varpi = %.12f  (C5 spectral bond)' % VARPI)

    return results


if __name__ == '__main__':
    print('QSD Qiskit Simulation Suite -- Core Circuits')
    print('Qiskit available: %s' % QISKIT_AVAILABLE)
    print('Aer available:    %s' % AER_AVAILABLE)
    print('Mode: %s' % ('numpy fallback' if not QISKIT_AVAILABLE
                         else 'full Qiskit'))

    results = run_all(use_hardware=False)
