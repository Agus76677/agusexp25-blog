"""Independent checks for the KHNTT reading note (Python 3, standard library only).

Run: python verification.py
Checks the note's algebra using direct evaluation/interpolation and schoolbook
negacyclic multiplication. This is NOT an RTL simulation or FPGA reproduction.
"""

import json
from itertools import combinations
from random import Random


def schoolbook(a, b, q):
    n = len(a)
    c = [0] * n
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            k = i + j
            c[k % n] += ai * bj * (1 if k < n else -1)
    return [ci % q for ci in c]


def roots(m, q):
    assert (q - 1) % (2 * m) == 0
    # m is a power of two, so psi**m == -1 establishes order 2*m.
    for base in range(2, q):
        psi = pow(base, (q - 1) // (2 * m), q)
        if pow(psi, m, q) == q - 1:
            return [pow(psi, 2 * j + 1, q) for j in range(m)]
    raise AssertionError('No primitive root found')


def forward(a, points, q):
    values = []
    for point in points:
        value = 0
        for coefficient in reversed(a):
            value = (value * point + coefficient) % q
        values.append(value)
    return values


def inverse(values, points, q):
    coefficients = [0] * len(values)
    for value, point in zip(values, points):
        power = 1
        inv_point = pow(point, q - 2, q)
        for i in range(len(values)):
            coefficients[i] += value * power
            power = power * inv_point % q
    inv_m = pow(len(values), q - 2, q)
    return [c * inv_m % q for c in coefficients]


def khntt_identity(a, b, q):
    n = len(a)
    m = n // 4
    points = roots(m, q)  # Also NTT(z), where z is the subring variable.
    aa = [forward(a[j::4], points, q) for j in range(4)]
    bb = [forward(b[j::4], points, q) for j in range(4)]
    hh = [[] for _ in range(4)]
    for i, z in enumerate(points):
        d = [aa[j][i] * bb[j][i] % q for j in range(4)]
        t = {(j, k): ((aa[j][i] + aa[k][i]) * (bb[j][i] + bb[k][i]) - d[j] - d[k]) % q for j, k in combinations(range(4), 2)}
        hh[0].append((d[0] + z * (t[1, 3] + d[2])) % q)
        hh[1].append((t[0, 1] + z * t[2, 3]) % q)
        hh[2].append((t[0, 2] + d[1] + z * d[3]) % q)
        hh[3].append((t[0, 3] + t[1, 2]) % q)
    result = [0] * n
    for j, values in enumerate(hh):
        result[j::4] = inverse(values, points, q)
    return result


def main():
    rng = Random(20261007)
    checked = []
    for n, q in [(16, 97), (64, 3329), (256, 3329), (256, 8380417), (1024, 12289)]:
        random_a = [rng.randrange(q) for _ in range(n)]
        random_b = [rng.randrange(q) for _ in range(n)]
        unit = [1] + [0] * (n - 1)
        top = [0] * (n - 1) + [1]
        cases = [([0] * n, random_b), (unit, random_a), ([q - 1] * n, [q - 1] * n), (top, top), (random_a, random_b)]
        for a, b in cases:
            assert khntt_identity(a, b, q) == schoolbook(a, b, q), (n, q)
        checked.append({'n': n, 'q': q, 'cases_passed': len(cases)})

    counts = []
    for n, log4n in [(256, 4), (1024, 5)]:
        baseline = 3 * n * log4n + n
        khntt = 3 * n * log4n + n // 4
        by_alpha = {a: 3 * n * log4n + 3 * n // 2 + 4**a * n // 2 - n // 4**a - 3 * n * a for a in range(log4n + 1)}
        assert min(by_alpha, key=by_alpha.get) == 1
        assert by_alpha[1] == khntt
        counts.append({'n': n, 'baseline_modmul': baseline, 'khntt_modmul': khntt, 'reduction_pct': (baseline - khntt) / baseline * 100})

    result = {
        'scope': 'Independent algebra and arithmetic only; no RTL or place-and-route reproduction',
        'seed': 20261007,
        'identity_checks': checked,
        'operation_counts': counts,
        'schedule_wait_reduction_pct': (76 - 39) / 76 * 100,
        'schedule_total_cycle_reduction_pct': (332 - 295) / 332 * 100,
        'ctc_a7_4bu_atp_recomputed': (3104 + 100 * 32 + 300 * 16) * 0.90 / 1000,
        'ctc_a7_8bu_atp_recomputed': (6456 + 100 * 64 + 300 * 28) * 0.78 / 1000,
        'ctc_a7_4_to_8_bu_speedup': 0.90 / 0.78,
        'rtc_1024_tp_mbit_s': 1024 * 14 / 1.75,
        'rtc_1024_tp_decimal_MB_s': 1024 * 14 / 1.75 / 8,
        'kyber_barrett_u_floor': (2**24) // 3329,
        'kyber_u_reported': 5040,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
