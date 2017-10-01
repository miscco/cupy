import unittest

import mock
import numpy

import cupy
from cupy import testing


@testing.parameterize(*testing.product({
    'dtype': [numpy.float32, numpy.float64],
    'format': ['csr', 'csc', 'coo'],
    'm': [3],
    'n': [None, 3, 2],
    'k': [0, 1],
}))
@testing.with_requires('scipy')
class TestEye(unittest.TestCase):

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_eye(self, xp, sp):
        x = sp.eye(
            self.m, n=self.n, k=self.k, dtype=self.dtype, format=self.format)
        self.assertIsInstance(x, sp.spmatrix)
        self.assertEqual(x.format, self.format)
        return x.toarray()


@testing.parameterize(*testing.product({
    'dtype': [numpy.float32, numpy.float64],
    'format': ['csr', 'csc', 'coo'],
}))
@testing.with_requires('scipy')
class TestIdentity(unittest.TestCase):

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_eye(self, xp, sp):
        x = sp.identity(3, dtype=self.dtype, format=self.format)
        self.assertIsInstance(x, sp.spmatrix)
        self.assertEqual(x.format, self.format)
        return x.toarray()


@testing.parameterize(*testing.product({
    'dtype': [numpy.float32, numpy.float64],
}))
@testing.with_requires('scipy')
class TestSpdiags(unittest.TestCase):

    @testing.numpy_cupy_allclose(sp_name='sp')
    def test_spdiags(self, xp, sp):
        data = xp.arange(12, dtype=self.dtype).reshape(3, 4)
        diags = xp.array([0, -1, 2], dtype='i')
        x = sp.spdiags(data, diags, 3, 4)
        return x.toarray()


@testing.parameterize(*testing.product({
    'dtype': [numpy.float32, numpy.float64],
    'format': ['csr', 'csc', 'coo'],
}))
class TestRandom(unittest.TestCase):

    def test_random(self):
        x = cupy.sparse.random(
            3, 4, density=0.1,
            format=self.format, dtype=self.dtype)
        self.assertEqual(x.shape, (3, 4))
        self.assertEqual(x.dtype, self.dtype)
        self.assertEqual(x.format, self.format)

    def test_random_with_seed(self):
        x = cupy.sparse.random(
            3, 4, density=0.1,
            format=self.format, dtype=self.dtype,
            random_state=1)
        self.assertEqual(x.shape, (3, 4))
        self.assertEqual(x.dtype, self.dtype)
        self.assertEqual(x.format, self.format)

        y = cupy.sparse.random(
            3, 4, density=0.1,
            format=self.format, dtype=self.dtype,
            random_state=1)

        self.assertTrue((x.toarray() == y.toarray()).all())

    def test_random_with_state(self):
        state1 = cupy.random.RandomState(1)
        x = cupy.sparse.random(
            3, 4, density=0.1,
            format=self.format, dtype=self.dtype,
            random_state=state1)
        self.assertEqual(x.shape, (3, 4))
        self.assertEqual(x.dtype, self.dtype)
        self.assertEqual(x.format, self.format)

        state2 = cupy.random.RandomState(1)
        y = cupy.sparse.random(
            3, 4, density=0.1,
            format=self.format, dtype=self.dtype,
            random_state=state2)

        self.assertTrue((x.toarray() == y.toarray()).all())

    def test_random_with_data_rvs(self):
        data_rvs = mock.MagicMock(side_effect=cupy.zeros)
        x = cupy.sparse.random(
            3, 4, density=0.1, data_rvs=data_rvs,
            format=self.format, dtype=self.dtype)
        self.assertEqual(x.shape, (3, 4))
        self.assertEqual(x.dtype, self.dtype)
        self.assertEqual(x.format, self.format)

        self.assertEqual(data_rvs.call_count, 1)
        # Note that its value is generated randomly
        self.assertIsInstance(data_rvs.call_args[0][0], int)


@testing.with_requires('scipy')
class TestRandomInvalidArgument(unittest.TestCase):

    @testing.numpy_cupy_raises(sp_name='sp', accept_error=ValueError)
    def test_too_small_density(self, xp, sp):
        sp.random(3, 4, density=-0.1)

    @testing.numpy_cupy_raises(sp_name='sp', accept_error=ValueError)
    def test_too_large_density(self, xp, sp):
        sp.random(3, 4, density=1.1)

    @testing.numpy_cupy_raises(sp_name='sp', accept_error=NotImplementedError)
    def test_invalid_dtype(self, xp, sp):
        sp.random(3, 4, dtype='i')
