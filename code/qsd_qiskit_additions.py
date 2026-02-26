#!/usr/bin/env python3
"""
QSD Qiskit Simulation Suite -- Additional Circuits
====================================================

Three extensions to the core quantum circuits:

4. K4TrotterEvolution:  Trotterized time evolution on K4 Heisenberg
   - First-order and second-order Trotter decomposition
   - All 6 edge correlations <S_i . S_j> tracked in real time
   - Trotter vs exact fidelity comparison
   - Circuit: RXX + RYY + RZZ per edge per step (4 qubits)
   - QSD significance: exchange dynamics at coupling J = Hb4

5. Code513ErrorCorrection:  Full error correction cycle
   - Encode -> error -> syndrome -> correct -> verify
   - Weight-1 errors: corrected (distance 3)
   - Weight-2 errors: detected but not corrected
   - Multi-round error correction with random noise
   - Logical gate verification (X_L, Z_L)

6. MathieuGroundState:  Z5 cosine potential from C5 continuum limit
   - V(theta) = V0(1 - cos 5*theta), derived from C5 tight-binding (S3)
   - Discretized on periodic grid, VQE ground state
   - Band structure from Bloch theory
   - Connection: small-oscillation frequency -> m_H = 5*mu_rad

Dependencies:
    Required : numpy, scipy, matplotlib
    Optional : qiskit, qiskit-aer (for circuit execution / hardware)
    Required : qsd_qiskit_suite.py (core classes and utilities)

References:
    [S1] qsd_s1_formal_proofs_v2.tex  - Code structure, stabilizers
    [S3] qsd_s3_lagrangian.tex        - K4 Heisenberg, C5 Mathieu, Berry phase
    [S5] qsd_s5_syndrome_prediction.tex - Syndrome phenomenology

Authors: QSD Collaboration
"""

from __future__ import annotations

import os
import sys
import warnings
from typing import Dict, List, Tuple, Optional

import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize
from scipy.special import mathieu_a, mathieu_b

# ---------------------------------------------------------------------------
# Import core suite (try several paths)
# ---------------------------------------------------------------------------
for _path in ['.', '/mnt/user-data/outputs', '/home/claude']:
    if os.path.isfile(os.path.join(_path, 'qsd_qiskit_suite.py')):
        if _path not in sys.path:
            sys.path.insert(0, _path)
        break

from qsd_qiskit_suite import (
    Code513Circuit, K4HeisenbergVQE, C5EigenvalueCircuit,
    kron_list, pauli_string_to_matrix,
    I2, SX, SY, SZ,
    QISKIT_AVAILABLE, AER_AVAILABLE,
)

# ---------------------------------------------------------------------------
# Import QSD constants
# ---------------------------------------------------------------------------
for _path in ['.', '/mnt/user-data/outputs', '/home/claude']:
    if os.path.isfile(os.path.join(_path, 'qsd_constants.py')):
        if _path not in sys.path:
            sys.path.insert(0, _path)
        break

try:
    from qsd_constants import (
        GOLDEN_RATIO, GOLDEN_RATIO_SQ, LN2, HB4, SIGMA, VARPI,
        MU_RAD, E_SYNDROME_QSD, M_HIGGS_QSD,
    )
except ImportError:
    GOLDEN_RATIO    = (1.0 + np.sqrt(5.0)) / 2.0
    GOLDEN_RATIO_SQ = GOLDEN_RATIO ** 2
    LN2             = np.log(2.0)
    HB4             = 1.0 / (4.0 * LN2)
    SIGMA           = 3.0 / (80.0 * GOLDEN_RATIO_SQ)
    VARPI           = np.pi * GOLDEN_RATIO_SQ
    MU_RAD          = 25.341111730942625
    E_SYNDROME_QSD  = MU_RAD * (1.0 + 8.0 * SIGMA)
    M_HIGGS_QSD     = 5.0 * MU_RAD
    warnings.warn("qsd_constants.py not found; using inline fallback.")

if QISKIT_AVAILABLE:
    from qiskit import QuantumCircuit, transpile

# Pauli map
PAULI_MAP = {'I': I2, 'X': SX, 'Y': SY, 'Z': SZ}


# ============================================================================
#  MODULE 4:  K4 TROTTER TIME EVOLUTION
# ============================================================================

