'''
******************************
**threej** – Wigner 3j symbols
******************************


Support for numba
=================


Origin
======

The :func:`~threejj` and :func:`~threejm` functions are Python implementations
of the ``DRC3JJ`` and ``DRC3JM`` routines in the `SLATEC`__ library, written by
R. G. Gordon & K. Schulten.

__ https://www.netlib.org/slatec/


Reference
=========

``threejj``
-----------

.. autofunction:: threejj


``threejm``
-----------

.. autofunction:: threejm

'''

__version__ = '2022.4.4dev'

__all__ = [
    'threejj',
    'threejm',
]

from ._threejj import threejj


def threejm():
    raise NotImplementedError
