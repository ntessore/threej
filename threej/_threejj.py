'''threejj implementation'''

from math import sqrt, fabs, copysign
from sys import float_info

# constants
EPS = .01

# HUGE is the square root of one twentieth of the largest floating
# point number, approximately.
HUGE = sqrt(float_info.max/20)
SRHUGE = sqrt(HUGE)
TINY = 1/HUGE
SRTINY = 1/SRHUGE


def _threejj(l2, l3, m2, m3, out):
    def norm(l2, l3, m2, m3, sumuni, thrcof):
        # Normalize 3j coefficients
        cnorm = 1 / sqrt(sumuni)

        # Sign convention for last 3j coefficient determines overall phase
        sign1 = copysign(1, thrcof[-1])
        sign2 = (-1)**int(fabs(l2+m2-l3+m3)+EPS)
        if sign1*sign2 < 0:
            cnorm = -cnorm

        if fabs(cnorm) < 1:
            thresh = TINY / fabs(cnorm)
            for n in range(len(thrcof)):
                if fabs(thrcof[n]) < thresh:
                    thrcof[n] = 0
                else:
                    thrcof[n] = cnorm * thrcof[n]
        else:
            for n in range(len(thrcof)):
                thrcof[n] = cnorm * thrcof[n]

    # cast parameters to float (for numba typing)
    l2, l3, m2, m3 = float(l2), float(l3), float(m2), float(m3)

    m1 = - m2 - m3

    # Check error condition 1.
    if l2-fabs(m2)+EPS < 0 or l3-fabs(m3)+EPS < 0:
        raise ValueError('either l2 < abs(m2) or l3 < abs(m3)')

    # Check error condition 2.
    if (l2+fabs(m2)+EPS) % 1 >= EPS+EPS or (l3+fabs(m3)+EPS) % 1 >= EPS+EPS:
        raise ValueError('either l2 + abs(m2) or l3 + abs(m3) non-integer')

    # Limits for l1
    l1min = max(fabs(l2 - l3), fabs(m1))
    l1max = l2 + l3

    # Check error condition 3.
    if (l1max-l1min+EPS) % 1 >= EPS+EPS:
        raise ValueError('l1max - l1min not an integer')

    # Check error condition 4.
    if l1min >= l1max+EPS:
        raise ValueError('l1max less than l1min')

    # Number of coefficients to compute.
    nfin = int(l1max-l1min+1+EPS)

    # Check error condition 5.
    if len(out) < nfin:
        raise TypeError('result array for 3j coefficients too small')

    # Use only nfin elements for output
    thrcof = out[:nfin]

    # Check whether l1 can take only one value, ie. l1min = l1max.
    if l1min >= l1max - EPS:
        thrcof[0] = (-1)**int(fabs(l2+m2-l3+m3)+EPS)/sqrt(l1min+l2+l3+1)
        return l1min, thrcof

    # Specialisations
    if m2 == m3 == 0.:
        return _threejj_00(l2, l3, thrcof)

    # Starting forward recursion from l1min
    l1 = l1min
    newfac = 0.
    c1 = 0.

    # Set first unnormalized 3j coefficient
    thrcof[0] = SRTINY
    sum1 = (l1+l1+1) * TINY

    n, nfor = 0, nfin-1
    while True:
        n += 1
        l1 += 1.

        c1old = fabs(c1)
        oldfac = newfac
        a1 = (l1+l2+l3+1) * (l1-l2+l3) * (l1+l2-l3) * (-l1+l2+l3+1)
        a2 = (l1+m1) * (l1-m1)
        newfac = sqrt(a1*a2)

        # If l1 = 1, (l1-1) has to be factored out of dv, hence
        if l1 < 1+EPS:
            c1 = - (l1+l1-1) * l1 * (m3-m2) / newfac
        else:
            dv = - l2*(l2+1) * m1 + l3*(l3+1) * m1 + l1*(l1-1) * (m3-m2)
            denom = (l1-1) * newfac
            c1 = - (l1+l1-1) * dv / denom

        # If l1 = l1min + 1, the third term in the recursion equation vanishes
        if n == 1:
            x = SRTINY * c1
            thrcof[n] = x
            sum1 += (l1+l1+1) * (x*x)
            if n == nfor:
                break
        else:
            c2 = - l1 * oldfac / denom

            # Recursion to the next 3j coefficient x
            x = c1 * thrcof[n-1] + c2 * thrcof[n-2]
            thrcof[n] = x
            sumfor = sum1
            sum1 += (l1+l1+1) * (x*x)
            if n == nfor:
                break

            # See if last unnormalized 3j coefficient exceeds SRHUGE
            if fabs(x) > SRHUGE:
                # This is reached if last 3j coefficient larger than SRHUGE,
                # so that the recursion series thrcof[0], ... , thrcof[n]
                # has to be rescaled to prevent overflow
                for j in range(n+1):
                    if fabs(thrcof[j]) < SRTINY:
                        thrcof[j] = 0
                    else:
                        thrcof[j] /= SRHUGE
                sumfor /= HUGE
                sum1 /= HUGE

            # As long as abs(c1) is decreasing, the recursion proceeds towards
            # increasing 3j values and, hence, is numerically stable.  Once
            # an increase of abs(c1) is detected, the recursion direction is
            # reversed.
            if fabs(c1) >= c1old:
                break

    # No backward recursion if only two 3j coefficients are computed.
    if nfin == 2:
        norm(l2, l3, m2, m3, sum1, thrcof)
        return l1min, thrcof

    # Keep three 3j coefficients for comparison with backward recursion.
    x1, x2, x3 = x, thrcof[n-1], thrcof[n-2]
    nbac = nfor - n + 3

    # Starting backward recursion from l1max taking nbac steps, so that forward
    # and backward recursion overlap at three points.
    l1 = l1max + 2

    # Set last unnormalized 3j coefficient
    thrcof[-1] = SRTINY
    sum2 = TINY * (l1max+l1max+1)

    n = 1
    while True:
        n += 1
        l1 -= 1.

        oldfac = newfac
        a1s = (l1+l2+l3)*(l1-l2+l3-1)*(l1+l2-l3-1)*(-l1+l2+l3+2)
        a2s = (l1+m1-1) * (l1-m1-1)
        newfac = sqrt(a1s*a2s)

        dv = - l2*(l2+1) * m1 + l3*(l3+1) * m1 + l1*(l1-1) * (m3-m2)

        denom = l1 * newfac
        c1 = - (l1+l1-1) * dv / denom

        # If l1 = l1max+1, the third term in the recursion formula vanishes
        if n == 2:
            thrcof[-n] = SRTINY * c1
            sumbac = sum2
            sum2 = sum2 + TINY * (l1+l1-3) * (c1*c1)
        else:
            c2 = - (l1 - 1) * oldfac / denom

            # Recursion to the next 3j coefficient Y
            y = c1 * thrcof[-n+1] + c2 * thrcof[-n+2]

            if n == nbac:
                break

            thrcof[-n] = y
            sumbac = sum2
            sum2 = sum2 + (l1+l1-3) * (y*y)

            # See if last unnormalized 3j coefficient exceeds SRHUGE
            if fabs(y) > SRHUGE:
                # This is reached if last 3j coefficient larger than SRHUGE,
                # so that the recursion series thrcof[-1], ... , thrcof[-n]
                # has to be rescaled to prevent overflow
                for j in range(1, n+1):
                    if fabs(thrcof[-j]) < SRTINY:
                        thrcof[-j] = 0
                    else:
                        thrcof[-j] /= SRHUGE
                sumbac /= HUGE
                sum2 /= HUGE

    # The forward recursion 3j coefficients x1, x2, x3 are to be matched
    # with the corresponding backward recursion values y1, y2, y3.
    y3, y2, y1 = y, thrcof[-nbac+1], thrcof[-nbac+2]

    # Determine now ratio such that yi = ratio * xi  (i=1,2,3) holds
    # with minimal error.
    ratio = (x1*y1 + x2*y2 + x3*y3)/(x1*x1 + x2*x2 + x3*x3)
    nlim = nfin - nbac + 1

    if fabs(ratio) >= 1:
        for n in range(nlim):
            thrcof[n] *= ratio
        sumuni = ratio * ratio * sumfor + sumbac
    else:
        ratio = 1 / ratio
        for n in range(nlim, nfin):
            thrcof[n] *= ratio
        sumuni = sumfor + ratio*ratio*sumbac

    norm(l2, l3, m2, m3, sumuni, thrcof)
    return l1min, thrcof


