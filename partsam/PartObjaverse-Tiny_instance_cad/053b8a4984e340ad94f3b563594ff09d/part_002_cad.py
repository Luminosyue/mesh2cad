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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/053b8a4984e340ad94f3b563594ff09d/part_002.stl', 'relative_path': '053b8a4984e340ad94f3b563594ff09d/part_002.stl', 'source_sha256': 'cbc785de64718ab9e4c6bb1c4dee6310ba171d4823ce6e6274dc34e7cde3214b', 'input_faces': 248, 'input_vertices': 211, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10884964466094971, -0.5000002384185791, -0.12745033204555511], [0.06978007405996323, 0.15426020324230194, 0.20405331254005432]]}
GEOMETRY_BASE85 = 'c$}r033M0L6~+gGQIHn2$f8z9v4*{d9SvlNfIwLOLfE%Kk{}wkBv28-5kjCqSOQcC+a&A>ON1l_0%jy37*JYzS{EQNT3eS&j{=Gw@uctF_r3V$8PD;w;oS3m^PBtbTW0?sLa|}>ni%5mA>+WrEj#+NO&$%6CdS-^<kV?X5>h(Mm^H7C(U>^@le%umh{2&Tb&R>j{D}C3lqty(kDC!uiQOaGnGuOIlT(u?&zLkbIX;2&ev^|@5*SZ;cJizQw%w{@WMn(DQ|or-0`q_TYrw~lSyfWX#9P|$2v;ZcdGBb28`bMqtK3^FxVh%!?r4QO_jEkUxqG}<3E#GcBmdHgV$Q9povFUHa8(ZF>wIvXoKl4w--l7Z?xWc|YUQIk><rX7|1TPk5qWMG^{;Wa+S<jp{q|lFS3BvwJkI@`mPex%Zf?sJ+x6TNRA0+?zq?3vZ7ttU8gqiy@j@<fKWolj8qfQm(|Wkz#@R`<ZM>S|(Kxkyufq<pzFNLNFyv9*x#B`~{oRpRXK?GvS0ySp9?qlnwauo-DephaXuR%2L2mc$O~=n^lXX~KXAkRagUjP(;&@4JVx3L7{#qRe$I;aC9UK?uZ02h;zq{_-Lv_aI7E&FJJ7rU7o<`{EP8uJ$g?w+Q;1=fPW4_MNV7@KuX!(|0hY`1EyskVht0xvkE8IULj*I=^gk!WnPRswM867_-E|~A8H$6t%E9PyZe&6}wB<0r)r|ZJ@l8D>6$IECukv)j}r9tjh=VjCOjY)#P{YIIX*Ez9XC&RO-{_$JE`ZvGZMC00260HACkjwgJ+pEOwk`saY*7d4P%D?}IE7aexjR&J^;pTz(B9)t!RhLz6X!&mJR9EFPU)Go0O)9NY>v-3K`Ld4WGXLketnc(4zn12gwWvazw`r9sH#KhQ`RT(dRBmeA(DIEHZOT+`YTW4qUVSM)(67d2zU0OSn{w2AL*q61Pl6wOP+TX-_hN#)W}J=xM%S}xetC(`iz6%Px-%LDxmnOWo9d0dlty(*B50iclIw3#zQ&#Ox64%SHEXz2&3DEGxy*NZwj}N^O%v;O;;N{xaWmYe^>?Cz+;0B9=(pQPv#EVtdvSgj%@uXJ2DuwMx;(&*Z?gmWU4pzOKlh^GKZrU;2juSyayNENxyqfYo7sW<y+K}+UvJ{@z;*P|jf1suujg)Y-5EjdtlQwK++We9Dv*C`0&y#D)8#<^w-W;SKi0_~Lg!IvIjytb|GYR48wa@;A1~Iw_3~t{KDeFMTI9D0a?1{<`8w^|&ZjzWE)@A+q>AI4-Ho_WD!3ChNAOkVOQf9&E2-a@G{LRS#J#O~#O?EQPE-5dLGIpp^c3Zrjb5SarfL^)%R5f_p2p455tMJ8jbE&e$6S4g@*R!)pFK|b-saTB>b$%-k#B4Xaw84-&Fg2-{$)6yx3!@2#A*@b<`<ud^JGZ_!50bc<lif<FO8ekBHugp%$jKBJTcFGBF=}3AoofJ98$S;CGN7CZ%Uq*cS+@zR>!_r=BnKKXAjD^V(L-8t<{(Lu2x^?ZikM7XH2L2lAU;QP2hN4kD+yNHEv~|66>%uY@N#8uiA=r?iM2Mj9NzP=5C)X)>Gr=g41ICy9;i;J5)TU6EBE58aEs7C=c+ko;hm1qj8yUA08?Cy**Q0FV8=4M&(|MHR8DUm@1xY;N}!DPVc5o^*ybQ+iP2y%4HpMZ|8EA%Q}9`N-_Q;g1d)9;=Y=S`GWfe)%of;C3lX+5I4V^A;ziI@iKGDRqi*9*;!k@wd%bbwZ7!W0I_azJgzn#IbT;Bj~~`n%vbAI=d!*Wr>~7i)^`f9o;Pn5M=Rqr3WHqcTOYLASljjPXk1?J-l8@eYrEc!#X&BwcV}I%O@Zse`d%Ez7UQ>2J=_odR$Ih<Oy`la#C<aJ-^BI%o~v<r-?Lu$TGY|*d$z{qea~5NWxHBO-sg?)Ki;n9%jbd@x<Opt|Lv??!IN&I`+?b@TD-^NdFN}~!}C;fqiWaX+VcHFgQ`?+Ob^y^@q9F=2kYou){)$mTzfux8kf&U@7l#2mCNU^uW|YObz5c9cboox;%QvIZ%FQG?<c;-Wxm^Hy{MzTUwImr?@N+f`ukPeAeZ^p*-?Ad^IyIP+8USddpeizht`=4!L|2Q8{F65OSOFYUg~Q3HSeokw+cSHu6SR<`?IHU8}H9v>G^%sj(-C3@!@;N2X`-gb6Mqvhx~%8RL2^Q?<Soi-}HiYe0(2STE67Y-|OwC{n~fUPdL6KT#d``2w!sTyT*7o$ZNhkB-g%cERENEH-Z1;yGG+R<N0V$K5bWIFQNR;?xx>4jDHAj?K~&+>t1v`?N2{=jq>vvrxTyQ?+CR6_nb?V?>_Pc{eI$V`Q9fFQ+-#<x2{bT&$0Weh&yrP>3;0a{80SP1nxVt3uu4%!Tjh@;8)05pU(N%Y{*KmsBbhe5+^G^L2}6dq}Kiu<h0Je>?g?1-T&X8AX~68G-Giai#jaovIvLPhc~cK=7huF&f*TRJJ5#vde~<`>%jAR_o6-57Vtc$DQa+S4*zQw_tBCH{VjYW7JRwGpud3+gTD)U5B#s74WW(U8=#Lnp^e~Mv-lm0Hqb}m|IFeqEY3pThHuBB6^pje2>81&hDV?#{KG6BKz|Ql4vjG9=2%Crcf+@2@gT;{^?vwwSe#>V9{N}K$654bF&4T4ek}YeEKac~V^IM;310zUjy#^93$1|9h37e4S&U&31ziXq1-}Hk4}Kr|TY@OVSbAdIQPA#6o$lyoDT|dXLeReOt5{^PI0!uoKa@ou7HQCQ_ya6nXR#c*41Pb0V)RptK9-^lZ<_}#g73$o7mKH$(eUY*TM_gWJn!o?`s4aX_?1}SzR;fVPoZW8bTxbtY8FE);FqJ`)6jnKd1$jAS`0r7eXN3Jz=zQPP-q|cgIL=G(AVLgMqk6APr>)aT>3zx;Fn?U{h+<z`yeMBx&%H0b3Y1w3!dv4tR>e<WnI^xE>}xAKD|+c>st6?tl>)N3V7Ma>(JBitI_r?=ow{yCHk*K-*SEy`nS+G_X#WpvX}-P4?hilF?139V)%8?z3}Vcv!Dg=TUivc*aSTSKas@%^gjT7b05#5Klb;>zKLj;iMHJD!FDFR1AQ6Zfqxb{4t^Z^kiI{*voPkZ&_Z}Vms~Ke<?y_(eW=ZKAv_;j8TOZ9-yY2G39Kd8vGBbAZkQ+69`G-t<~ZmW_;K+4q21ueqvj&$EARyvb0PF3{37J+h33K+BIgLS41NH{HW2y*`~((LStLTIz$d~#1Dy>247`oteiHKezUQEG;JN+*{yF#;5Zteaz6!q{elv@0&@Iqc;kUqVL~y^I#XJ@pSj<Im|0l!-C4U2I@cBNE`AvbBZJ$TIK`e%_m=9e5pU>hji$l=Y;O8SJA9@)6MHVlyh=mS@KZLd~LSKT9Mb04T5cruacCeU@;Qknbd;Z?pk;O<BG0>UtG4Q<IlPo%eaqXhybU}?27O5<DLrdUy!@r5Pyw+%FD*R~p6pXDDZMePxUjonTM55nL(9ZC`$5<kvUEn)lUwddI{3!ID3{8RWgqowEqv0RJz7fz-@Y7k$Vv!Bq37>?0E;Ji{xYBL}+Dylo9>e~}ux~iV&-cYahr{RKIL?61gg=3`%Yp8IKaPDaGzWecj+4hC6kDfmldzxrFAhKcIrNgP{)Y#>W$?2^ZJExJYCcjzvA5AXe_i&EpKKqReCxk`+61%'

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