class K4TrotterEvolution:
    """
    Trotterized time evolution of the Heisenberg antiferromagnet on K4.

    The K4 Hamiltonian decomposes into 6 pairwise terms:

        H = J * sum_{(i,j) in K4} S_i . S_j
          = sum_{(i,j)} H_{ij}

    where H_{ij} = (J/4)(X_i X_j + Y_i Y_j + Z_i Z_j).

    First-order Trotter:
        exp(-i H dt) ~ prod_{(i,j)} exp(-i H_{ij} dt)

    Second-order (symmetric) Trotter:
        exp(-i H dt) ~ prod_{(i,j)} exp(-i H_{ij} dt/2)
                      * prod_{(j,i) reversed} exp(-i H_{ij} dt/2)

    Circuit implementation: each exp(-i H_{ij} dt) decomposes into
        RXX(J*dt/2) . RYY(J*dt/2) . RZZ(J*dt/2)
    on qubits (i, j), giving 3 two-qubit gates per edge per step.

    QSD significance (S1, S3):
        The Trotterized dynamics compute the PHYSICAL time evolution
        of the K4 spin system.  Correlation oscillation frequencies
        are multiples of the energy gaps, which are set by J = Hb4.
        This is NOT encoding classical numbers -- it is genuine
        quantum simulation of the exchange Hamiltonian.
    """

    # K4 edges
    EDGES = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

    # Named initial states
    INITIAL_STATES = {
        'neel':     0b0101,   # |0101>
        'neel_alt': 0b1010,   # |1010>
        'all_up':   0b0000,   # |0000>
    }

    def __init__(self, J: float = None):
        self.J = J if J is not None else HB4
        self.n_qubits = 4
        self.dim = 16

        # Build Hamiltonians
        self._H_full = self._build_full_hamiltonian()
        self._H_edges = self._build_edge_hamiltonians()

        # Build observables
        self._corr_ops = self._build_correlation_operators()
        self._S2_total = 3.0 * np.eye(self.dim, dtype=complex) + \
            2.0 * self._H_full / self.J
        self._Sz_total = self._build_total_Sz()

    def _build_full_hamiltonian(self) -> np.ndarray:
        H = np.zeros((self.dim, self.dim), dtype=complex)
        for i, j in self.EDGES:
            for P in [SX, SY, SZ]:
                ops = [I2] * 4
                ops[i] = P
                ops[j] = P
                H += self.J * kron_list(ops)
        return H

    def _build_edge_hamiltonians(self) -> Dict[Tuple[int, int], np.ndarray]:
        edges = {}
        for i, j in self.EDGES:
            H_e = np.zeros((self.dim, self.dim), dtype=complex)
            for P in [SX, SY, SZ]:
                ops = [I2] * 4
                ops[i] = P
                ops[j] = P
                H_e += self.J * kron_list(ops)
            edges[(i, j)] = H_e
        return edges

    def _build_correlation_operators(self) -> Dict:
        ops = {}
        for i, j in self.EDGES:
            C = np.zeros((self.dim, self.dim), dtype=complex)
            for P in [SX, SY, SZ]:
                mats = [I2] * 4
                mats[i] = P
                mats[j] = P
                C += kron_list(mats)
            ops[(i, j)] = C
        return ops

    def _build_total_Sz(self) -> np.ndarray:
        Sz = np.zeros((self.dim, self.dim), dtype=complex)
        for i in range(4):
            ops = [I2] * 4
            ops[i] = SZ
            Sz += kron_list(ops)
        return Sz

    # ------------------------------------------------------------------
    # Initial states
    # ------------------------------------------------------------------

    def prepare_initial_state(self, name: str = 'neel') -> np.ndarray:
        state = np.zeros(self.dim, dtype=complex)
        if name in self.INITIAL_STATES:
            state[self.INITIAL_STATES[name]] = 1.0
        elif name == 'ghz':
            state[0b0000] = 1.0 / np.sqrt(2.0)
            state[0b1111] = 1.0 / np.sqrt(2.0)
        elif name == 'singlet_pair':
            # (|01>-|10>)/sqrt2 x (|01>-|10>)/sqrt2 on qubits (0,1) and (2,3)
            state[0b0101] =  0.5
            state[0b0110] = -0.5
            state[0b1001] = -0.5
            state[0b1010] =  0.5
        else:
            raise ValueError('Unknown initial state: %s' % name)
        return state

    # ------------------------------------------------------------------
    # Trotter unitaries
    # ------------------------------------------------------------------

    def _first_order_trotter(self, dt: float) -> np.ndarray:
        U = np.eye(self.dim, dtype=complex)
        for edge in self.EDGES:
            U = expm(-1j * self._H_edges[edge] * dt) @ U
        return U

    def _second_order_trotter(self, dt: float) -> np.ndarray:
        U = np.eye(self.dim, dtype=complex)
        for edge in self.EDGES:
            U = expm(-1j * self._H_edges[edge] * dt / 2.0) @ U
        for edge in reversed(self.EDGES):
            U = expm(-1j * self._H_edges[edge] * dt / 2.0) @ U
        return U

    # ------------------------------------------------------------------
    # Main evolution
    # ------------------------------------------------------------------

    def evolve(
        self,
        t_total: float = 10.0,
        n_steps: int = 200,
        order: int = 1,
        initial_state: str = 'neel',
    ) -> Dict:
        """
        Trotterized time evolution tracking all observables.

        Parameters
        ----------
        t_total : float
            Total evolution time (natural units).
        n_steps : int
            Number of Trotter steps.
        order : int
            1 (first-order) or 2 (symmetric Trotter).
        initial_state : str or ndarray
            Name or explicit vector.
        """
        dt = t_total / n_steps

        if isinstance(initial_state, str):
            psi_0 = self.prepare_initial_state(initial_state)
        else:
            psi_0 = np.asarray(initial_state, dtype=complex)
            psi_0 /= np.linalg.norm(psi_0)

        if order == 1:
            U_trotter = self._first_order_trotter(dt)
        else:
            U_trotter = self._second_order_trotter(dt)

        U_exact = expm(-1j * self._H_full * dt)

        # Allocate storage
        times = np.zeros(n_steps + 1)
        energy = np.zeros(n_steps + 1)
        total_s2 = np.zeros(n_steps + 1)
        total_sz = np.zeros(n_steps + 1)
        fidelity = np.zeros(n_steps + 1)
        correlations = {e: np.zeros(n_steps + 1) for e in self.EDGES}

        psi_t = psi_0.copy()
        psi_ex = psi_0.copy()

        for step in range(n_steps + 1):
            times[step] = step * dt

            energy[step] = np.vdot(psi_t, self._H_full @ psi_t).real
            total_s2[step] = np.vdot(psi_t, self._S2_total @ psi_t).real
            total_sz[step] = np.vdot(psi_t, self._Sz_total @ psi_t).real

            for e in self.EDGES:
                correlations[e][step] = np.vdot(
                    psi_t, self._corr_ops[e] @ psi_t).real

            fidelity[step] = abs(np.vdot(psi_ex, psi_t)) ** 2

            if step < n_steps:
                psi_t = U_trotter @ psi_t
                psi_ex = U_exact @ psi_ex

        energy_drift = np.max(np.abs(energy - energy[0]))

        return {
            'times': times,
            'energy': energy,
            'total_spin_squared': total_s2,
            'total_sz': total_sz,
            'correlations': {
                '(%d,%d)' % e: correlations[e] for e in self.EDGES
            },
            'fidelity_vs_exact': fidelity,
            'energy_drift': energy_drift,
            'min_fidelity': float(np.min(fidelity)),
            'final_fidelity': float(fidelity[-1]),
            'trotter_order': order,
            'dt': dt,
            'n_steps': n_steps,
            't_total': t_total,
            'J': self.J,
            'initial_state': initial_state if isinstance(
                initial_state, str) else 'custom',
        }

    # ------------------------------------------------------------------
    # Error scaling analysis
    # ------------------------------------------------------------------

    def trotter_error_scaling(
        self,
        t_fixed: float = 5.0,
        step_counts: Optional[List[int]] = None,
    ) -> Dict:
        """Measure infidelity vs step count for both Trotter orders."""
        if step_counts is None:
            step_counts = [5, 10, 20, 50, 100, 200, 500]

        psi_0 = self.prepare_initial_state('neel')
        U_exact_full = expm(-1j * self._H_full * t_fixed)
        psi_exact = U_exact_full @ psi_0

        dt_vals = []
        err1 = []
        err2 = []

        for n in step_counts:
            dt = t_fixed / n
            dt_vals.append(dt)

            for order_val, err_list in [(1, err1), (2, err2)]:
                if order_val == 1:
                    U_step = self._first_order_trotter(dt)
                else:
                    U_step = self._second_order_trotter(dt)

                psi = psi_0.copy()
                for _ in range(n):
                    psi = U_step @ psi

                fid = abs(np.vdot(psi_exact, psi)) ** 2
                err_list.append(1.0 - fid)

        return {
            'step_counts': step_counts,
            'dt_values': dt_vals,
            't_fixed': t_fixed,
            'error_order1': err1,
            'error_order2': err2,
        }

    # ------------------------------------------------------------------
    # Qiskit circuit
    # ------------------------------------------------------------------

    def trotter_circuit(
        self,
        n_steps: int = 5,
        dt: float = 0.1,
        order: int = 1,
        initial_state: str = 'neel',
    ) -> 'QuantumCircuit':
        """Build full Trotter circuit for Qiskit execution."""
        if not QISKIT_AVAILABLE:
            raise RuntimeError('Qiskit not installed.')

        qc = QuantumCircuit(4, name='Trotter_K4_n%d_o%d' % (n_steps, order))

        # Prepare initial state
        if initial_state == 'neel':
            qc.x(1)
            qc.x(3)
        elif initial_state == 'neel_alt':
            qc.x(0)
            qc.x(2)
        elif initial_state == 'ghz':
            qc.h(0)
            for q in range(1, 4):
                qc.cx(0, q)

        qc.barrier()

        # Angle for RXX, RYY, RZZ
        # exp(-i J/4 (XX+YY+ZZ) dt) ~ RXX(J*dt/2) RYY(J*dt/2) RZZ(J*dt/2)
        angle = self.J * dt / 2.0

        for step in range(n_steps):
            if order == 1:
                for i, j in self.EDGES:
                    qc.rxx(2 * angle, i, j)
                    qc.ryy(2 * angle, i, j)
                    qc.rzz(2 * angle, i, j)
            else:
                for i, j in self.EDGES:
                    qc.rxx(angle, i, j)
                    qc.ryy(angle, i, j)
                    qc.rzz(angle, i, j)
                for i, j in reversed(self.EDGES):
                    qc.rxx(angle, i, j)
                    qc.ryy(angle, i, j)
                    qc.rzz(angle, i, j)
            qc.barrier()

        return qc

    def print_summary(self, result: Dict):
        print('\nK4 Trotter Summary')
        print('=' * 60)
        print('  J = Hb4 = %.12f' % result['J'])
        print('  Initial: %s,  order: %d' % (
            result['initial_state'], result['trotter_order']))
        print('  dt = %.6f,  steps = %d,  t = %.2f' % (
            result['dt'], result['n_steps'], result['t_total']))
        print('  Energy drift:     %.2e' % result['energy_drift'])
        print('  Final fidelity:   %.10f' % result['final_fidelity'])
        print('  Min fidelity:     %.10f' % result['min_fidelity'])


