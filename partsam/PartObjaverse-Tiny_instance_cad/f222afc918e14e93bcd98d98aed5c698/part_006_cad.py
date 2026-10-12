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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f222afc918e14e93bcd98d98aed5c698/part_006.stl', 'relative_path': 'f222afc918e14e93bcd98d98aed5c698/part_006.stl', 'source_sha256': 'cc0b65bf25611add888268bd629e1ff9077fac9e3ad4838c70db8b92c763884b', 'input_faces': 452, 'input_vertices': 303, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.36363598704338074, -0.4545449912548065, 0.09090910106897354], [0.45456162095069885, 0.4545449912548065, 0.7272665500640869]]}
GEOMETRY_BASE85 = 'c$}r137D2u8HT?fP(*<NS%y_c1x5r{TyRM+8!Snq)Y23YVGv4DhY=+;2d&(5K`plg7XrxzP!TuAEmQ&=#mKF&EHIapO3f5IFW>$CoO!-8*VR?O*LywB`~2s9&ikG7e`n_ZMn;cn-KJ}nzqZf%Z=C!2`aW4^(LU>%O{=Y|pFF;H>aJ5xpI*v3ZPM-KIP-|34<CJODVvs^Q$3+}>iD|q{i~`EoH(p{NLBU3)9UK$#!VS}THS<N(?^awWom8Er%oDodTq#e8oK+?Ayq>M4XHY>>VJG~9a>nss%Fhn!$T_HFr3v?vv_zyud1n8meL!R)HkK{S?g-nr1Zvam2af<6R)p-Gu9isja-xJ$93(;b?v9@BmKCp{kUG}XXDhS<al%)KVo*xvebCjTN>Z6%b2&4`qMS*Vm-Tb<l>aS>+0{i`j>U}&w6}*P|6=&{TqVM@Wg((uKVS>?pN7I_RDqc$Mw{DruuPR`*B_SDf>u2uBY}l)z7T(xk~lpy7uF`_EYweeq2x8U#WRrPu<t4dCNYD`#PStadv%EvvYuXRrh&S_jwCG%&U4!^ZNR`uIGvB+K-+m1s~~0&lA-P{m6Nux{lZLMD>=&`~6<fx!+ya^F(#^*Yl*HtG}Els;j@AC#vgy>3LG{k^R#1MD^5qrsmaiLv@{3&kfaeUOhKd*M9WeDELS}dTzw`QEFa2H&jpEzo~ik+^~7#`!k#`%Tjt)ll!aQ_(IK^SkG=RpKHrfy85{8K5OT$UzqAgb@x$SeY79d)kpgYpOAHrCq56V`@X2|`%>^(m-hF4aa}(Ts_VS^c_{eEy!v_Ym+z0STS4FO#j05MmyR#%jJI`;uP5G@X4e_*OSAhS+TY<V>~E~AkM6Jg>h%_M`ro_{&9Aqh%lOp&mAYQlwa?W3mAYQl-KSypp}D_&o>lkHmFoVvD)_8R`}^n0b^Sc6uJh{Wx!@!7>gRbx_mR2Zn5I`Y`5$)s@{~TJ?Taf?dc(MU9}D9vDw|@xam{6~ru<!3f7jK&JRbkXt8%|=di^W$zN=n!XMMBrdcCT9KdO5_h4IplUa#uvuh&}`uh;wN`d6D>SNF?TCf7l99bZ@n(aU{`UhY%Jd!Oiqbr4<s3+tfc#b4K9ZFlYixh~axUe$fx!g%I&U9U@Z_1EhvjK{xf^=&Vu_EB}eUf1<{Rrh{W_kIfFr60Xs)zx3Gw=iC>mwhZ;uk3GCW#!As^$}gi7uHAga{r>2``7W_KYC$(L|6a9`sjG^FRYK~<<EZ|KmYZ)nds&3*P@rdU#pLQzZSjxy&k>rd`xtmxA1&SePrIk^D)uO&o^Ax=VPMl_`>rs(OVi{etxC8KfgjRJRcKX{R_{>R9Am}J|?>Q7oLxauKQJZKBhjhUxnvmqNmm~)lcF1nCRM1;rW>8sr^m$Q+Pfmy7p6eKBhj>PvQAkbbqDhEj%9+J$3)4=GET=t5&lwg`XqM_08vebA9tUFXPMSJojDU=SXv1{fj?GWIX<}E@A!T+*94xO?6+lf)DGadinXlCBBZ$&pp+3UOo2;J~FSKd#d~Awyev!r@D^Ub5He_#{0Qc&^eb}*K<#G_1AN+psT-}d#bCyo_nh6e(AYa@R9w}b5HfudZzl(b5C{cN6$UgQ~R6hN6$UgwI4nA3O>@0o_q2Am6})2J=Ih9Z))CV=icaMe<gi=!n_^t>y~8}?Xs@f#BtG|NKLetWBN~|llS_s{zSUh-h2MPe<E!PJ-iTN%TkV8lyYuid>e3UxZ%rL&JBMX@fXMqn<BmnU&A)|S+v2=upQiRb(V9(mm|K4d=<XVSK@2f8b6EH_!({mH+(6}x#8-FuOwfIuk#i78n(jEq7{CIZQ+J5W;r)}DdH>0SKw>>l@Mz}bS&lAzLfL!tanGSL&R-eJAl7~zlK+*QjRvZ6Ez*+h7}RF+6wSh_!|LV53y}2$IhjkTNv*Sc7q$P&2nz|CfsUYqy9De>P&Q^&af-o@DEwe4cBIy$5imXVV8(o&t1UZ!~c}!^*!*hu|25i0ynITxYbsIe}uoC<zCz2X=AserV?)0H{w>?7hIohe$TK!xFh_1#{3O@JL2o8HS9y3MIY)7cYqtdm*w2>eYn;Bg?hu@)LHbV&TxCU;k#MR4c~)X?VqVP>_weLFX{}d;D+yHIX8S4ZnbYwZ`hMMi=NaO_JbS#HOsl-JMe!5{CkK&r5txE<=n#fuHY_k!%woD8~zJ!wHv56tftPQnmWTFaKn$YoEv@;@eSk~=*{_u_!<tx&tf2chJ)dTA7wc={5awtl7EP=^AGSf9Dtw20Q?Mhh8zAf%emo45&wYv1AL8tKg9P!TmoJUzaqqGA$|&;4!1Fr8E1GA{9^bO;N@_`Dex(HIiE~E8DHm<@G$%d{37_};AL>bQ{kuL>wFUVBz&h(`(x@1FNGVP0zZX%=O>e&jF<7DA@&ThA2<wd|1VOT5Zi!TM7%X)4flZW2_FXT3pZ>BZ-=k**5s}6b>0dO!`<O~!1o3Bfg5fG-wI#nt;k#9>%4@A;coEV;roDl!wuWQ+v4lIL|($zd4`9*c7^W--y7TuZn!0UOMIPY<QcxkJFpK2fcwFRv3~o5?cwdoJAm83E5I*-2f)4NK(HgcBY6er9-TvU3Nai!2>#^|_ABNgV7G{OBJV`K^9t%K=*9TKA-dq#g?i@|<Q3F+jd~pcZVTU*ybD+XuLNtrgW+ED6|g(JJ9#DO9(}=4U=7@B4g>qZ`;hkq-Qyb}b_g*V+%e*P$onwXd2c)ozXm@dvtR9VzwN1a-kZEP_0D@yZ}?UC;UTK<tD@d{FY;d0JMT%o;i2%ahv<i2KkA+LB=1SR^B&Y2j)ZSV-Vf{v-zh|Oh@-)y;Kzm-65_kyE)lOLucqGlK<W*TgdYVz7CZ)SI2b+{U*`kK2jc5|03L?lf*%P#2K)}(aA)|=_&OgzJ^<gr)P9pX!*9b42f+tX@4P>Gf4q!e7~)4E8o(J5{{gw-SrNDQrh^y4&*Hsl;B@$f_)Q0=MSKSN4C;+vK+XA4?fKC>4UxBVd+%)U0=Um}CU`dd0{qSf&y08jx%X+jHpIjbCxPQ5ej>Tyn26hZW5HVZ7~VS`91E|-Z!CCx#K)75r{4GkYQ{yi<Dz*^ioBiMdnbSs;6BfB;0f>v_?-YA7x9zGy-(xkgg7_E8DL$+e@Jdv4?mCm9PnItJ^57dJa`@NodHgTe-`5N5YK?Wj(Dk*=Z4So-t*+off@WW>MS>W4(>J2fX~4{4e{>~Pk~QI{0nl!XW`G1F9SEiKc#LXxD4(!Pl3zeOF}#x;$HB+h(Atlct89x@+IKI@cYRZfsetL;P)7~2!0<m_kxSyi$gpV;%@Msh(AhhxDfsb`C{-P_(Jjp;3M$G_&owHfZs#S-QWWF6Cs`q@c{T>#D7C>*a%-v{sj0Wypen<xE%fje#^n7@CT`R09*>cm$jP%{xahClN-*5FOqfk{hd#KSG4|j@!lNrIcSUUnvXUgeGY46Yj+2DXT%qh8_t6-kahO`oku=5TK~DccL(_$XbbR~hc*x0_)Q^h4skVjO~hxB8(t5;mHZ~~X885w*MYafZ^G|Z@H+T4)Lac-2frc2jUlcCuZs9D$PKTB-$H%^cq9B;@|oZ*@Eh>E1)K@Likd6Inef{}+#cd*;LjueD{{lx@X@16t-7{u>7T@Gel=|R;u8M@8Le#om^iK+7=9ToKQtaaYKu+ZU0Q|z>_F~p-!QZP051BPEd'

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
