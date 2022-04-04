'''numba support'''

import numpy as np
from numba import types
from numba.extending import overload
from numba.core.errors import TypingError

from . import _threejj


@overload(_threejj._threejj, jit_options=dict(nogil=True, fastmath=True))
def _(l2, l3, m2, m3, out):
    for a in l2, l3, m2, m3:
        if not isinstance(a, types.Number):
            raise TypingError('parameters must be numbers')

    if not isinstance(out, types.Array) \
            or not isinstance(out.dtype, types.Float):
        raise TypingError('out must be float array')

    return _threejj._threejj


@overload(_threejj._threejj_00, jit_options=dict(nogil=True, fastmath=True))
def _(l2, l3, thrcof):
    return _threejj._threejj_00


@overload(_threejj.threejj)
def _(l2, l3, m2, m3, out=None):
    if isinstance(out, types.Optional):
        out = out.type

    if isinstance(out, types.NoneType):
        def threejj(l2, l3, m2, m3, out=None):
            l1min = max(abs(l2-l3), abs(m2+m3))
            l1max = l2+l3
            n = max(int(l1max-l1min+1.1), 0)
            return _threejj._threejj(l2, l3, m2, m3, out=np.empty(n))
    else:
        def threejj(l2, l3, m2, m3, out=None):
            return _threejj._threejj(l2, l3, m2, m3, out=out)

    return threejj


def init():
    pass