# ============================================================================
#  MODULE 5:  [[5,1,3]] FULL ERROR CORRECTION
# ============================================================================

class Code513ErrorCorrection:
    """
    Full quantum error correction cycle for the [[5,1,3]] code.

    Extends Code513Circuit with:

    1. Full correction cycle:
       encode |psi>_L -> inject error -> syndrome -> correct -> verify

    2. Weight-2 error detection:
       Distance d=3 detects any weight-2 error (syndrome != 0)
       but cannot uniquely identify it.

    3. Multi-round error correction under random noise streams.

    4. Logical gate verification: X_L, Z_L properties.

    QSD significance (S1, S5):
        The error correction cycle IS the physical process that
        maintains spacetime coherence.  Each syndrome measurement
        is an observation of the vacuum's error-correcting response.
        The 28 GeV resonance (S5) is the ENERGY of this process.
    """

    def __init__(self):
        self.code = Code513Circuit()
        self.dim = 32  # 2^5

    def _error_operator(self, error_type: str, qubit: int) -> np.ndarray:
        """Build single-qubit error operator on 5-qubit space."""
        ops = [I2] * 5
        if error_type != 'I':
            ops[qubit] = PAULI_MAP[error_type]
        return kron_list(ops)

    def _two_qubit_error(
        self, t1: str, q1: int, t2: str, q2: int,
    ) -> np.ndarray:
        """Build weight-2 error operator."""
        ops = [I2] * 5
        ops[q1] = PAULI_MAP[t1]
        ops[q2] = PAULI_MAP[t2]
        return kron_list(ops)

    def _measure_syndrome(self, state: np.ndarray) -> int:
        """Measure 4-bit syndrome from stabiliser eigenvalues."""
        syn = 0
        for i, g in enumerate(self.code.stabilizer_matrices):
            ev = np.vdot(state, g @ state).real
            if ev < 0:
                syn += (1 << (3 - i))
        return syn

    # ------------------------------------------------------------------
    # Full correction cycle
    # ------------------------------------------------------------------

    def correct_single_error(
        self,
        error_type: str,
        error_qubit: int,
        logical_state: str = '0',
    ) -> Dict:
        """
        Full cycle: encode -> error -> syndrome -> correct -> verify.

        Returns recovery fidelity and identification correctness.
        """
        cw = self.code.get_codewords()
        table = self.code.get_syndrome_table()

        psi_orig = cw['logical_zero'].copy() if logical_state == '0' \
            else cw['logical_one'].copy()

        # Inject error
        E = self._error_operator(error_type, error_qubit)
        psi_err = E @ psi_orig

        # Syndrome
        syn = self._measure_syndrome(psi_err)

        # Correction lookup
        if syn == 0:
            ct, cq = 'I', -1
        else:
            ct, cq = table[syn]

        # Apply correction
        C = self._error_operator(ct, max(cq, 0))
        psi_rec = C @ psi_err

        fidelity = abs(np.vdot(psi_orig, psi_rec)) ** 2
        correct_id = (ct == error_type and cq == error_qubit)

        return {
            'error': '%s_%d' % (error_type, error_qubit),
            'syndrome': syn,
            'syndrome_binary': format(syn, '04b'),
            'correction': '%s_%d' % (ct, cq),
            'correct_identification': correct_id,
            'recovery_fidelity': fidelity,
            'success': fidelity > 1.0 - 1e-12,
            'logical': logical_state,
        }

    # ------------------------------------------------------------------
    # Test all weight-1 errors
    # ------------------------------------------------------------------

    def test_all_weight1(self) -> Dict:
        """Test correction of all 15 single-qubit errors on both codewords."""
        results = []
        for log_s in ['0', '1']:
            for et in ['X', 'Y', 'Z']:
                for q in range(5):
                    results.append(self.correct_single_error(et, q, log_s))

        n = len(results)
        n_ok = sum(1 for r in results if r['success'])

        return {
            'results': results,
            'n_total': n,
            'n_recovered': n_ok,
            'all_corrected': n_ok == n,
            'summary': '%d/%d weight-1 errors corrected' % (n_ok, n),
        }

    # ------------------------------------------------------------------
    # Weight-2 detection
    # ------------------------------------------------------------------

    def test_weight2_detection(self) -> Dict:
        """
        Test DETECTION of weight-2 errors.

        Distance d=3: any error of weight <= 2 is detected
        (non-trivial syndrome), but only weight <= 1 is correctable.
        """
        cw = self.code.get_codewords()
        psi_0 = cw['logical_zero']
        psi_1 = cw['logical_one']
        table = self.code.get_syndrome_table()

        results = []
        n_detected = 0
        n_logical_err = 0

        for t1 in ['X', 'Y', 'Z']:
            for q1 in range(5):
                for t2 in ['X', 'Y', 'Z']:
                    for q2 in range(q1 + 1, 5):
                        E = self._two_qubit_error(t1, q1, t2, q2)
                        psi_err = E @ psi_0

                        syn = self._measure_syndrome(psi_err)
                        detected = (syn != 0)
                        if detected:
                            n_detected += 1

                        # Try weight-1 correction
                        outcome = 'undetected'
                        if detected and syn in table:
                            ct, cq = table[syn]
                            C = self._error_operator(ct, cq)
                            psi_after = C @ psi_err
                            f0 = abs(np.vdot(psi_0, psi_after)) ** 2
                            f1 = abs(np.vdot(psi_1, psi_after)) ** 2
                            if f0 > 0.99:
                                outcome = 'accidentally_fixed'
                            elif f1 > 0.99:
                                outcome = 'logical_error'
                                n_logical_err += 1
                            else:
                                outcome = 'out_of_codespace'

                        results.append({
                            'error': '%s_%d %s_%d' % (t1, q1, t2, q2),
                            'syndrome': syn,
                            'detected': detected,
                            'outcome': outcome,
                        })

        n_total = len(results)
        return {
            'n_total': n_total,
            'n_detected': n_detected,
            'detection_rate': n_detected / n_total if n_total else 0,
            'n_logical_errors': n_logical_err,
            'all_detected': n_detected == n_total,
            'results': results,
        }

    # ------------------------------------------------------------------
    # Multi-round error correction
    # ------------------------------------------------------------------

    def multi_round_correction(
        self,
        n_rounds: int = 50,
        error_rate: float = 0.10,
        seed: int = 42,
    ) -> Dict:
        """
        Simulate repeated error-correction rounds with random noise.

        Each round: with probability error_rate apply a random
        single-qubit Pauli error, then measure syndrome and correct.
        """
        rng = np.random.RandomState(seed)
        cw = self.code.get_codewords()
        table = self.code.get_syndrome_table()

        psi = cw['logical_zero'].copy()
        psi_target = cw['logical_zero'].copy()

        fidelities = [1.0]
        errors_log = []
        corrections_log = []
        syndromes_log = [0]

        for _ in range(n_rounds):
            # Random error
            if rng.random() < error_rate:
                et = rng.choice(['X', 'Y', 'Z'])
                eq = rng.randint(0, 5)
                E = self._error_operator(et, eq)
                psi = E @ psi
                errors_log.append('%s_%d' % (et, eq))
            else:
                errors_log.append('none')

            # Syndrome + correction
            syn = self._measure_syndrome(psi)
            syndromes_log.append(syn)

            if syn != 0 and syn in table:
                ct, cq = table[syn]
                C = self._error_operator(ct, cq)
                psi = C @ psi
                corrections_log.append('%s_%d' % (ct, cq))
            else:
                corrections_log.append('none')

            fidelities.append(abs(np.vdot(psi_target, psi)) ** 2)

        n_err = sum(1 for e in errors_log if e != 'none')
        n_corr = sum(1 for c in corrections_log if c != 'none')

        return {
            'n_rounds': n_rounds,
            'error_rate': error_rate,
            'fidelities': fidelities,
            'final_fidelity': fidelities[-1],
            'maintained_coherence': all(f > 0.99 for f in fidelities),
            'n_errors': n_err,
            'n_corrections': n_corr,
            'errors': errors_log,
            'corrections': corrections_log,
            'syndromes': syndromes_log,
        }

    # ------------------------------------------------------------------
    # Logical gate verification
    # ------------------------------------------------------------------

    def verify_logical_gates(self) -> Dict:
        """
        Verify X_L and Z_L:
          1. Commute with all stabilizers
          2. X_L |0>_L = |1>_L
          3. Z_L |0>_L = +|0>_L, Z_L |1>_L = -|1>_L
          4. {X_L, Z_L} = 0  (anticommutation)
        """
        cw = self.code.get_codewords()
        psi_0 = cw['logical_zero']
        psi_1 = cw['logical_one']
        XL = self.code.x_logical_matrix
        ZL = self.code.z_logical_matrix

        # Commutation
        comm_ok = True
        for g in self.code.stabilizer_matrices:
            if np.max(np.abs(XL @ g - g @ XL)) > 1e-14:
                comm_ok = False
            if np.max(np.abs(ZL @ g - g @ ZL)) > 1e-14:
                comm_ok = False

        # X_L action
        fid_xl_swap_01 = abs(np.vdot(psi_1, XL @ psi_0)) ** 2
        fid_xl_swap_10 = abs(np.vdot(psi_0, XL @ psi_1)) ** 2

        # Z_L eigenvalues
        ev_zl_0 = np.vdot(psi_0, ZL @ psi_0).real
        ev_zl_1 = np.vdot(psi_1, ZL @ psi_1).real

        # Anticommutation
        anticomm = np.max(np.abs(XL @ ZL + ZL @ XL))

        all_ok = (
            comm_ok and
            fid_xl_swap_01 > 1.0 - 1e-12 and
            fid_xl_swap_10 > 1.0 - 1e-12 and
            abs(ev_zl_0 - 1.0) < 1e-12 and
            abs(ev_zl_1 + 1.0) < 1e-12 and
            anticomm < 1e-14
        )

        return {
            'stabilizer_commutation': comm_ok,
            'XL_swaps_codewords': (fid_xl_swap_01 > 1 - 1e-12 and
                                   fid_xl_swap_10 > 1 - 1e-12),
            'ZL_eigenvalue_0L': ev_zl_0,
            'ZL_eigenvalue_1L': ev_zl_1,
            'XL_ZL_anticommute': anticomm < 1e-14,
            'all_passed': all_ok,
        }

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def print_summary(self):
        print('\n[[5,1,3]] Error Correction Summary')
        print('=' * 60)

        w1 = self.test_all_weight1()
        print('\n  Weight-1 errors: %s' % w1['summary'])

        w2 = self.test_weight2_detection()
        print('  Weight-2 detection: %d/%d (%.1f%%)' % (
            w2['n_detected'], w2['n_total'],
            100 * w2['detection_rate']))
        print('    All detected: %s' % w2['all_detected'])

        lg = self.verify_logical_gates()
        print('\n  Logical gates:')
        print('    Stabilizer commutation: %s' % lg['stabilizer_commutation'])
        print('    X_L swaps codewords:    %s' % lg['XL_swaps_codewords'])
        print('    Z_L eigenvalues: +%.0f / %.0f' % (
            lg['ZL_eigenvalue_0L'], lg['ZL_eigenvalue_1L']))
        print('    {X_L, Z_L} = 0:         %s' % lg['XL_ZL_anticommute'])
        print('    All passed:             %s' % lg['all_passed'])