def _threejj_00(l2, l3, thrcof):
    '''_threejj(..., m2=0, m3=0, ...)'''

    # cast parameters to float (for numba typing)
    l2, l3 = float(l2), float(l3)

    # Limits for l1
    l1min = fabs(l2 - l3)
    l1max = l2 + l3

    # Number of coefficients to compute.
    nfin = int(l1max-l1min+1+EPS)

    # Starting backward recursion from l1max.
    l1 = l1max + 2

    # Set last unnormalized 3j coefficient
    thrcof[-1] = SRTINY
    sum2 = TINY * (l1max+l1max+1)

    for n in range(3, nfin+1, 2):
        l1 -= 1.
        oldfac = sqrt((l1+l2+l3)*(l1-l2+l3-1)*(l1+l2-l3-1)*(-l1+l2+l3+2))
        l1 -= 1.
        newfac = sqrt((l1+l2+l3)*(l1-l2+l3-1)*(l1+l2-l3-1)*(-l1+l2+l3+2))

        # Recursion to the next 3j coefficient Y
        y = -oldfac/newfac * thrcof[-n+2]
        thrcof[-n+1] = 0.
        thrcof[-n] = y
        sum2 += (l1+l1-3) * (y*y)

        # See if last unnormalized 3j coefficient exceeds SRHUGE
        if fabs(y) > SRHUGE:
            # This is reached if last 3j coefficient larger than SRHUGE,
            # so that the recursion series thrcof[-1], ... , thrcof[-n]
            # has to be rescaled to prevent overflow
            for j in range(1, n+1):
                if fabs(thrcof[-j]) < SRTINY:
                    thrcof[-j] = 0
                else:
                    thrcof[-j] /= SRHUGE
            sum2 /= HUGE

    # Normalize 3j coefficients
    cnorm = 1 / sqrt(sum2)

    # Sign convention for last 3j coefficient determines overall phase
    sign1 = copysign(1, thrcof[-1])
    sign2 = (-1)**int(fabs(l2-l3)+EPS)
    if sign1*sign2 < 0:
        cnorm = -cnorm

    if fabs(cnorm) < 1:
        thresh = TINY / fabs(cnorm)
        for n in range(nfin):
            if fabs(thrcof[n]) < thresh:
                thrcof[n] = 0
            else:
                thrcof[n] = cnorm * thrcof[n]
    else:
        for n in range(nfin):
            thrcof[n] = cnorm * thrcof[n]

    return l1min, thrcof


