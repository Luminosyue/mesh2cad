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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_010.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_010.stl', 'source_sha256': 'db3e304dfef88c72f577430253d952a009de91680e9b6eefa6a700ad21c9a0f0', 'input_faces': 168, 'input_vertices': 140, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[1.484689474105835, 2.048466205596924, -0.3030852675437927], [2.3792884349823, 3.3324246406555176, 1.0276226997375488]]}
GEOMETRY_BASE85 = 'c$}q}3s_ZE7RQf(pyrcM(bA6jAd*D$k+1an2p{-Bd?YAxh=-b>2uL80Zc2h-J~ErialBbhYBf_vD8<Od2E}I&O2$OHI)$mJHJX->n!W%3b%$Hu%=gVVbH8tWYp>r~XYIB3UT2?uZbZ1ZPk_N+7vuOR`K68)hM}do5nyB{re(~JPfYK%Fg3f8(HdO;+<N__=@TQO8X1{JPEbN(dVE^YU^8fF(!ih)Gbm|MT1Hyj!q`P=35lAA#U-aFDxN+sE;Uiv_x0)5JH+f89Af5~|KqQjO2Ij<^7?S4t%Gm**_5`|w*OY!&KZZnZFlE10iU^<+^@%vTDz7<(|>;QW$^xsz^!Ga@HcL4_y&AcI=FGM9R9}RU!Dao&jYuY?_>OH3EzRYI1X-GD}2FR`i~Mmq>^#|_)0x^g5OWzBjXLtZ8cpFAdejp;I6<zaHCUTIsERO4Q^amz&Miw*zcucaP#|I_S<bSxb4&zj5DiCBh6i|!jBL?>N?|`hyZt<*}9i`2HpT46VVj>rSkKLb2Oa%Ym@VKBkCOZH}lDz7ZJzqee8t_ZN?UYJN=Uo$DaKs`WL+mZtiZ+{J)rndA1F%2X{rDA^+XFGvM_X!L3yW;|w<b4qiFqCgN{e#(V}vAy4~Vv&iQR@J5_#_AJ=fGr*15?-;-M>C=dFEfd`KW-aso{pt#xzm<_qzT^jRTZbR^X>L1_4{n|BjC_o_#}LQaaviw6=PmmCR=$sU*!D8GE2@U;@_NYyj6bxD@k`?yYi{<M`UT=HsAB%rH+&Gk-`pz1eQrPdO*#SY-0{;V@auVi;|j{bxSV5?G0)DjL*R}H6WDJ;*-69+IKw#eGSRQ&Wc8=;TX&KC&?sNctuuX2AWo%m3;Aan@Ha-4l_2kApIfZcDfAD^MjWF{8*rm&6~}dK#(vmk{@}LQ9*om{(gw`W+a18o`@UqJd52kVzMa6GA%R#&GpOV}`0wh$I7M3-=ban75Z`|Q{YS_;7QAs3>-Fp~^2l}IMwRzp5NA>t<9zfwxK-a6>*c7ACVzDw<KNzz3IFOCj%)B@*5S#Mr<kWj|N2ebH=6(SIr@7mo8y}9!u;5xc6|lEOG_E&&LZ^dxVaB?WzJa6dG5q|u+8q`ME(WufII3hGoQz7A0VH;dpZB(-eW#NIbWmSiaN%B<uLj+%oTWETy0$7_KAgDmu6QEV7y7qZzIpko4608MPT0Sr#pcg=ZC=G{<ANim&h*Q&S$$LzSA6CjXb@2GS1zHm`~RHTKKo_P5;c5^q-rL=i2^P8@S_zMckKyZ|uf%H+2m8i+94`RlE`Xx^9M(cYdD!@A#Bp9wtl!cfEha3*&n4#GBw(W0}wCBg|*VXw1Kv`Um=_{F&qO&i@qoPpsg0i-+Smvh_H_`CRfLxILyl;@j4|b_jXay6E3Lm;6YlkJ0bWuQ=YkrOfk<u)|p2Y3Ip1r?Ngrl<tN9lny^5{?Rau*ZySbC*b3zfLm?4a(@f`nEBs372F6Z<o@vdt1irQ#zJu0oQ}<q&(Ip~OGPg*{<7<=w@Y_%-6uQ1&B)2z4@=g51Rl1X{rbIzaXB*swjrMu<=~FD&auvCgq-ERR6+l9O*#L~R-qo88}~Aw6aJi^@Vq^myV8#_pL4glkDdG;`5UWlfIA1X{+$(xHHedI`~v^7ROZvZ81wIJ*ZLRMXD#ch$wJh*bA3N>+tF>92m7?k*vD+A2K~bQGLrqy-tZZ?Bab{Z9Ncz!5&X?J3cww;O&I?`6zaq^Zaw`=+VQzA*v#i*<`(j6eE%BXKXVXy*6d+Ey}en7F?Fab<4`NS*R8$f=+~?qP>1`U3k0_ZwBS6%yo`FVE$j*I4BE_fAKIr3`Q$wa?r8ofxV3vY&JT{A<o4iXaL4^kaei>@AHq0|z4*Qu6py;K4||w#Vn5*g>~Ds3G<Hn{cU>u9zoi=&AfHi>F@87Mhb#87{=ZG&xY};<;W!3<&i$u=ar{2uJk)K(dO2(>=s)H*>->&*aO={mJon6bpZQ;1eHeWEHu9=y^lP=;kNwlwLGHXzM_yHp`LsW^ll-$#KJUp-?Lz)*OE})zTE=gAd=J)rc?J0pZ_a<)*Ddrr_W<*(eVFSTor^j&YyQT3eokZlmnNbf?E6lWTiaMa<8NXgu<h}}b7&SH<h%_FIfnW1ZpHn=FCKO4>~R&(g=<z{?ic5Ip0ruJS#K>LVw?*{xSvmt;JGef5Z`CPvv@u+&Q@W5u94fV6z1c&2m6mBdK%;O@6Y%{x45`Z&gMDh+bet@ZJGQb;_r#$J~DnJ$GiG**6lx1_<jxPiumT)bz9+Ix0d6Ycai=FJ7T>YV_s(b+tV>#<B?Fj@2u5(=zlht{sk|6&iB(k=D+zg;yaF4ehmIL&z(kHIQOydstORN-6i_(+D`tW@4I+jp18*OX*!GNjUgp`-X93`0<YnBf${XQYVa1_z#Xlxa^1Uatl&P-9o!ZFJnMP<P@D%`)qTi+T!lEUS9apOWF;*jH^;Ky<)@IpwQUW!QIpU3SsS*a-vgV#%`4}*j!lA*zcuOy<{6Vl9y<c(E~~l;&Pk4nHRNwUQaU{1S6_EKMrYh_HBqignyRn6q&SaHI}P>Et^fU}-TZ$4-KX7vf&cHPU8>4qfs&=7wH>XbrII_8+$~z$jiudIcw4cXiL?^dN^CD_>z|M4R>B*3FdwnKl|(8Treu)lNXcihlE;-Kiq`fMO45|fSF%L3wv&{kD9KThEn3?PCEiRWF`~6SUiyfUIfxNkUwc&I%@pmvZ-LnE{@nNJeiEdw1hM0kBnyl6xE3pUr%0YD9^=sd@iNwUv14WY+MXlYJs&y;OYXJA*12aXS*9dI$<v~>ov-9cCCfz$h1r!9DOn*}+fOMOr(~#->7ungKuH@Vz6R@~rL?_;>l(RFbQ`&@+oo{SXs9DC{=)o?hC1>S?c-tlOFur+myg)`T0bQZDd{U(+k=(#l6GHdYaJxl#wr;p@{osrHzoIr?j`=(?yRJTX!mt(-=pMS(eCR}vQ|??N6DIv6*f}zSh+S@$s<Z4L{F3UEG3UAnJ8M@i=>_C5m(!bC6BI3x{KC!C%I>_ho81{mCTd1bwB^9Vn@q*4-*|Ne6HM+AzItBm82^P7du?+8KOOFFkO6#4c1<fXl*|ueudI56kFGAmh_h@I!od$^|+oT*EI`K@}QE3MRa?Nl0a#@uWP%5NKau8N_(KR!{pvDu{EFI!N!O^#b|gAQ$%z-PIA(FM!snGzN^QtpR)p4j{>pvGphH7<)XE{#ACizh!l!Xp4^)$TH7nd&h=Pt_w|($t3dQhSpyv_M`GvvrvEg_Ax-Rj>EFGt<V$<0^riP{_kNu#<I+F(d!VssFOfTphIfs&^}9sZ(hwz~qP4B-s<#IV6}yX)5n^|gcDUG~a=oL7ZnrnMKlN7<AZ@LEMf({I`-`^k6kolEO%~l>?lV2uWU)ty?j!9!M#DZgNeRxGN*)mHw(n9BEZTkDZMPHMTH5-bVtu4&E?V17l|+O$@(S?&Pk%i({Oo!Ge)UK6Z}0r|vBvYxQ!3WK4mlCwjrClqh4aFqXY1^Ye*!5Jl+O'

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