# ============================================================================
#  MODULE 6:  MATHIEU GROUND STATE (C5 CONTINUUM LIMIT)
# ============================================================================

class MathieuGroundState:
    """
    Quantum simulation of the Mathieu equation from C5 continuum limit.

    From S3 (Theorem 3.1, Section 3.3):
        The tight-binding Hamiltonian on C5 in the continuum limit,
        constrained by Z5 symmetry, uniquely produces:

            -d^2 psi/d xi^2 + 2q(1 - cos xi) psi = a psi

        with xi = 5*theta and Mathieu parameter q = V0/(hbar*omega).

    The potential V(theta) = V0(1 - cos 5*theta) has:
        - 5 minima at theta = 2*pi*n/5 (pentagon vertices)
        - Small-oscillation frequency 5*omega
        - Higgs mass: m_H = 5*mu_rad = 126.7 GeV

    Implementation:
        Discretize on periodic grid of 2^n_qubits points.
        H = kinetic (3-point stencil) + potential (diagonal).
        Ground state via exact diag and VQE.
    """

    def __init__(
        self,
        n_qubits: int = 4,
        q_param: float = 1.0,
    ):
        self.n_qubits = n_qubits
        self.n_grid = 2 ** n_qubits
        self.dim = self.n_grid
        self.q = q_param

        self.xi = np.linspace(0, 2 * np.pi, self.n_grid, endpoint=False)
        self.d_xi = 2 * np.pi / self.n_grid

        self._H = self._build_hamiltonian()
        self._eigenvalues = None
        self._eigenvectors = None

    def _build_hamiltonian(self) -> np.ndarray:
        """
        Mathieu Hamiltonian on periodic grid.

        H = -d^2/dxi^2 + 2q(1 - cos xi)

        Kinetic: 3-point finite difference with periodic BCs.
        """
        N = self.n_grid
        dx = self.d_xi

        T = np.zeros((N, N), dtype=float)
        for j in range(N):
            T[j, j] = 2.0 / dx**2
            T[j, (j + 1) % N] = -1.0 / dx**2
            T[j, (j - 1) % N] = -1.0 / dx**2

        V = np.diag(2.0 * self.q * (1.0 - np.cos(self.xi)))
        return T + V

    # ------------------------------------------------------------------
    # Exact spectrum
    # ------------------------------------------------------------------

    def exact_spectrum(self, n_levels: int = 8) -> Dict:
        """Exact diagonalization with analytical Mathieu comparison."""
        if self._eigenvalues is None:
            evals, evecs = np.linalg.eigh(self._H)
            self._eigenvalues = evals.real
            self._eigenvectors = evecs

        evals = self._eigenvalues[:n_levels]

        # Analytical Mathieu characteristic values
        # Our H = -d^2/dxi^2 + 2q(1 - cos xi) = -d^2/dxi^2 - 2q cos xi + 2q
        # Standard: d^2y/dxi^2 + (a - 2q cos xi) y = 0
        # Eigenvalue relation: a_our = a_standard + 2q
        analytical = []
        try:
            for m in range(n_levels):
                if m == 0:
                    a_val = mathieu_a(0, self.q) + 2 * self.q
                elif m % 2 == 1:
                    b_idx = (m + 1) // 2
                    a_val = mathieu_b(b_idx, self.q) + 2 * self.q
                else:
                    a_idx = m // 2
                    a_val = mathieu_a(a_idx, self.q) + 2 * self.q
                analytical.append(a_val)
        except Exception:
            analytical = [None] * n_levels

        omega_osc = np.sqrt(2.0 * self.q)
        gap = evals[1] - evals[0] if len(evals) > 1 else 0.0

        return {
            'eigenvalues': evals.tolist(),
            'analytical': analytical,
            'ground_energy': float(evals[0]),
            'first_gap': gap,
            'omega_osc': omega_osc,
            'q': self.q,
            'n_grid': self.n_grid,
            'n_qubits': self.n_qubits,
        }

    # ------------------------------------------------------------------
    # VQE
    # ------------------------------------------------------------------

    def run_vqe(
        self,
        n_layers: int = 3,
        n_restarts: int = 8,
        maxiter: int = 500,
    ) -> Dict:
        """VQE ground state search with hardware-efficient ansatz."""
        n_params = self.n_qubits * 2 * n_layers + self.n_qubits

        def cost(params):
            psi = self._build_ansatz(params, n_layers)
            return np.vdot(psi, self._H @ psi).real

        best_e = np.inf
        best_p = None

        for r in range(n_restarts):
            np.random.seed(42 + r)
            p0 = np.random.uniform(-np.pi, np.pi, n_params)
            res = minimize(cost, p0, method='COBYLA',
                           options={'maxiter': maxiter, 'rhobeg': 0.5})
            if res.fun < best_e:
                best_e = res.fun
                best_p = res.x.copy()

        exact = self.exact_spectrum()

        psi_vqe = self._build_ansatz(best_p, n_layers)
        if self._eigenvectors is None:
            self.exact_spectrum()
        overlap = abs(np.vdot(self._eigenvectors[:, 0], psi_vqe)) ** 2

        return {
            'vqe_energy': best_e,
            'exact_energy': exact['ground_energy'],
            'error_abs': abs(best_e - exact['ground_energy']),
            'error_rel': (abs(best_e - exact['ground_energy']) /
                          abs(exact['ground_energy'])
                          if exact['ground_energy'] != 0 else 0),
            'overlap': overlap,
            'n_layers': n_layers,
            'n_params': n_params,
            'q': self.q,
        }

    def _build_ansatz(self, params: np.ndarray, n_layers: int) -> np.ndarray:
        """Hardware-efficient ansatz: Ry-Rz layers + CNOT ladder."""
        n = self.n_qubits
        state = np.zeros(self.dim, dtype=complex)
        state[0] = 1.0

        idx = 0
        for layer in range(n_layers):
            for q in range(n):
                state = _apply_ry(state, params[idx], q, n)
                idx += 1
            for q in range(n):
                state = _apply_rz(state, params[idx], q, n)
                idx += 1
            for q in range(n - 1):
                state = _apply_cnot(state, q, q + 1, n)
        for q in range(n):
            state = _apply_ry(state, params[idx], q, n)
            idx += 1

        return state

    # ------------------------------------------------------------------
    # Band structure
    # ------------------------------------------------------------------

    def band_structure(self, n_k: int = 101) -> Dict:
        """
        Mathieu band structure via Bloch quasi-momentum.

        Twisted BCs: psi(xi + 2pi) = exp(2pi i k) psi(xi).
        """
        N = self.n_grid
        dx = self.d_xi
        k_vals = np.linspace(0, 0.5, n_k)

        n_bands = min(6, N)
        bands = np.zeros((n_bands, n_k))

        for ki, k in enumerate(k_vals):
            T = np.zeros((N, N), dtype=complex)
            phase = np.exp(1j * 2 * np.pi * k / N)
            for j in range(N):
                T[j, j] = 2.0 / dx**2
                T[j, (j + 1) % N] = -1.0 / dx**2 * phase
                T[j, (j - 1) % N] = -1.0 / dx**2 * phase.conj()

            V = np.diag(2.0 * self.q * (1.0 - np.cos(self.xi)))
            evals = np.sort(np.linalg.eigvalsh(T + V).real)
            bands[:, ki] = evals[:n_bands]

        gaps = []
        for b in range(n_bands - 1):
            gaps.append(np.min(bands[b + 1]) - np.max(bands[b]))

        return {
            'k_values': k_vals,
            'bands': bands,
            'n_bands': n_bands,
            'gaps': gaps,
            'q': self.q,
        }

    # ------------------------------------------------------------------
    # QSD interpretation
    # ------------------------------------------------------------------

    def qsd_interpretation(self) -> Dict:
        """Map Mathieu spectrum to QSD physical quantities."""
        spec = self.exact_spectrum()
        m_H_pred = 5.0 * MU_RAD
        m_H_exp = 125.25  # GeV, PDG 2022

        return {
            'ground_energy': spec['ground_energy'],
            'first_gap': spec['first_gap'],
            'omega_osc': spec['omega_osc'],
            'higgs_mass_predicted': m_H_pred,
            'higgs_mass_experimental': m_H_exp,
            'higgs_discrepancy_pct':
                abs(m_H_pred - m_H_exp) / m_H_exp * 100,
            'potential': 'V(theta) = V0(1 - cos 5*theta)',
            'origin': 'Z5 symmetry of [[5,1,3]] stabilizer cycle (S3)',
        }

    # ------------------------------------------------------------------
    # Qiskit circuit
    # ------------------------------------------------------------------

    def vqe_circuit_qiskit(self, n_layers: int = 3) -> 'QuantumCircuit':
        if not QISKIT_AVAILABLE:
            raise RuntimeError('Qiskit not installed.')
        from qiskit.circuit import ParameterVector
        n = self.n_qubits
        n_params = n * 2 * n_layers + n
        theta = ParameterVector('t', n_params)
        qc = QuantumCircuit(n, name='VQE_Mathieu_L%d' % n_layers)
        idx = 0
        for layer in range(n_layers):
            for q in range(n):
                qc.ry(theta[idx], q); idx += 1
            for q in range(n):
                qc.rz(theta[idx], q); idx += 1
            for q in range(n - 1):
                qc.cx(q, q + 1)
        for q in range(n):
            qc.ry(theta[idx], q); idx += 1
        return qc

    def print_spectrum(self, n_levels: int = 6):
        s = self.exact_spectrum(n_levels)
        print('\n  Mathieu Spectrum (q = %.4f, N = %d)' % (
            self.q, self.n_grid))
        print('  %-6s  %-16s  %-16s  %-10s' % (
            'Level', 'Numerical', 'Analytical', '|diff|'))
        print('  ' + '-' * 56)
        for i, (en, ea) in enumerate(zip(s['eigenvalues'], s['analytical'])):
            if ea is not None:
                print('  n=%-3d  %16.10f  %16.10f  %.2e' % (
                    i, en, ea, abs(en - ea)))
            else:
                print('  n=%-3d  %16.10f  %16s' % (i, en, 'N/A'))


