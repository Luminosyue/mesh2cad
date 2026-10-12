"""Deterministically compiled Fusion 360 backend for PART_000.
Source: frozen 14-bit Compact IR v2 + semantic AST metadata.
This file is intended for execution inside a Fusion 360 Script/Add-In host.
"""
import adsk.core
import adsk.fusion
import adsk.cam
import traceback

SOURCE_IR = "14BIT_COMPACT_IR_V2"
PART_ID = "PART_000"
BITS = 14
Q_MAX = 16383
FUSION_BACKEND_READS_CANONICAL_CADQUERY = False
RE_QUANTIZATION = False
SPLINE_RESAMPLE = False
POINT_COUNT_CHANGED = False
NORMALIZATION_CHANGED = False
SECTION_ORDER_MATCH = True
FUSION_FEATURE_LEVEL_CODE = True
POSITION_RANGE = (-47.382318, 0.005937428248794482)
OTHER_RANGE = (-52.93513900000001, 0.006763439174754319)
SECTIONS_Q = [{"id":0,"plane":"XY","origin_q":6834,"periodic":true,"points_q":[[16,7211],[11,7211],[5,7211],[0,7211],[816,7152],[812,7152],[807,7152],[802,7152],[798,7152],[793,7152],[789,7152],[784,7152],[779,7152],[775,7152],[770,7152],[765,7152],[761,7152],[756,7152],[751,7152],[747,7152],[742,7152],[738,7152],[733,7152],[728,7152],[732,7149],[736,7147],[740,7144],[744,7142],[748,7139],[752,7137],[756,7134],[760,7132],[764,7132],[768,7133],[773,7134],[777,7136],[782,7137],[786,7138],[791,7139],[795,7141],[800,7142],[804,7143],[809,7144],[813,7146],[818,7147],[822,7148],[827,7149],[831,7150]],"masks":["PP","PP","PP","PP","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO"]},{"id":1,"plane":"XY","origin_q":7121,"periodic":true,"points_q":[[2853,7139],[2761,7296],[2731,7474],[2725,7656],[3219,7701],[3157,7845],[3027,7926],[2870,7929],[2711,7911],[2552,7893],[2393,7874],[2234,7856],[2078,7823],[1923,7780],[1769,7738],[1615,7695],[1461,7652],[1306,7609],[1152,7567],[998,7524],[848,7468],[701,7405],[561,7331],[462,7209],[488,7063],[599,6956],[743,6889],[897,6845],[1051,6801],[1204,6756],[1358,6712],[1514,6676],[1670,6640],[1826,6604],[1982,6568],[2138,6532],[2297,6509],[2455,6488],[2614,6467],[2774,6461],[2934,6455],[3094,6449],[3254,6442],[3412,6463],[3559,6524],[3570,6675],[3489,6812],[3407,6950]],"masks":["PP","PP","PP","PP","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO"]},{"id":2,"plane":"XY","origin_q":7407,"periodic":true,"points_q":[[6168,7205],[6096,7539],[6025,7873],[5950,8205],[5938,8304],[5761,8537],[5518,8711],[5226,8758],[4930,8714],[4634,8666],[4342,8598],[4051,8527],[3762,8451],[3475,8365],[3188,8280],[2901,8194],[2615,8104],[2332,8007],[2049,7909],[1765,7812],[1485,7706],[1207,7596],[928,7486],[657,7360],[504,7130],[714,6933],[993,6825],[1278,6733],[1563,6640],[1848,6550],[2140,6482],[2432,6414],[2723,6346],[3018,6296],[3315,6252],[3611,6209],[3907,6165],[4204,6121],[4500,6077],[4796,6034],[5093,5990],[5392,5975],[5691,5961],[5990,5960],[6282,6006],[6396,6265],[6361,6561],[6298,6853]],"masks":["PP","PP","PP","PP","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO"]},{"id":3,"plane":"XY","origin_q":7694,"periodic":true,"points_q":[[9201,7168],[9089,7610],[8981,8054],[8873,8498],[8765,8670],[8420,9060],[8220,9395],[7860,9550],[7461,9539],[7070,9454],[6680,9361],[6291,9265],[5907,9149],[5523,9034],[5139,8918],[4756,8802],[4372,8686],[3995,8549],[3621,8406],[3246,8263],[2872,8120],[2502,7966],[2138,7797],[1823,7558],[1723,7181],[1815,6796],[2172,6623],[2550,6489],[2935,6381],[3325,6287],[3717,6203],[4109,6121],[4502,6040],[4894,5959],[5287,5878],[5679,5796],[6073,5720],[6471,5670],[6868,5619],[7266,5568],[7665,5534],[8065,5507],[8465,5491],[8866,5507],[9245,5593],[9283,5975],[9169,6359],[9034,6736]],"masks":["PP","PP","PP","PP","PO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO"]},{"id":4,"plane":"XY","origin_q":7980,"periodic":true,"points_q":[[12097,8113],[11992,8574],[11881,9034],[11770,9493],[11657,9558],[10882,9934],[10564,10178],[10158,10262],[9743,10272],[9332,10215],[8927,10127],[8528,10013],[8131,9890],[7735,9767],[7338,9643],[6945,9509],[6553,9373],[6160,9238],[5768,9103],[5380,8955],[5000,8787],[4625,8611],[4414,8282],[4398,7872],[4413,7461],[4478,7051],[4542,6650],[4872,6408],[5184,6150],[5559,5975],[5958,5857],[6356,5739],[6762,5655],[7169,5573],[7576,5491],[7987,5430],[8399,5378],[8810,5325],[9224,5289],[9638,5268],[10050,5299],[10435,5450],[10714,5757],[10991,6066],[11238,6400],[11485,6733],[11588,7126],[11517,7535]],"masks":["PP","PP","PP","PP","PO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO"]},{"id":5,"plane":"XY","origin_q":8267,"periodic":true,"points_q":[[14817,9061],[14958,9476],[14749,9884],[14506,10272],[13273,10103],[12884,10205],[12490,10277],[12090,10316],[11689,10339],[11288,10361],[10886,10384],[10485,10394],[10083,10394],[9686,10340],[9290,10271],[8905,10154],[8525,10025],[8152,9877],[7778,9730],[7421,9546],[7093,9318],[6961,8966],[6980,8569],[7009,8171],[7076,7774],[7169,7384],[7324,7017],[7549,6685],[7706,6316],[7763,5920],[8055,5661],[8428,5518],[8820,5428],[9214,5356],[9614,5310],[10014,5310],[10399,5400],[10709,5654],[11001,5930],[11294,6206],[11586,6481],[11875,6761],[12157,7047],[12439,7333],[12721,7619],[13024,7883],[13314,8159],[13573,8466]],"masks":["PP","PP","PP","PP","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO"]},{"id":6,"plane":"XY","origin_q":8553,"periodic":true,"points_q":[[15841,9760],[16110,10037],[16324,10352],[16115,10646],[14642,10246],[14304,10275],[13966,10295],[13627,10316],[13289,10335],[12950,10348],[12611,10362],[12272,10375],[11933,10383],[11594,10379],[11255,10375],[10916,10370],[10578,10354],[10241,10315],[9907,10262],[9615,10098],[9575,9767],[9561,9430],[9723,9146],[9758,8814],[9727,8479],[9890,8185],[9973,7858],[10030,7523],[10102,7192],[10196,6867],[10290,6541],[10418,6227],[10582,5945],[10888,6066],[11166,6260],[11442,6457],[11697,6680],[11953,6902],[12209,7125],[12465,7347],[12721,7570],[12986,7780],[13256,7985],[13501,8219],[13747,8453],[13992,8687],[14237,8921],[14482,9155]],"masks":["PP","PP","PP","PP","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO"]},{"id":7,"plane":"XY","origin_q":8840,"periodic":true,"points_q":[[16204,10095],[16330,10255],[16383,10447],[16283,10625],[14971,10250],[14793,10277],[14614,10290],[14435,10288],[14255,10285],[14075,10283],[13895,10281],[13716,10279],[13536,10277],[13356,10275],[13176,10273],[12997,10258],[12818,10244],[12640,10218],[12463,10186],[12304,10115],[12217,9964],[12156,9795],[12096,9626],[12064,9449],[12050,9270],[12061,9094],[12153,8939],[12244,8784],[12336,8630],[12430,8477],[12540,8335],[12652,8194],[12783,8071],[12947,8015],[13115,8073],[13261,8176],[13399,8291],[13538,8405],[13677,8520],[13815,8635],[13954,8749],[14092,8864],[14231,8978],[14369,9093],[14508,9207],[14646,9322],[14785,9437],[14916,9560]],"masks":["PP","PP","PP","PP","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO"]},{"id":8,"plane":"XY","origin_q":9126,"periodic":true,"points_q":[[16023,10341],[16024,10344],[16026,10348],[16027,10352],[14892,9912],[14893,9915],[14890,9914],[14887,9913],[14883,9912],[14880,9912],[14877,9911],[14873,9910],[14870,9909],[14866,9909],[14863,9908],[14860,9907],[14856,9906],[14853,9905],[14851,9903],[14850,9900],[14849,9896],[14848,9893],[14847,9890],[14847,9886],[14846,9883],[14845,9880],[14844,9876],[14843,9873],[14842,9870],[14841,9866],[14840,9863],[14842,9863],[14845,9865],[14847,9867],[14850,9869],[14853,9871],[14856,9872],[14859,9874],[14862,9876],[14865,9878],[14868,9880],[14870,9882],[14873,9884],[14876,9886],[14879,9888],[14882,9890],[14884,9892],[14885,9896]],"masks":["PP","PP","PP","PP","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO","OO"]}]
TRANSFORMS_Q = [{"op":"located","q":[7980,7980,7980,7980,8149,7980,8149,7980,7980],"classes":["P","P","P","P","P","P","P","P","P"]},{"op":"translate","q":[7990,8045,8453,8145],"classes":["P","P","P","P"]}]

