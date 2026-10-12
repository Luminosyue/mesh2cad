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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/94f6eb48b8fe44c69dba4ef04cea53b4/part_003.stl', 'relative_path': '94f6eb48b8fe44c69dba4ef04cea53b4/part_003.stl', 'source_sha256': 'a64ce6c21b3820e5892758d6f836eb8d1b2ade9b527a3bec65ec85312dc4dc83', 'input_faces': 254, 'input_vertices': 200, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11800524592399597, -0.1366967111825943, -0.49999961256980896], [0.11803338676691055, 0.13930881023406982, 0.42858442664146423]]}
GEOMETRY_BASE85 = 'c$}r03se_X9>*^VYi1^z8CtD>){HQ>%tt<v$!AI;rLB>#Aw;1R5PX%QlL%tuD>4xc|A8R!7LfO25Vf_`+{~2R^k17|wwA4yN3Gnszxze!&Y3-D&+h-6@A-cCdjEIs{O+CmpP6G&KwI~&OnkgqeM?1yavx({_pq*PNm$IHh|sXuCnBR?cVnKE^G~a%1im;aDA<iHVat8ygvEx&_zZLSjF>ybr?10jZdA;on2^ZXQ89DEcs?#<er%YL$A*VQhZ%oA*1uoBzK#LDeI0R*|M7FTF$8Vvp!x>G)uR)2f5TnwZ=B_S>sz0qoE_=Xz;mbjYRZ+=-XcE`P{VVFdotx(syF4@n(%7sr%g8HEX_l-f5&$<&(+^=QLd)_R!8}eidW6KWBVnMdq<Yg-^jJ?=O}k2d|YPE*^Xw>zG+IMId|r-tEIe)M};|e6h?@=_<+=pR(idL^0S{e()c_4>kQSQyoz!qu}i7By<U+e+V6f!H|J_q0_Cp54aHLX>Ill6UR6cXachDp*Bj5*ih6Dk=T$qYM%1ZOp}D=Q&X;oSl~3}d^KI}D{q$M;p>)0x-&9lkp#uu2&X*RP_BZF}Mo`XLnwq(5`;Jhquj-gBjX!*!$csnk(DzQ)eBp1(HD%{+s#DA1W|7xZ?l`-?fX?UZo~LLXg;$IG*&nDrPV}RNmx%s<n_MR6g_OIF7uK0`B|KNONA7anPyMU=vnY4&Xvmc2<zSo`XX)S%q<VfdQ{=hh)1~%@o}rvg`#Mdk^U)Jkbe=OFE~a(Dj){5vVi4sld&DyHde%;QQ?BJyOZ~V`d5HFZ)z_NaE9cr*Qtm%%mu+rcpXa}$_04XiNc}4pj!^CzURfy}_d=s+|6P3po#*eri*<4_i*jY)PttYaymGFb+7)+{*1vZ31m#+WCLNdkd`Pqp9<@iR=Pw16v+lFy>*CsG(a)_?X`QRr7gFxp|3bdBo^MW~TtCwyt#j9}zM`M>=XOhVaQkd89XI+wJ=N2FjTonUn#g|+md3BQ3lw=ozYS79_lkXo{quvR=6PYB*&=`ZM6x+|bzVuiHoVVfX&$>@q&l+mbxw2c7(c4mZhp1#!zfp-b(HpD$Ali@`bib*==Qu!=t8;fbyb>QWy@9CcU&dk$ot-|TB^J1dqCQ6m6Ba_-MY3vDb<tJ9j5tUg;(Y4qG^oCHLs1*e0@5D_9>>Gl&%Z?_^-K?XH=|{>UQFDkvC^-lCGmOkBHpwk)2XMUI|%tb#ru&6M37}sGBDGe{d}2`ue+cbA8l@dy71$SDjP`$E97=&!wBvb;NqF7x`CTN%ho+9m$}2T;C|w(;4VT`;K$WLvlUqzuZaQdBt`q|7;@dN9;ngR8Qx%iPVnuZzruohkHPpT|Jc!HQT6u-*%JMA@iz9rGMWST`OI8J(4MR9xs&EmEP-<t@OQfo>Kjtzr<e}$@{PKlj_-;TkF}HTaVkCJM@24+P1guOUT*s^b*^C-upS*w!L?s9k%(^P3!E=i~ac4X50LyHTHFg-z2TK+wCpulO=q%)!(L`Y{lwSf4lm>UP8IGZu)|fZT>d%tA@Rh=5MneTo+v#)X%T^^8MAt3zR#$jgt0f^@3+6wNE)E*YjJIa@PNpR8Q^1Ci>lSCbh`-X@9#+x%E0yk2<paZPtl)_*u$XWn1a~%5_K+x#han4kd})x({r8ESGZYzL9uL<ko#=4a>8un;w@W@_tWGlj^)MDWB>ey7*o5I34pZQ_i-`eqTD@smBT_&ncJcua3K1MCY^jmQ**Fw<q0aINs<k)j{+2qTIUw>pe$MZvDMbdyXl#t<UwzrF1@){a?FUB=XSdIa2>u8YtHXL`v&H{powkt-ov9<y(|%znquq;QYa-jM~5CCfDuaDv=*sEB~H;7ms|)6si6fGDY4u{7tESOHrBKI9=zPC|3#=?2^WF?kwe6b)<B@%C|Sm?8fhK1?;u!pPgB{*Y<qBT1C0*rmu8d^>h*C&RKh;oSm+q+>ta#9{-m$l(V_Zq;YD^pNiaipL6O*+wtf}^U5jjyjtqVb@+I>-EozVJ5*5rfj8v!ynj`NU3<2FE#-Rn7I~cec2lmjYc8|Pt^F&FO``u!56Js~{t4yQ`&+H9LnZZNxqrT$Th_l)J(+T~>rQE$YDIjd?fLF$TSd9$zTH*asmkuUb`<xdTw8WX+E-c8la#wchD*<b&ceZ>AIo!uqtKsn_3f1fQhf@hQ0~0ZUV0u>^5=<u^c;D9^P;Nk&P&gWrCizYM5bM?7yRaw>YTS!<bQuT+b(w$za_0_W%qH>zva2fl`^e{`msF!Dk-6qvoGhyn(Lr!%A{Odm@cgcWn+ctXLDYIbiT>gYV79Sk=%}s=j=95z7JXFLpckMl%5BjiStBmeQ%KX8s+NQrSkeuNEYoa?;q6oOp%{BD)0Y`PS?@-k6+bjm$PmsrSno2ofY}WvC{Zmu`MFc9bImh>sLC;_ffImi~Rl@(({@Udqw0uBC@3Q9D7al|F3-cI*qv{a?AUi+j(eyyg65+eQ2N3!nR@F#d{=I)Bwt@@12}cgT=mPeoqx7y?xtyvVLCpJ&bX+XI<Ic5YwwS9`aAC+rN5?82I14dK)zG|9$o5G{&&aPyu`knEN|m?#W>8Z-NWJ>*1@x+}DA*zXj&L5zKuPcs+PC{5>%DRB$Se$2r(gfT0&5&VPY8KL_^%^Y$+riiXbvM}wo_bHUuFgQMYbhN=whHS|8jxztdNp%O#2@KSIo+SEdv>)=)3I&i(A26zR$3S5QbRY086;BnwI@N$TABs>Zn37!F;4xWxW&44&hg8P9df&C%QkHdYzkAv@qIJY-+m!WosI>Ot7JA(VbeZhUeBjJ8vKg{b$i1S2<^Gonxa4_cYC5ZDvcpP{kcm@1@@Cxt_cqzCPbIkb<jK5wN=hO~-H@vT@4t-G@?uw~aim9FoYRo;*RP#X03HO<%Ihu+2<o>E@emO6PzrpUT2hM45jon!@oGaj&;0Cx3aju4Ef<H2J&`=o@pALrH3_WeAm!ZM%A>hH_G4Qcq?o+^Hz%LjYZRmMJL53#7XF;52L!4Fk^Wf*vhYFtpUS=r5&{Fsk@KW$vcoH}Po()d|XTTHTN#I2AV)zp9VsJP-0vrwwfvaE@V-A5hPlb;KPX&*I4*`z@4~6#v4+ZyzIJ-lfJ(yUxd`;gA_W<7u?gVk}3~}xPalQ}Y+zsOVM~HJzh_eIY><#Y)_69!!aefTq{AY;sAo$bZLEusF(O~XD;MTP@3gY~Xp#kvz5a*{L&ix?HPePoZVB#9*uE3uGE8sx*WN;vOCVUpVb4_!94L%F}8hAc@Hh4aG0bB)hj{tLD23`Pu9pbzOo&e^a4PFC&8{)hH;`}bec`L+uJH+_|h;uG{514y7I2W7`an6G{7ebs1;FavoJqhOzA<j7v=iLzJEQs?ih;t^yneTNvyb)drZUpaxmxK3#o8WuEP2m0TY;fzI!ubF^9i9PB2gkz`!SUcl@WtRo;4pYNI1Ky>JOs>rD)<%fH2661H1K%%Q1E#0FnDk9Fz};rcQE(1;77rKf;fA^+km;dfw^}8dx8hTeZT|3BjCfqBft~j&w?j_L*aA4++)F^;28KSa13}Qd?$D%I0aq?P5~Fg4}uS3?u#MLMeua+LxvtU^dQ8!2gLaSh;w&C_Z#vu#2-z90^HhkZTp}8i@=?a#tSU{hXLz1<;NTIH&+^c-G0~!3h>~+A;#pjp_?pk2mkBev^1lN'

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