# ============================================================================
#  HELPER FUNCTIONS (statevector manipulation)
# ============================================================================

def _ry_mat(theta):
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)

def _rz_mat(phi):
    return np.array([
        [np.exp(-1j * phi / 2), 0],
        [0, np.exp(1j * phi / 2)]
    ], dtype=complex)

def _apply_gate(state, gate, qubit, n_qubits):
    dim = 2 ** n_qubits
    psi = state.reshape([2] * n_qubits)
    axes = list(range(n_qubits))
    axes.remove(qubit)
    axes = [qubit] + axes
    psi = np.transpose(psi, axes)
    psi = np.einsum('ij,j...->i...', gate, psi)
    inv = [0] * n_qubits
    for new_p, old_p in enumerate(axes):
        inv[old_p] = new_p
    psi = np.transpose(psi, inv)
    return psi.reshape(dim)

def _apply_ry(state, theta, qubit, n_qubits):
    return _apply_gate(state, _ry_mat(theta), qubit, n_qubits)

def _apply_rz(state, phi, qubit, n_qubits):
    return _apply_gate(state, _rz_mat(phi), qubit, n_qubits)

def _apply_cnot(state, ctrl, targ, n_qubits):
    dim = 2 ** n_qubits
    psi = state.reshape([2] * n_qubits)
    sl0 = [slice(None)] * n_qubits
    sl1 = [slice(None)] * n_qubits
    sl0[ctrl] = 0
    sl1[ctrl] = 1
    sub = psi[tuple(sl1)].copy()
    t_pos = targ if targ < ctrl else targ - 1
    i0 = [slice(None)] * sub.ndim
    i1 = [slice(None)] * sub.ndim
    i0[t_pos] = 0
    i1[t_pos] = 1
    new = np.zeros_like(sub)
    new[tuple(i0)] = sub[tuple(i1)]
    new[tuple(i1)] = sub[tuple(i0)]
    result = psi.copy()
    result[tuple(sl1)] = new
    return result.reshape(dim)


