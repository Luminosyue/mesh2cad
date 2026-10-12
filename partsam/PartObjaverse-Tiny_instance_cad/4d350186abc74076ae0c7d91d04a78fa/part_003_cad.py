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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4d350186abc74076ae0c7d91d04a78fa/part_003.stl', 'relative_path': '4d350186abc74076ae0c7d91d04a78fa/part_003.stl', 'source_sha256': '35cccdb216db6f22b9c7f1f0bc7b17031d12fa2179f273a031a68fc0b6b81723', 'input_faces': 152, 'input_vertices': 204, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.471861869096756, -0.33318862318992615, -0.18121355772018433], [-0.17177525162696838, -0.2347734123468399, 0.16326278448104858]]}
GEOMETRY_BASE85 = 'c$}qK33L@z5^VwuM3JBYWOLFOHU$>~ksuk;xP;9hVGm2_011nPK*FK|(g=abqKJ`20{*y+EJ6$+h8Q4Uc4L4qpCyYx3mOCm9mN4<K<9PU?aX@|=bSk+Ip?0b|DO8Q_3G8D_i6g~ty!y~#(yof_T`J~dxAC1K|QUZHZw7G`oyt`X%A1C`a%t@0qM@4Yv1TMIHrGG4Q-}2yY0Bdw6UpeAJ^MPCPlREptns*Nu8dWFlBT~>bOKlk4~7JmMHYJ2?<jZ#piZmk9O{$cY2_MK3D%A|Lzbe=r_a877J@$8*tLGT3PAAVoBFseZtJQqa@w_Y?uF!{5{aE@$lc?l>Jwvogmx1`Rn9=rV;zMT6C2Bi$hkB9uY{o_B#7(-G19n-%G1Yy0<iybUnN4n`Fn<W*u?7V~g2eV_nZ$NV*mpkx8FRG$p>(@!D?Ehu%6v-$NYF@B-33zg|BhKUW)6YX|A!tm}iPlkT1P{Sx~AqMu1O@LbQF19_zHy~^=FT+HiD{w{+)U-^M`#5eog+(Vz6{Ec)Iajdl6q<f00l;_$zgK52<s`I34TRFaV{zNW)Kjtjw<ND{^$?K}9;5hI%%Sv~V4L?e{XA<)1Ibt<gv*e6iPy6!dRrEP-H`fRLTJ)<_AG4}Zse_*KEbBS>tQVke*$1f(dQ83&$BtZ7O#T(Qysl{(ysk^f7Lot+xoUk9d$ND{`$~MRmyhdUX0whs*0-;bt{=+cIIe%xVXA}v(;C*{?-~CJ*XQJN&IjkhYErQyO42R#zX@HBS*G-lo*uJ`*OkHX&2*06ZUFVOeSEgsZ!x{8Zg&0IYQJ@AyqrG&HjAI@#+h*k`*&qsck4DgWGU$f)0BSGN}r&***~W6z9Wt`Ie_)dNov344&#0cV_mz-=g6G%?n=^&laxAZl}-6Pj$+;WEuSw<-$--7(`Jm)pIXNO)Sq@<yi$Mji@QlThs1F{c&;_jr1RyuFqqfn#{W4akIz%A;&1mJM(4<!5ySakf`3|5K3`i#d`Wp?UKuZrrhT+e4JF;gd@y4-@V+PaA>D&|S_yG^j_$b;O}f1fb0A_3>G~sGN!PGm<7V%C(uaq09LxvPpTYW(Akr<I3nS&&cJ{BQ#5besQ+#{l^-5Z=+t10%DUR*GO1eFj>#09g%6jzCN;!YczK7%ZOE?bt!HgP6x><L3rJTQBvo^&sI~6MNjfy8Zey@T``Mh{~R2Iv+dtO{!FWJIze!~18bBmulbR+v?fAy}Byf5=L&J*+82)lZKJ_p^ZpzpWF{c_Mxx@XZpE9Cvv8%KRY`xX2P>4v+%SLU+*{tq1I2-n9OFpKUxkMBFuE%$!$4<X&$e7Qodr#_=gA?1Ivil6KD!--j>>*LQ>$o+5pIG6G?S5~l&`Rq-P=XFgkuaN6+2em7rIIB-`K5qY{OkllsKIu04$J?cd@9UMhO8!RaI@0aHk1FJT)9=jLNp)WJp_0FO{tD^(ye!h)`RR=q$@$k?%W>R!dnA%{d%<eXAO3n^GUaJE$mICwAN$-E)?Z3f>Tk?j%lU6kVSjgCJ^KRZzhH`5|2aQ#{@W&T9CuDuhEe@J#u%mkT39ys$#d~a{zkxjUf0v3)cQBRKz(9PjZ^a1XNFS#W<V^*cjs02R@^5K#gMLJ{&<hq;&s(|rb6z2`_`A-Cz-vt&TjvoY|j08YH_*T&xXI3m-Mj<%jJIdcAr4Hd1EH&7V2X!UrOiBY@Jpv@2@?sgwNxyMAGd+yk4u}9*U!1OemN8%{%W5>2_RXx!gbYx*8nkVuTXklWOoB@Q0Sm{opM<$MF;Na=D(y&EI)l{u^aV{+ZDf$Mf5@GI@XP=h9ivg6`heg>UVXb$9+$>u+8vlh^BAy^ibV{iaOGr)Cl7Ikc=y-Y?_Oz3l(>i86V=wCi2CK8N2pO`jX@;W(%F@25C37Lr~)$C_Q>^Bypt{oOfsc`xZ&cZ>A{-HuUS!{4De)q49LM`hh!lXhA@M^>98>NjnF3hC8zpeUMjYxtPc^0_d|llfev$FuIvrR093TXrnz_E#yCk9NEtJ=fLs`ga|bb@P`9_IKw}$QFKXXt<J(_V*>6XUkA!y;}MW+OKLI>veS_RVTfAE{*KV=lAy(r<HU4V|%Xisvu=wth!|sM^C+eO0JvnZU*IJtiMXSJAb@gCi490RCP+On|JUE-mlT;Pbts6JeBMAj}z>V`CyC*=KDqef^>I2Sl9So)6Nx~RQmbzZ+PFKSNAh?efmYe+*ejWYo0T2U+~L)Wvs5v`G=qK%j?yGHgf&<9rw%oVxbP6>-+ukdaX}$C{ORgPyKSAXhXOT*7bFMdEd3VS9ss=U!%s)I>K{u+5*44k4E6D94Bj@U#_Qx{?vnpEBRYXOE^x}5Wl=%n$G=Z`+6z)8{Lm{o#UTY;~(G7>-xEiU*0coeZKeYkj{R2zqE7VtnbeE$@TX(gZ^!<Pp-d~(}?RZ?>(Q=Z{O|YI@ingDfPiUX!dx+r}W!;FZcP;*L+I-r+BzNJtp~-`s=s2pC>1&@pqizJ}HXzDfMr;f#X!g_~iO{^Izin3~Q(4?;T&s{ZrM-C)eM&$-hIaX7?)jyK~R;L9iNs+df`b_dogM`nz+?oEYGf>+jAnqcGuf(%ttA4?Iri+N&9)dvG6V_Z94QbYtOtq?_))(<kMye{o5P;@>Kj{YPb!?%rQUK`!}Qd287p_l0)x3!YbN`;qS6Ut0JKj+57ubbB;@&v-IPw_0>y9ruy(ax&-hSZg)@_scl`xI5S%_mMaE6371}fOG@*k@Zy|`)}I%8Tn(bT3>TNRO{|MtPyrd(J^mbe{19x(!J+-{#(CVimnCm{C9QZ#3uE*eQK(@8y~vXV3V59L&pyAKHucNxb6LwtKU8+UH$g=SFWzi&;H8Wy=?97a8Dgka)Cgtp_Y^&zuK$AZm#{~S9=pX|5vZ}I);b+zpwT_6FICDI1D=-+_6uAJNABX$JPKp4DS4WE>PmE2XOcdz~N5=4iAM501pMPDUc_SBajO?d@Jl0@U7sRU_Sug1pdCjc7cxsw!wY~z72dc>_+g-;C}@i{+__Q0&fds0}fvgyAFIk_*&T2;A_F(6nMwkbAb)8S>PMM--2BO{ucNuz~Pw!uL~>}cnxs)64*uHOTb@-wZLBnpChnB;8lTTu&;nG15byY51tM_4{-Qwfkc5(0ttY_<6sAa$AQPf#(>9y_ZAo@U<!<c9R@xUd=PAZ@Im0u01odZ5H8SOpd;Y$mazAMw*+qldpCF^@H+)M3p^_DAgm7lAb4}whTzS?8vqV>-kWz4XeaP6;P4RGrr;sq!LaqggTd<xgb8#IXaoCa@HXI0VDABM0$vYr_@4wG5oj&&0O0Tzu=j$u01tu<1P=nQE%1;)TY*-v&A?lMH-^0nyfJtkz~Qw7dJ6OqcoJ}U6zpHXqrkhtb_MSS-bEl<;0XZ(wmY~19trz6cqDiP;PA%;#tV!V7z;Rj1nf}o5#R%1p9LQX-d7+=V2nUK>~QdS@FB1Rz=weM103E*;01v+fmwjVr@^LxPXkYeeGWVse4@bf0y70tVW)zpf=_{+3_b;X65#L&0-p-()tui&Z1;nE!S}%)1m6dK0C4yrfrSDu31q;&2%Z7H6m~B7Qt-uq!xsoRcW{xwZouJ%um#|S;2*>0gMSRZLtu}<E`d*AcY^otTO*)h&HwaYcmMvg=pvN=Bk%Tasy_?lZ=Mygs(&Q(?_1kBr{Y2kpp7kbCX4njCxRIY'

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