def _dequantize(q, cls):
    offset, scale = POSITION_RANGE if cls == "P" else OTHER_RANGE
    return offset + scale * q

def _section_points(section):
    return [adsk.core.Point3D.create(_dequantize(qx, mask[0]), _dequantize(qy, mask[1]), 0.0)
            for (qx, qy), mask in zip(section["points_q"], section["masks"])]

def _vector(values):
    return adsk.core.Vector3D.create(values[0], values[1], values[2])

def _point(values):
    return adsk.core.Point3D.create(values[0], values[1], values[2])

def _cross(a, b):
    return adsk.core.Vector3D.create(a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x)

def _transform_values(entry):
    return [_dequantize(q, cls) for q, cls in zip(entry["q"], entry["classes"])]

def _build_final_transform():
    located = _transform_values(next(t for t in TRANSFORMS_Q if t["op"] == "located"))
    moved = _transform_values(next(t for t in TRANSFORMS_Q if t["op"] == "translate"))
    origin = [located[i] for i in range(3)]
    x_dir = [located[i] for i in range(3, 6)]
    normal = [located[i] for i in range(6, 9)]
    scale = moved[3]
    translation = moved[0:3]
    origin = [origin[i] * scale + translation[i] for i in range(3)]
    x_dir = [v * scale for v in x_dir]
    normal = [v * scale for v in normal]
    x_vec = _vector(x_dir)
    n_vec = _vector(normal)
    y_vec = _cross(n_vec, x_vec)
    matrix = adsk.core.Matrix3D.create()
    matrix.setWithCoordinateSystem(_point(origin), x_vec, y_vec, n_vec)
    return matrix