# ============================================================================
#  VISUALIZATION
# ============================================================================

def plot_trotter_evolution(result: Dict, save_path: str = None):
    """Plot correlations, energy, fidelity for Trotter evolution."""
    import matplotlib.pyplot as plt

    times = result['times']
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)

    # Correlations
    ax = axes[0]
    colors = ['#E91E63', '#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#795548']
    for idx, (ekey, corr) in enumerate(result['correlations'].items()):
        ax.plot(times, corr, color=colors[idx % 6], linewidth=0.8,
                alpha=0.8, label=ekey)
    ax.axhline(0, color='gray', linewidth=0.3)
    ax.set_ylabel(r'$\langle \mathbf{S}_i \cdot \mathbf{S}_j \rangle$')
    ax.set_title('K4 Trotter (order %d, dt=%.4f, %s)' % (
        result['trotter_order'], result['dt'], result['initial_state']))
    ax.legend(fontsize=7, ncol=3, loc='upper right')

    # Energy
    ax = axes[1]
    ax.plot(times, result['energy'], color='#2196F3', linewidth=1)
    ax.axhline(result['energy'][0], color='red', linewidth=0.5,
               linestyle='--', alpha=0.5)
    ax.set_ylabel(r'$\langle H \rangle$')
    ax.set_title('Energy (drift = %.2e)' % result['energy_drift'])

    # Fidelity
    ax = axes[2]
    ax.plot(times, result['fidelity_vs_exact'], color='#4CAF50', linewidth=1)
    ax.axhline(1.0, color='gray', linewidth=0.3, linestyle='--')
    ax.set_ylabel('Fidelity vs exact')
    ax.set_xlabel(r'Time $t$')
    ax.set_ylim(max(0, np.min(result['fidelity_vs_exact']) - 0.05), 1.02)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches='tight')
    return fig


