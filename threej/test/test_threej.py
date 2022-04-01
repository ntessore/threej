import unittest

from threej import threejj


class TestThreejj(unittest.TestCase):
    values = {
        (10, 12, 3, -4):
            [0.1298626009487131, -0.009004351278571220, -0.08480610625948394,
             -0.02880207382397568, 0.05504015301860649, 0.05356728317972323,
             -0.01835419580251258, -0.05884749035199277, -0.01915305329558134,
             0.04244513283708138, 0.04607960459077556, -0.008624329328425667,
             -0.05062627027405322, -0.03008402651469377, 0.02576080347314591,
             0.05240628143444200, 0.02282939845103895, -0.03108688726372217,
             -0.06167908216213664, -0.05313229297855209, -0.02509012921599955],
        (1/2, 1/2, 1/2, -1/2):
            [0.7071067811865475, 0.4082482904638630],
        (1, 1, 1, -1):
            [0.5773502691896258, 0.4082482904638630, 0.1825741858350554],
        (5, 3, 0, 0):
            [-0.2080625946441198, 0., 0.1413506985480439, 0.,
             -0.1277380770053171, 0., 0.1517754517096559],
        (5, 5, 1, -1):
            [0.3015113445777636, 0.05504818825631803, -0.1374085837243033,
             -0.08078865345335647, 0.07884165279854435, 0.09656090991705352,
             -0.03142050359353865, -0.1036823720766748, -0.02059959850092195,
             0.09771247522185529, 0.1066130509632497],
        (5, 5, 3, -1):
            [0.1615773069067129, 0.1365577483997838, 0.,
             -0.1079583792718826, -0.09108032686966361, 0.01571025179676933,
             0.1047694586203995, 0.1118167111806716, 0.05976854619341832],
        (5/2, 7/2, 3/2, -1/2):
            [-0.1336306209562122, -0.2191252450446388, -0.1259881576697424,
             0.06579516949597690, 0.1745949755388324, 0.1303721289114050],
        (5/2, 3, 3/2, -1):
            [-0.2182178902359924, -0.2415229457698240, -0.06900655593423542,
             0.1259881576697424, 0.1880253582725887, 0.1163105262998089],
        (0, 3, 0, 1):
            [0.3779644730092272],
        (1000, 10000, 0, 0):
            [0.0009696133905311009, 0., -0.0006857554830529789, 0.,
             0.0005939989997298896, 0., -0.0005423516867788967, 0.,
             0.0005074240389997046, 0., -0.0004814801870830299, ...,
             -0.0004581525904391646, 0., 0.0004827909482784878, 0.,
             -0.0005159711642761156, 0., 0.0005650495118173705, 0.,
             -0.0006522685412570973, 0., 0.0009221723628448327],
        (10000, 10000, 0, 0):
            [0.007070891041799028, 0., -0.003535445534156109, 0.,
             0.002651584173816124, 0., -0.002209653508559803, 0.,
             0.001933446856238336, 0., -0.001740102211937807, ...,
             -0.0002216238886764027, 0., 0.0002335974848939490, 0.,
             -0.0002497106037923903, 0., 0.0002735271617315186, 0.,
             -0.0003158222192848557, 0., 0.0004466121511911233],
    }

    def assertArrayAlmostEqual(self, x, y, places=15, delta=None):
        self.assertEqual(len(x), len(y), msg='length of arrays not equal')
        for i, (a, b) in enumerate(zip(x, y)):
            self.assertAlmostEqual(a, b, places=places, delta=delta,
                                   msg=f'array element {i} not almost equal')

    def assertThreejj(self, l2, l3, m2, m3, out=None):
        l1min, thrcof = threejj(l2, l3, m2, m3, out=out)

        self.assertEqual(l1min, max(abs(l2-l3), abs(m2+m3)))

        values = self.values[l2, l3, m2, m3]

        if ... in values:
            i = values.index(...)
            a, b = values[:i], values[i+1:]
            self.assertArrayAlmostEqual(thrcof[:len(a)], a)
            self.assertArrayAlmostEqual(thrcof[len(thrcof)-len(b):], b)
        else:
            self.assertArrayAlmostEqual(thrcof, values)

    def test_integers(self):
        self.assertThreejj(10, 12, 3, -4)

    def test_half_integers(self):
        self.assertThreejj(5/2, 7/2, 3/2, -1/2)
        self.assertThreejj(5/2, 3, 3/2, -1)

    def test_l1min_is_0(self):
        self.assertThreejj(5, 5, 1, -1)

    def test_l1min_is_m1(self):
        self.assertThreejj(5, 5, 3, -1)

    def test_singlet(self):
        self.assertThreejj(0, 3, 0, 1)

    def test_doublet(self):
        self.assertThreejj(1/2, 1/2, 1/2, -1/2)

    def test_triplet(self):
        self.assertThreejj(1, 1, 1, -1)

    def test_m2_and_m3_equal_zero(self):
        self.assertThreejj(5, 3, 0, 0)

    def test_huge(self):
        self.assertThreejj(10000, 10000, 0, 0)
        self.assertThreejj(1000, 10000, 0, 0)

    def test_out(self):
        self.assertThreejj(10, 12, 3, -4, out=[0.]*100)

    def test_errors(self):
        with self.assertRaises(ValueError):
            threejj(0, 0, 1, 0)
        with self.assertRaises(ValueError):
            threejj(0, 0, 0, 1)
        with self.assertRaises(ValueError):
            threejj(1/2, 0, 0, 0)
        with self.assertRaises(ValueError):
            threejj(0, 1/2, 0, 0)
        with self.assertRaises(TypeError):
            threejj(1, 1, 0, 0, [0.])
