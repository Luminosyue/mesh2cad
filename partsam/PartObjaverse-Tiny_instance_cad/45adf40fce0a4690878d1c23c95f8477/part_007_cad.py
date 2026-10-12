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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/45adf40fce0a4690878d1c23c95f8477/part_007.stl', 'relative_path': '45adf40fce0a4690878d1c23c95f8477/part_007.stl', 'source_sha256': '775ba614d26eb28845f66f0e5295f8d617b76c9a88cfe572581350a34f07eece', 'input_faces': 288, 'input_vertices': 232, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16174936294555664, -0.165934219956398, -0.13012754917144775], [0.09418660402297974, -0.13340051472187042, 0.11073178797960281]]}
GEOMETRY_BASE85 = 'c$}r0dvsLA9mj716ljIg5|9e&B7qGhghzM;1rn$gG^jyK8=$R8AQX@$F+}94n-+P9LJ;NAmar;HM34j$$OA}1Vx@pcQM3xA;UUtOhqnHKwx_2%yPp|$e)smAo_5c<=kv+e$#3W0J9lPsB_q8}+c+ok>FqQx$yu1z-Eq`$lN0AG$So|IGb49?QeMHL7^h1(S0Bv{4@|i~V`_}Ez**v-nLB?*q5n>wfAp*rf1=MnE5ER)Fgx#&{KA>JD!(Ut-u&E9K7V$0L2l^hgrUhp6Mf136Mf5k|KsPYst>~|o9jae-rcoP(fPwas_VUSXG_ai)%D~OD-Zs)Pn}}Jka#=)!hb0IdxMrXMdw*g>)~)d@XI4s{f6s{!gUfqJL2`dfy9$m9vG3cAyu^>P-^83v9~mYe{VpM-TuXYZ42l9uQgiznbiBW)Nuai@Xx*}W8PA1y^<ff4k8bnEvSxeuj|P6=6h)$NNBO@`2Lt)Q}2;yUD|NKD{uX<<bYS5V9TVM=v;rVtZ&X&)HnSX_04^xzLQXC_wz3|*VcRFzSgGwUb%CodB0bk)(bsqqjS?wQQw@GsBgxJsBg}T`T>8beP7xxkBk$4f!+UW$7{Xvtn*#>d$vCv7x`Y1JD(h_jm}N~MSXL=qP}S_>YMYWep<irR^G6<{jTu&_3dHxC+%+!)_LY<*Hn4szEjUurF!HIS2F6NbN#)tzR5*>b6%pp=|A<I`0@s8od11CxW3Gtk4IK{<-wCFRbF+Rt7TSwGtNbQbDc$f(_Yj!?Wv#E=NUV1R~8v>edgKup`+#D_IHf8`}uiOxIZ!veAKhbEBBr3QRP)9c(u7MIyc`d>YL|6)HnA_)Hm0G`p&qrde8eMa&tXpdwo4+dwsviUH41mvcBtn$@aSb*vPtM+Mk}jFMK`5oIC9K9LZddbCH{IE^_l6k-MHFnTz_a=SbwH{#^-nf0%z{uIC?Dd*&aR>-k6La(<J!tS{#`nVb1@RPd11PrWXP+^h>CH|v7P&ALPGT6aV)>$}z+k(+gA<RrVFdR-Q|S(im_)@6~Kb)Vd|?u%U3cdh#(H|ze$!FGT2K1bwcUqtTO7m3`oA6|CQ8n>saBhTr8!L`=-zx-~v|4#3~0sFoLBiEtZ_DZY&>`R@F+bgX0f66=<uK#8G-Bv%p7#Z2GzU>cM_gBx`BG3Bgr;+xXmoE0KGkEzEsb1eZ`oj8DuYS&+ywz&Yc{#^AY>&>(b!fR>7M+{x*4klbs@MGzxw-!2uKOi&)Ba+bRY#9End|W;b3NW<ZpItA9M3YB_2qb$xv78on%z(Ryo=mC?;<zPyU5LaLhhPRL@w*Q<`a>d`d6>NVf9n*Cq-`dld`?uPm0{kx8$z<s>o%1*M3#xrv7JHyQ9BXuXnDT^-kt`y_31wH<HWs)Rl|+ay^x~sei4&%Jn|M`TY8u)_B(Y6Oo(!iEOX;C$hcXpOCxuKO&d)UHc!|Ue{liS#EtV`$L)Q{h`eD{!r#-e@HI(pE8&A<^EIVrv6jA?E37ho#Lx@uIKaOVHKYDOXTKy%J%wt%J%wtlDqDg$Yp)k{gUl<{pD@<dOk-o*W+B|W}J)MjB|3=b0l+7-}M}c+|++M)6V(3)mc$#_fyY5A~*AoY_I1Zk(>F4+%><6T-JBZZz4DKS9jTGjc5IyVfE;JR{!<7Aab)Vh}^6TA~)*-xoh1KxvcM6cSLULuPL$nsn=zZn{`>_W?dG!S(nLO>%Pckeb>4#@*DMc+5OS`9Fd!S4!LVzB=Q^WEA4*j_lhN5s;qIY-%mbYVCDLKrnBk9eyfgtU%ItdwRK+V{c48w_IZ72{7k2FNJB?QC(fCb9rfxt{2v_0(EHW%oMHdntLK!I|M%7NkWe4)3LU8&$|u0@;1lo+I0?_dGvW8}Ogszz5YNJA!<qPOJP*#p^YA$^7oUS?!yn<<_*6IrpNdb0_v4fCiSTZGBAy0E<7xN^I20d&C&6#yNqAq_8}Ezvf<5qFcpU74$Kjpe*YHkwSNL_jE8Y{{jQ7Ojp%0J82g3gNKzukHf-9!tuZE7@p`(IBc^y1}*WpdD9&f@=z@zvH{0#gpeg;1eKf=%B7hx-Y5pRJX<1P3H@HGAb{to;N{tn&@8}MfQAgsm@;(Otn_+ES`d=1};zXZ49FX3C@i})6NJ$w#dkFSPL<E!yv_!M4@uY$|*Rd@+}7B9g!!x!+)co6;y58|)GS8>G({FTu0M(EhXp}YoG;Wc<8JcKvm$KbE=WB7aUUHm=#Ec_5Zi(i1h$1mXL;P3Er`1|k_{yu&jzKtKpkHEwD5xf@e$7}I&xC<}G%iwmr4BrNSiEqO<!43E(d>veauftcupW`d>0DKY;;49$I@D=!4_zb=l-w2<_H{zx67kDYY1HOVQ?!l8o$C%JDjzjsq@VofE_(Sjk{2_cA{60Pn&w)S2bMU!v7Cslxhd;&h@kilL@JI0(@DY3lJ{|r5pN>BaAH*NV?}PW?_u=E=SbRL50*B!#_+Xfb561nl5AMfrgSX(f;oadk@$PtMcoW_k?*_ktcf)Um-@<Rj`@uW#e)u3b03U>pgvq$#I9!bZ_5a^vp!)ev4&?=K8m^dw7vP0(E?$Ti!F)WQdtU@+;A-AhbMzt(<x5~OuDA+cf-i$5xZ-Af8NLq&@qPFu_&Tmwfh*SGm+((u6aJPHnU7wEWw_!tTyYcrGQJe9!xdNJiUE8nz8J2+7vl@zT0F~%>?0rNP(GhS`C~8-SDb?@X5)|H>2NBpI2l)*h^ONTFbz+@JHipTViK;#TYD!m_7uN@E4IVi(KZGq;fj56#a?&}?m+!#iDD<`#z%Q9?25<YZD3El4c->U<8AQ{a3J0Rza0+8Z^uW$R9tZaJ_=s|GjPRBTrmq*d>mJN0#{s!E3U;AH{yz=_yW8V?!XoI;Fb7ESc9L$FT+OsGJXXf!>{0<s`E;ZiH&RXpZ@96jZZ+`SnD4$$=|g9?2P`+CquQ&AE6oP?bP@R-R#)#V6Rbk&iOa_Nuj_'

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