def threejj(l2, l3, m2, m3, out=None):
    r'''Evaluate the Wigner 3j symbol

    .. code-block:: text

        f(l1) = ???  l1    l2  l3 ???
                ???-m2-m3  m2  m3 ???

    for all allowed values of ``l1``, the other parameters being held fixed.

    Parameters
    ----------
    l2, l3, m2, m3 : float
        Parameters in 3j symbol.
    out : array_like, optional
        Output array for coefficients.  Must have space for ``l1max-l1min+1``
        elements.  If ``None``, a new array is created.

    Returns
    -------
    l1min : float
        Smallest allowable ``l1`` in 3j symbol.
    thrcof : (l1max-l1min+1,) array_like
        Set of 3j coefficients for all allowed values of ``l1``.

    Notes
    -----
    The subroutine generates ``f(l1min)``, ``f(l1min+1)``, ...  where ``l1min``
    is defined above.  The sequence ``f(l1)`` is generated by a three-term
    recurrence algorithm with scaling to control overflow.  Both backward and
    forward recurrence are used to maintain numerical stability.  The two
    recurrence sequences are matched at an interior point and are normalized
    from the unitary property of 3j coefficients and Wigner's phase convention.
    The algorithm is suited to applications in which large quantum numbers
    arise.

    Although conventionally the parameters of the vector addition coefficients
    satisfy certain restrictions, such as being integers or integers plus 1/2,
    the restrictions imposed on input to this subroutine are somewhat weaker.
    See, for example, Section 27.9 of Abramowitz and Stegun or Appendix C of
    Volume II of A. Messiah.  The restrictions imposed by this subroutine are

    1. ``l2 >= abs(m2)`` and ``l3 >= abs(m3)``;
    2. ``l2+abs(m2)`` and ``l3+abs(m3)`` must be integers;
    3. ``l1max-l1min`` must be a non-negative integer, where ``l1max=l2+l3``
       and ``l1min=max(abs(l2-l3), abs(m2+m3))``.

    If the conventional restrictions are satisfied, then these
    restrictions are met.  However, the user should be cautious in using input
    parameters that do not satisfy the conventional restrictions.  For example,
    the the subroutine produces values ``threejj(2.5, 5.8, 1.5, -1.2)`` for
    ``l1 = 3.3, 4.3, ..., 8.3`` but none of the symmetry properties of the 3j
    symbol are satisfied.

    References
    ----------
    .. [1] Abramowitz, M., and Stegun, I. A., Eds., Handbook of Mathematical
       Functions with Formulas, Graphs and Mathematical Tables, NBS Applied
       Mathematics Series 55, June 1964 and subsequent printings.
    .. [2] Messiah, Albert., Quantum Mechanics, Volume II, North-Holland
       Publishing Company, 1963.
    .. [3] Schulten, Klaus and Gordon, Roy G., Exact recursive evaluation of 3j
       and 6j coefficients for quantum-mechanical coupling of angular momenta,
       J Math Phys, v 16, no. 10, October 1975, pp. 1961-1970.
    .. [4] Schulten, Klaus and Gordon, Roy G., Semiclassical approximations to
       3j and 6j coefficients for quantum-mechanical coupling of angular
       momenta, J Math Phys, v 16, no. 10, October 1975, pp. 1971-1988.
    .. [5] Schulten, Klaus and Gordon, Roy G., Recursive evaluation of 3j and
       6j coefficients, Computer Phys Comm, v 11, 1976, pp. 269-278.

    Examples
    --------
    >>> from threej import threejj
    >>> l1min, thrcof = threejj(3, 1, 1, -1)
    >>> l1min
    2.0
    >>> thrcof
    [0.239045..., 0.267261..., 0.154303...]

    Half-integer arguments are fully supported.

    >>> l1min, thrcof = threej.threejj(5/2, 3/2, 1/2, -1/2)
    >>> l1min
    1.0
    >>> thrcof
    [0.316227..., 0.119522..., -0.169030..., -0.218217...]

    '''

    if out is None:
        l1min = max(abs(l2-l3), abs(m2+m3))
        l1max = l2+l3
        n = max(int(l1max-l1min+1+EPS), 0)
        out = [0.]*n
    return _threejj(l2, l3, m2, m3, out)