def _new_offset_plane(root, z):
    plane_input = root.constructionPlanes.createInput()
    plane_input.setByOffset(root.xYConstructionPlane, adsk.core.ValueInput.createByReal(z))
    return root.constructionPlanes.add(plane_input)

def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if design is None:
            app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            design = adsk.fusion.Design.cast(app.activeProduct)
        root = design.rootComponent
        sketches = []
        profiles = adsk.core.ObjectCollection.create()
        for section in SECTIONS_Q:
            z = _dequantize(section["origin_q"], "P")
            sketch = root.sketches.add(_new_offset_plane(root, z))
            sketch.name = f"{PART_ID}_SEC_{section['id']:03d}"
            points = adsk.core.ObjectCollection.create()
            for point in _section_points(section):
                points.add(point)
            fitted = sketch.sketchCurves.sketchFittedSplines.add(points)
            fitted.isClosed = bool(section["periodic"])
            if sketch.profiles.count == 0:
                raise RuntimeError("closed spline did not produce a profile")
            profiles.add(sketch.profiles.item(0))
            sketches.append(sketch)
        loft_input = root.features.loftFeatures.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        for index in range(profiles.count):
            loft_input.loftSections.add(profiles.item(index))
        loft_input.isSolid = True
        loft = root.features.loftFeatures.add(loft_input)
        loft.name = f"{PART_ID}_LOFT_000"
        body = loft.bodies.item(0)
        body.name = f"{PART_ID}_BODY"
        body.transformBy(_build_final_transform())
        app.activeViewport.fit()
    except Exception:
        if ui:
            ui.messageBox(traceback.format_exc())