def plot_trotter_scaling(result: Dict, save_path: str = None):
    """Plot Trotter error vs dt for both orders."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    dt = np.array(result['dt_values'])
    e1 = np.array(result['error_order1'])
    e2 = np.array(result['error_order2'])

    m1 = e1 > 1e-16
    m2 = e2 > 1e-16

    ax.loglog(dt[m1], e1[m1], 'o-', color='#E91E63', label='1st order', ms=6)
    ax.loglog(dt[m2], e2[m2], 's-', color='#2196F3', label='2nd order', ms=6)

    if np.any(m1):
        d = dt[m1]
        ax.loglog(d, 0.5 * (d / d[0])**2 * e1[m1][0],
                  '--', color='#E91E63', alpha=0.4, label=r'$\sim \sigma t^2$')
    if np.any(m2):
        d = dt[m2]
        ax.loglog(d, 0.5 * (d / d[0])**3 * e2[m2][0],
                  '--', color='#2196F3', alpha=0.4, label=r'$\sim \sigma t^3$')

    ax.set_xlabel(r'$\sigma t$')
    ax.set_ylabel('Infidelity $1 - F$')
    ax.set_title('Trotter Error Scaling (t = %.1f)' % result['t_fixed'])
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches='tight')
    return fig


def plot_multi_round(result: Dict, save_path: str = None):
    """Plot fidelity over multi-round error correction."""
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True,
                                   gridspec_kw={'height_ratios': [2, 1]})

    rounds = range(len(result['fidelities']))
    ax1.plot(list(rounds), result['fidelities'], 'o-', color='#4CAF50',
             markersize=3, linewidth=1)
    ax1.axhline(1.0, color='gray', linewidth=0.5, linestyle='--')
    ax1.set_ylabel(r'Fidelity with $|0\rangle_L$')
    ax1.set_title('[[5,1,3]] Multi-Round EC (p = %.0f%%, %d rounds)' % (
        100 * result['error_rate'], result['n_rounds']))
    ax1.set_ylim(0.95, 1.02)

    for i, (err, corr) in enumerate(zip(result['errors'], result['corrections'])):
        if err != 'none':
            ax2.plot(i + 1, 1, 'v', color='#E91E63', markersize=6)
        if corr != 'none':
            ax2.plot(i + 1, 0, '^', color='#2196F3', markersize=6)

    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(['Correction', 'Error'])
    ax2.set_xlabel('Round')

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches='tight')
    return fig


def plot_mathieu_states(m: MathieuGroundState, save_path: str = None):
    """Plot Mathieu potential, energy levels, and wavefunctions."""
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))

    xi = m.xi
    V = 2.0 * m.q * (1.0 - np.cos(xi))

    spec = m.exact_spectrum(6)
    colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', '#795548']

    # Potential + levels
    ax1.plot(xi / np.pi, V, 'k-', linewidth=2, label=r'$V(\xi)$')
    for i, E in enumerate(spec['eigenvalues'][:6]):
        ax1.axhline(E, color=colors[i], linewidth=0.8, linestyle='--',
                    alpha=0.6, label='$E_%d = %.4f$' % (i, E))
    ax1.set_xlabel(r'$\xi / \pi$')
    ax1.set_ylabel('Energy')
    ax1.set_title(r'Mathieu Potential ($q = %.3f$, $N = %d$)' % (m.q, m.n_grid))
    ax1.legend(fontsize=8, loc='upper right')

    # Wavefunctions
    if m._eigenvectors is None:
        m.exact_spectrum()
    evecs = m._eigenvectors

    for i in range(min(4, len(spec['eigenvalues']))):
        psi = evecs[:, i].real
        psi_n = psi / np.max(np.abs(psi)) * 0.3
        E = spec['eigenvalues'][i]
        ax2.plot(xi / np.pi, psi_n + E, color=colors[i],
                 linewidth=1.2, label=r'$\psi_%d$' % i)
        ax2.axhline(E, color=colors[i], linewidth=0.3, linestyle='--', alpha=0.3)

    V_sc = V * max(spec['eigenvalues'][:4]) / max(V) * 0.8
    ax2.fill_between(xi / np.pi, 0, V_sc, color='gray', alpha=0.1)
    ax2.set_xlabel(r'$\xi / \pi$')
    ax2.set_ylabel(r'$E + \psi(\xi)$')
    ax2.set_title('Lowest eigenstates')
    ax2.legend(fontsize=9)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches='tight')
    return fig


def plot_mathieu_bands(b: Dict, save_path: str = None):
    """Plot Mathieu band structure."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    k = b['k_values']
    colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', '#795548']

    for i in range(b['n_bands']):
        ax.plot(k, b['bands'][i], color=colors[i % 6], linewidth=1.5,
                label='Band %d' % i)

    for i, gap in enumerate(b['gaps'][:5]):
        if gap > 0.01:
            y_mid = (np.max(b['bands'][i]) + np.min(b['bands'][i + 1])) / 2
            ax.annotate(r'$\sigma_%d = %.3f$' % (i, gap),
                        xy=(0.25, y_mid), fontsize=8, color='gray', ha='center')

    ax.set_xlabel(r'Bloch $k$')
    ax.set_ylabel('Energy')
    ax.set_title(r'Mathieu Band Structure ($q = %.3f$)' % b['q'])
    ax.legend(fontsize=8, loc='upper left')

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches='tight')
    return fig


