import os

import numpy as np
import rasterio
from affine import Affine

from bw2regional.density import divide_by_area

AREAS = (
    np.array(
        [
            3077.2300079,
            3077.0019391,
            3076.5458145,
            3075.8616605,
            3074.9495164,
            3073.8094348,
            3072.4414813,
            3070.8457347,
            3069.0222870,
            3066.9712434,
            3064.6927222,
            3062.1868550,
            3059.4537865,
            3056.4936748,
            3053.3066912,
            3049.8930202,
            3046.2528597,
            3042.3864209,
            3038.2939285,
            3033.9756204,
            3029.4317480,
            3024.6625762,
            3019.6683833,
            3014.4494612,
            3009.0061153,
            3003.3386648,
            2997.4474422,
            2991.3327939,
            2984.9950800,
            2978.4346744,
            2971.6519646,
            2964.6473522,
            2957.4212526,
            2949.9740951,
            2942.3063230,
            2934.4183938,
            2926.3107788,
            2917.9839636,
            2909.4384482,
            2900.6747464,
            2891.6933866,
            2882.4949115,
            2873.0798782,
            2863.4488581,
            2853.6024374,
            2843.5412166,
            2833.2658109,
            2822.7768503,
            2812.0749792,
            2801.1608571,
            2790.0351582,
            2778.6985716,
            2767.1518013,
            2755.3955665,
            2743.4306011,
            2731.2576543,
            2718.8774905,
            2706.2908892,
            2693.4986451,
            2680.5015685,
            2667.3004848,
            2653.8962347,
            2640.2896746,
            2626.4816763,
            2612.4731271,
            2598.2649300,
            2583.8580035,
            2569.2532818,
            2554.4517149,
            2539.4542684,
            2524.2619238,
            2508.8756783,
            2493.2965451,
            2477.5255533,
            2461.5637477,
            2445.4121891,
            2429.0719545,
            2412.5441367,
            2395.8298444,
            2378.9302026,
            2361.8463521,
            2344.5794500,
            2327.1306692,
            2309.5011988,
            2291.6922441,
            2273.7050264,
            2255.5407830,
            2237.2007674,
            2218.6862492,
            2199.9985139,
            2181.1388633,
            2162.1086151,
            2142.9091030,
            2123.5416769,
            2104.0077025,
            2084.3085615,
            2064.4456516,
            2044.4203864,
            2024.2341953,
            2003.8885234,
            1983.3848318,
            1962.7245972,
            1941.9093120,
            1920.9404843,
            1899.8196375,
            1878.5483108,
            1857.1280585,
            1835.5604507,
            1813.8470724,
            1791.9895239,
            1769.9894206,
            1747.8483931,
            1725.5680867,
            1703.1501618,
            1680.5962932,
            1657.9081707,
            1635.0874985,
            1612.1359952,
            1589.0553936,
            1565.8474409,
            1542.5138984,
            1519.0565410,
            1495.4771578,
            1471.7775513,
            1447.9595378,
            1424.0249466,
            1399.9756206,
            1375.8134157,
            1351.5402005,
            1327.1578567,
            1302.6682785,
            1278.0733724,
            1253.3750574,
            1228.5752643,
            1203.6759360,
            1178.6790272,
            1153.5865040,
            1128.4003439,
            1103.1225355,
            1077.7550785,
            1052.2999830,
            1026.7592702,
            1001.1349711,
            975.42912705,
            949.64378940,
            923.78101904,
            897.84288636,
            871.83147097,
            845.74886152,
            819.59715539,
            793.37845851,
            767.09488512,
            740.74855748,
            714.34160569,
            687.87616739,
            661.35438752,
            634.77841811,
            608.15041795,
            581.47255240,
            554.74699308,
            527.97591765,
            501.16150951,
            474.30595754,
            447.41145586,
            420.48020351,
            393.51440422,
            366.51626611,
            339.48800143,
            312.43182627,
            285.34996030,
            258.24462644,
            231.11805066,
            203.97246162,
            176.81009042,
            149.63317034,
            122.44393648,
            95.244625564,
            68.037475592,
            40.824725575,
            13.608615243,
        ]
    ).reshape((-1, 1))
    * 1e6
)
FIXTURE = os.path.join(os.path.dirname(__file__), "data", "density_fixture.tiff")


def test_divide_by_area(tmpdir):
    destination = os.path.join(tmpdir, "output.tiff")
    divide_by_area(FIXTURE, destination)
    with rasterio.open(destination) as r:
        given = r.read(1)

    expected = np.zeros((180, 3))
    expected[:, 0] = 1
    expected[:, 1] = 10
    expected[:, 2] = 100
    expected /= AREAS

    assert np.allclose(given, expected[::-1, :])


def write_test_raster():
    meta = {
        "affine": Affine(0.5, 0, -90, 0, -0.5, 90),
        "count": 1,
        "crs": "EPSG:4326",
        "driver": "GTiff",
        "dtype": "float64",
        "height": 180,
        "nodata": 0.0,
        "width": 3,
    }
    array = np.zeros((180, 3))
    array[:, 0] = 1
    array[:, 1] = 10
    array[:, 2] = 100

    with rasterio.open(FIXTURE, "w", **meta) as sink:
        sink.write(array, 1)


if __name__ == "__main__":
    write_test_raster()
