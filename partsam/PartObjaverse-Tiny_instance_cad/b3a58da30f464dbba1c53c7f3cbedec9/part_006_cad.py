"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b3a58da30f464dbba1c53c7f3cbedec9/part_006.stl', 'relative_path': 'b3a58da30f464dbba1c53c7f3cbedec9/part_006.stl', 'source_sha256': '4b95160a6d403676cf846ba5593c6f887a30712f28da0fcc68ef22c356309aea', 'input_faces': 241, 'input_vertices': 152, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09009339660406113, 0.17654620110988617, -0.3201002776622772], [0.18142752349376678, 0.3570179343223572, -0.06686864048242569]]}
GEOMETRY_BASE85 = 'c$}q~3s4p36~|Wu1x2L^L?t2@UkDO>qbPw@11h2-f`X!4<e?w}UKGSfTq@uTjY`y7TjxS1XsaO#Rx~!Uii%Gj7quZVBaSn*$+UDvCe1Wj?fuUA-*#E(OsBmwXa2wa&&RiC&wl$oG;&@~dsm5nUeb@5U-eh}OOgm@$yLftF>OdoO3Crh%+Bv2xsWe@HZ5HcGe0t}hm<RA@lH<3Nium)Gk6E3PWARPc&BEWHkcAK6S7RnDZ&p+%*aWx`Z;S7vs0|sqsLF4;AfcV<7e1r_#c0LtSK1dU21BDu9({xVpT)juj<9M?DNS5p=x`1v+&I!-`%Em@vF%<`X0Sce(l~nT3^1ktx5P&$C>Nm+Tiok?}SQj_sKVuG~UztN@l)A_-!xj=)OvP#(AOUZ-2PU?N{E{`fBC^%10UX^;OPuKKqHmEy6dp4!lM8`&%#ajV`b0xr`yl8nwQ%Wj3`p$br|{&#5B6((VD}6SDq>xNf@^aE|MfdxxIa^!G-sFF)*0`OEGFS2&;6v-Etv1r1b(Vz*|kFVAtH{*5^&DSxT>NhSH0FR<V7<{IVUS@Ribdl~uW5(lb}8g=tGoX?2c<R3CLYkk$fhVqfz|9XjiU$mdZ@5?j5qV<)^)6~B@xRLX}lzfWv+9f}vI#)d5_gGw8L4HgO`R0npDqSxQE~9?R?vk%MzoPuj&Uq)OPIWG~sGc_lShT)cHiPP~&Y!^Jrgi79InUwu=)GJT)}r-Q|4Dq`>LHiOuTYP1`=L~4b5ul&)>kSYQTw*)$@E-OPRdbI$7u46acg*-=L|l`e()p8r!|}2i@N>6ZXUN^a6h%ZZqoH}OFlh^%glPJ&y%YbtuMu#;&Jsnt(vZ-z&vVyAoeb|x3p+|dHOG@e}jAcMe^;V(x~3Qji>jeBy_ZBeQDPe%2O&hMs<*6c_@#Qe(dji#^ZUMS1RS5`;^Cj#wRUWU-2)c_C|FszsIWf68ig?2=ZmMFZH90G?!9-Ki1vk_cFFc>&uRRYT<mU=zCCOJIFWJeRGH3d+-CTua<qq<3u^b@4Y1aFy*o0kM!P^x0XH7`bwpV^Ev;T$MfDLzo0yPH#Ktq|7g+rihn)V!QHo(`iWh5g6|u~^M>a|i`KXG-_}}GM|C)pc#^JNj?wd~H=<j#zVX|$^jxxE(gUq;cDX|Nw-s&e<QrXL8hLyU>Ex?rft=5i28-609=@V_n&%Har}dT0zfj$z1%obh@+-GL;_o!Bu5&-dkGLPxrB3%vY~}a<{B!y)l+a6OxSt3fw_&+W)IR?T`I4i7$G^$>F86b^l6<!go^NYCXg*X=AOF0&I@^4GoefUC&r(0P(s`b7K60CV*R%W{J9r*8oud1y<yGug`tW@9BB6oudE|MHuD#ClJQ<?!`r;IEuDfw!^Y!Dz;1tJx`#S1Js@Op5PTRws<V$mQaD93WqWYM#oU6JUw>DotZsnj=Ro#6THowbv;gna^-FIj6_1~R2tC9VeUR=+T(mPzAx@z__=)JUAHd?g4{(Dy+HdS-}-|+nW;$;KZzu-KzKm2>FM=$VR9-rrWhV%O6yq)SMIaOYu`|0N&`1<+B7?f7S<MTA-Y5cR3MeBE&--7%uQeE`(Bz*lmsgzsD*U!T?Uq27aL9e*IZl1UK`gvX{KlTOX|MU&lIcih0*4M8ia@MDp`M#mFFH(zKTC{$b^~iDhmt2PwTHg)D^-Ws8%eofS_$7}|-TDY$zdkDEbyv83=k?d-cUgb4-jJ_f-)(-E^}T#dEq_N}Q~pZrPmNk%c6>tP$58Q#_HS+JlFI$mP<`4$!!250zuzzxj#Ie~ar|Ax&1%s4@*E@2C$&|)UoA{#|K($9FFS9cc|)l&UZpy?c+t3(GuB$PzJC8B+utEyzC4rn$)0h|T3^49YD<5~{p<E)HebIVGp7%`#_c=r_iVm?zb7s7sN?5)+RWo5v`OoC*-xggCSUa$OLbO|zs=Y0OARO5*`L0j_wBI(4O(Av{DJDJlq|o^{diobJaqeEo3Gyws~!Q@wd1Gl#Vwv^z7N07b?CegxB2>gxS{Yn@)iGQeD26MG<EWI`+V8H`Ub!E&gTW2uRkxC)BgbfB!BOp9>1^k_2&`U{yF*jbB)dKa;~u-&HImb6Frw&+e+is{QYO->(5g*Uw@u5PI*Rtm-8BY{dvutZdcFu)t&q71M9i|nsZ`gr_*or)H9Ly`bv@rC+q1qHBoc)6{h&vwELrP+NA&L=sRK3`2Y9lyT_Wtc5Cd1?f~xxAA}Zz4}$kWe-7RU-VOZ_yc?`QH-Qy!t~FLzBh4Bq2*K;2x!_#1Uyl&H8X-6f`XN|o4mb-O3*88w2c3fuycD_-EOY~SDL5Ot1H1#Z%SH%ZgAkk#-2)a{0L}-S5Q6ip;bx7Y)))fy1`h#`gpLP~1doLVgU5n{pbNl3;7I67a3t6WO$Qsn8PGg%26zj!0K5fU1l<EJ0+&GdgG<1r(1YMo@Db=f@DcDK=x*>K@Ls3_-U}{-=7I~so1tmo&EU1r72vht1n7Kl0(hY{{H-y?8siXxr$QHk7oz=Cgy6Xd!Ew+PV4*4CIPh|W;3VjJu+Y`uB=8bw7FcL3*!DdvK?t4=odcc?4udWQhk+MEv%x~wfER<4q4{8;CU7!19w9gtng<q|4o(FxgRTTG1BXKwfWyHd&|q)~cp`K>cp}&r>J9b<8=ynM2Jj$+;DJy#u+RbEfnXPeVDWE}J+0wjjo#2c;NIYV&;j6n;J2Y};J3l<&>>)V@Nnoz@Nn>Z(6Qk6z|)~Y;OXEfXe2layb5XruL5U6Gr*bPZO|>?ZQxzdBJeKo0cZ*M0QfMp6nq$b6nX@F6#Oyt5cp&8N6@|CkH9;jh2Wjwt<cTjt>AUgwcvH&L}&sy5xfYx5WEN+0G$F30Q*7x!G7Rj)))*O0rdxu0FQ!>1CIhvKnM<mP6Z2{3l0R&LI{qA#({+{2S<Y=ph;k%OTa>BgCoE*p<&>e;2F@x;2GdhXfjx6JUA2_15E`BT?UQ;e*g^!e*k_T8UlVFJQ+F>JQ+L&>I)tN9t|~sM}xhfgTP*3PlVuipaa1|UBK^ve})j;7up9b)B)TV?1&KD1KJZTR08(^+e7WZ_FyMyFR&B1KhzoAAM6T!3+xJh7djX$bOiWaum^M$*aPeXodEU$PeKTu1`PxYoduo-mZ8yLp%GxAGr^Jbdf2)4{7?T4_V1rU#nb+$nEo$2A0f1V`P$mozYY|U^Bj6{@$G2AcMuhk{s}B8*-`'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