# ============================================================================
#  MASTER RUNNER
# ============================================================================

def run_all_additions(save_figures: bool = True) -> Dict:
    """Execute all three additional modules."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig_dir = 'figures'
    os.makedirs(fig_dir, exist_ok=True)
    results = {}

    # ==================================================================
    # Module 4: K4 Trotter
    # ==================================================================
    print('\n' + '=' * 70)
    print('  MODULE 4: K4 Trotter Time Evolution')
    print('=' * 70)

    trotter = K4TrotterEvolution(J=HB4)

    print('\n  First-order (Neel, t=10, 200 steps)...')
    r1 = trotter.evolve(10.0, 200, order=1, initial_state='neel')
    trotter.print_summary(r1)
    results['trotter_o1'] = r1

    print('\n  Second-order (Neel, t=10, 200 steps)...')
    r2 = trotter.evolve(10.0, 200, order=2, initial_state='neel')
    trotter.print_summary(r2)
    results['trotter_o2'] = r2

    print('\n  Singlet-pair initial state (order 2, t=10, 200 steps)...')
    r3 = trotter.evolve(10.0, 200, order=2, initial_state='singlet_pair')
    trotter.print_summary(r3)
    results['trotter_singlet'] = r3

    print('\n  Error scaling analysis...')
    sc = trotter.trotter_error_scaling(t_fixed=5.0)
    results['trotter_scaling'] = sc
    print('    %6s  %14s  %14s' % ('Steps', 'Order-1', 'Order-2'))
    for n, e1, e2 in zip(sc['step_counts'], sc['error_order1'], sc['error_order2']):
        print('    %6d  %14.6e  %14.6e' % (n, e1, e2))

    if save_figures:
        plot_trotter_evolution(r1, os.path.join(fig_dir, 'trotter_o1.png'))
        plot_trotter_evolution(r2, os.path.join(fig_dir, 'trotter_o2.png'))
        plot_trotter_evolution(r3, os.path.join(fig_dir, 'trotter_singlet.png'))
        plot_trotter_scaling(sc, os.path.join(fig_dir, 'trotter_scaling.png'))
        plt.close('all')

    # ==================================================================
    # Module 5: Error Correction
    # ==================================================================
    print('\n' + '=' * 70)
    print('  MODULE 5: [[5,1,3]] Full Error Correction')
    print('=' * 70)

    ec = Code513ErrorCorrection()
    ec.print_summary()

    print('\n  Multi-round (50 rounds, 10% error rate)...')
    mr = ec.multi_round_correction(n_rounds=50, error_rate=0.10)
    results['ec_multiround'] = mr
    print('    Errors injected: %d' % mr['n_errors'])
    print('    Corrections:     %d' % mr['n_corrections'])
    print('    Final fidelity:  %.15f' % mr['final_fidelity'])
    print('    Coherence kept:  %s' % mr['maintained_coherence'])

    results['ec_w1'] = ec.test_all_weight1()
    results['ec_w2'] = ec.test_weight2_detection()
    results['ec_gates'] = ec.verify_logical_gates()

    if save_figures:
        plot_multi_round(mr, os.path.join(fig_dir, 'ec_multiround.png'))
        plt.close('all')

    # ==================================================================
    # Module 6: Mathieu
    # ==================================================================
    print('\n' + '=' * 70)
    print('  MODULE 6: Mathieu Ground State (C5 continuum)')
    print('=' * 70)

    for nq in [4, 5]:
        print('\n  --- %d qubits (%d points) ---' % (nq, 2**nq))
        mth = MathieuGroundState(n_qubits=nq, q_param=1.0)
        mth.print_spectrum()

    mth4 = MathieuGroundState(n_qubits=4, q_param=1.0)

    print('\n  VQE (4 qubits, 3 layers, 8 restarts)...')
    vqe = mth4.run_vqe(n_layers=3, n_restarts=8)
    results['mathieu_vqe'] = vqe
    print('    VQE:   %.10f' % vqe['vqe_energy'])
    print('    Exact: %.10f' % vqe['exact_energy'])
    print('    Error: %.2e' % vqe['error_abs'])
    print('    Overlap: %.10f' % vqe['overlap'])

    interp = mth4.qsd_interpretation()
    results['mathieu_qsd'] = interp
    print('\n  QSD interpretation:')
    print('    %s' % interp['potential'])
    print('    m_H = 5*mu_rad = %.3f GeV (exp: %.2f, diff: %.2f%%)' % (
        interp['higgs_mass_predicted'], interp['higgs_mass_experimental'],
        interp['higgs_discrepancy_pct']))

    print('\n  Band structure...')
    bands = mth4.band_structure(101)
    results['mathieu_bands'] = bands
    for i, g in enumerate(bands['gaps'][:4]):
        print('    Gap %d-%d: %.6f' % (i, i+1, g))

    if save_figures:
        plot_mathieu_states(mth4, os.path.join(fig_dir, 'mathieu_states.png'))
        plot_mathieu_bands(bands, os.path.join(fig_dir, 'mathieu_bands.png'))
        plt.close('all')

    # ==================================================================
    # Summary
    # ==================================================================
    print('\n' + '=' * 70)
    print('  SUMMARY')
    print('=' * 70)
    print('\n  K4 Trotter:')
    print('    Order-1 drift: %.2e,  fidelity: %.10f' % (
        r1['energy_drift'], r1['final_fidelity']))
    print('    Order-2 drift: %.2e,  fidelity: %.10f' % (
        r2['energy_drift'], r2['final_fidelity']))
    print('\n  [[5,1,3]] Error Correction:')
    print('    Weight-1: %s' % results['ec_w1']['summary'])
    print('    Weight-2 detect: %.1f%%' % (
        100 * results['ec_w2']['detection_rate']))
    print('    Logical gates: %s' % (
        'PASS' if results['ec_gates']['all_passed'] else 'FAIL'))
    print('    Multi-round: %s' % mr['maintained_coherence'])
    print('\n  Mathieu:')
    print('    VQE error: %.2e' % vqe['error_abs'])
    print('    m_H = %.3f GeV' % interp['higgs_mass_predicted'])

    return results


if __name__ == '__main__':
    np.random.seed(42)
    run_all_additions(save_figures=True)
