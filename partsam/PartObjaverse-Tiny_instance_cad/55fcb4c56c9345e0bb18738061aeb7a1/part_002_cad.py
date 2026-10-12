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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/55fcb4c56c9345e0bb18738061aeb7a1/part_002.stl', 'relative_path': '55fcb4c56c9345e0bb18738061aeb7a1/part_002.stl', 'source_sha256': 'f04f535ea0496e21b4ed6366ff838192bbd8be07f53a4a0b30696f65fdf130f4', 'input_faces': 358, 'input_vertices': 321, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0404629185795784, 0.03427969664335251, 0.006088804453611374], [-0.00806046836078167, 0.11721283197402954, 0.31119996309280396]]}
GEOMETRY_BASE85 = 'c$}r133yId8pqFvY7@k+ma0!Jp+XQ5V*4;vV{25^q-7-1sI63}t)sq%si|qvp|w@TQiKvDC6@A0yO4;s=q9wZsx75sjIDFtd;aJ4-uE8QGtZ29-ueH(-#y>C=f3AX=bnTnbT3|_l2CtYi}RVox6OZ82#V68k{FkoHg;%A>X;@YU!3R@<t$Erw9e_(w`W44PmB{UM?RN2CM7L0-XGa^aI45Df8^j%X=BrpM-Cj7_FO9QF3BUtq)I+!Nb-xR@^gcj=FOt~F%6^qll}kWpKv*Zz|1Wxc1aCYt+ufPeO@>(yMuuzt*d<4$%8{LW;=N>X1&D&;_?QIi=}xcUNpATF%u7ky<bQwUdyz&*i*&2ugL9}YvM_P3;8A<n)CPxQvZ@pYWy=lU2nD9dLiA(gZ;1PIJr1oQSm$H6@P!jang)NWi4LR<GSkS^1%g0KCpeJk-xoly@?l{ZnV+F1I@#8jQt$FxW&YS^WWHR<Vg*78SlFycDIq2ti9jF{e^oEn0V5$o`;Pb^X}mposSvs+bt{KIR3)A1;+gRIM&F61sjd?724aU(8y75o;+8JI$>=8c^@MWWdGpec73uu*qr6TuG@I`_-)R{Z*w;O;H?R2y*xB)s;hm|>DeZ3uU|G!o3n9h&c|tUHcp$fafViYlVe&(HfQU|=4>5l&exIMo~;+n`FgQATQ7G1Y`xf=tryMtdeNM(7n`&E+nnWJ^Lyr#)vev0)ve~dZuP#$*Q4fqJ!;O^qvpCE0)6)`C+`2Imo-np%BQnUJZX5#!^ZaULkpZd)OBOFslDd9eQ4D##as7Q>*ZqgToW%^w?E&+1Bc^IxH$Uv^aJkc2VD0PY`bu|Yn`J0JskD#;i!Mkb^UX$>)gXp=bnC0=N^ta=Umshr+?H5=eiC#*LA45y<f5X*qr6Z<}5#&^ZaPe^J8<CAG;rxADgrMXwLIv_s{a9InR&gIzNGdcQUNH`gXfocSGtGn7BxPN!9<x8y3%)+%3ymFW7%L*ZpvQuYUCYqq$w5^RG^Ga(iAF*W={l(cC|7gIY(I4p}^~z2t}VIb-?~>ztUeXQ~>{OKr29^TN5k4>PX!)j;Jb>b~FaaqaV*>wY-b{e+&M<l^@GW#9-k{)2HU&kLSZ`{AbNRr?P6T>F2hM2d^+I^<l}o2PwQbzbFM*Oge4sOF_cOqTP$!P`%%{JhX4%T@o3+jYL6oyGk(Z>sZB)a&U^9$NOLs>6nJ*Sk1-?{gkHl#=P>{Cuu?(Ye{ydtH<t=IY;nt(~<m2cPZd;^KpeTdnqUu1qj;HXhAG1M)LXJg{@5Iv4-gN{zpBp6h)oUazh4wxxzzFZ#Un#X~M`pL00Z=N!iEa}MMB=LP>OU6xq+>5{(I8u!{Xb>CID-m~&qubaiicYdo5i=J-uuEp<9RzF`QcARA5!MVE@n0V;WuPQ$iIxe#AJ8k+3i|0+sHSu7eW5^m$mGKKKUMFgqvmXyXH7nP|1KV1f`&k%K;N<@5gRJ|CeX)z2T%^od>8vXc=j}6nJ6-Lg%UL{QX76RL`C{CjFW$cT6WJyn7~f*EiTmfS*=_7!pFeqfz3=h%jR)kJc*e53N1fcBuZ!J|J9*NzpFeW07Z2C<%sI=C<~%=|2S$96ZQ{W*XSbPn=$BzTjrYC1GGx5(yp(+=?tks(eiP3)I_ikApM<k{CZ2SqQoeCKT~`zs`Q|ppJclkXHghq$(3qbqrPO&o;?#U=o#u~K^EhnlaVIZY6J@=h#F^SJTlsGFrs5NQ*8GWn?X5ab`f94hlh*dNc&P0itDj){B#VoznC;Gb&^%E8x9!e;iXum=emXy>*5jo`nMPi_nmQNl=x*`Q_~B}wk4h_aa{siT#r+@M+~DHa|NW)#`=sPfYMj`&i&Ag6xIgcNRZpR*i}Cx9)~bDa*-U5sYhE;Eq8d+XO=~><52Drc*1ECUYF~5PHYX3}-Bx@|odYKBe_{Di7yl$Y)0s~X$NKVctS`>>`r<s$V9*vPFZw*)`W$LD*?QhU@A`_D|9H8xf6jIPoa=qe!y_)`ns~5QSjfcnzUR3w_B~H~eNN-;vF~xN_dU%+*@f1;*yn2S;NG7tUi6n&_PP2QeNFL;&0PK4b%^=pocC{^TTpKv-t>DT7ri<ZI=Qa%q@SKSYT_BCPv)C=;F;3LjlA0`BM(g}=DM#x`jS=mf#Wq@_27@Ws@7LrfvcZj(RGW9-lqyoJP;i1YH#l+SQj47>Qi%GpPK9U3+MX%!nuCGc<zh$i|4+0zi_VKFP!W5i>DvFUpUwA7teU`e(`X;Up&u+_lt+){o=_F-Y;U`!Fg8we|yKuS8(+XwcjKzpXcfa=lRfuuivrwj1)ERIA>}u&Zeq5!8uU#jJP4Hf1E$XBO~ToT%V)PJ-o)m_4$)?eg5>c?-y3!<e>^nUFSN^bzOPd<6OtN-VZs~`<thK>~Eg-*xx+uvA=Py_czV$bKSz=A`|EN<mY)$KP;bidzMcTcG7j8^l+R{?C~GXRp)U0zM6ABe!Xwozi05J2Q6OX&81d;dfdu)a$YB#>*uojVfDbdt_RNbymPMS-P4c$xt_PjynEVX-Z|Iv?ir8%Jr6jaFS|X<zs>KFXM3OFyx9TQ&kG)o^NfeHJZsMLthwILIoJC+=XyW)+!y<~=f2p_IoJC+=XyW)^n?AJbG@H?#)JLb!?B-xo(ucAhhsnY<Oln?=JwAcH17$nztuk8@4&}h%gYhT2osgW;AF>NX%n=D3pM|h_Rtpp-Ct?Pw)%hnN;^f4p_Po*&~fmjqu{H`m?Gmr=umiyDl#5}_Je;6{&8puJhiC|M*1{-9~pn75{LGHuOOp5u9wF(@;=<781!-Ynlv3U>Os4}myl6cMsa8z_-c5zy3jiC56I{)<34C4d{sPi9q425^emO|JfwXcz9K%8J_X+o*HaMW2SNM74}wpIJ_Vl)p9Jj#-v>EM!o4csdIek~Uq;YBvk)Qy`UE^_0~yak8^TkYFkBDAHS*8MNR%-cnhO7jpz>GOYvUUEKgsAO<2h(g_!=^*<9c;mBVQ78EuepZzaMQ%K<mQO9M>0W{%gY1zZj_njfB>RPsF^YLVLl}nEkl!$F)Q}_Y24i=}36WNjk2l<C@N6f8^>3_yp(x_yqXgGM<F~89D&Itc(a;k8rfzAmdjVS<q|n+hzPFV;l4?e71~#$=C$F4xcOIwu~*%TkxCEW+U{U@atq0my7QM=r2O~k7W4d=N-5&je`~`=??fEXe01_`tDNb$MEZAT*ZB^;vVFi;5z~6Qut`c^>r8v`KCVAS2T1Td~=`5T{CDFd<&m?<{0Qk_*kFHT?^<Y_?9wqgu0%C{F0B8@u5)HNps-ieJa<j!KvM5Xe)RM@>`&-;alUo<lFkxe6|6jez!u~z_&pg^6fAOZK2!X+hac3LAS$q@Ts|M58VMzW4kHT*h&8l{~>%1>WcDk1DXS$gElwt47c#Cx6s#SjO#AOOnL`?D|{~WHvCf54AlT>W1sT#r2o5&cc3%iOUP^V&Mpbv1OK+v*KwV67d%~~Huph``IM)=-gbOfx1ERk=r$$M{($t;WgLY54gMhfA?O?M<z)OrsC7^J7W^T!`3ZU${wMfr(5vvXWXzUv96`QN#tG<K(An_KWK5OO96B2QGqgMD_&)jC^4Utscm!G+ei^>A9C{MI6s}Rb6;jLi6fcACF2}WHXx|iL>W?6=_rw7h+W_$9$a^u&11ZhDo|74vvl*Cc@|R@%Ama-3GW?IY_A~Sf{COGQqAlq~hyMnjNxz4ue<%2wjA-aIcseJ%D%81vGz~r)ZJI*=3QuPYI%`#dj)89>V}guW=*#eQo*66DIfZlzd@S0uguVn%XQbgmy@yGM!PC2KB%Wg=o*^9Hq3^~){{l}nN_7+goeduWUj{l0p3anXwv2~Pf)B`eQAS7T^YB&h?3JOf!pGygZJ^`fJINR#qZD*9JiX)TUEdzs4!((u#xmMMJHto8H-;~T&vbU_iLv#>xXBO3Jvu<!!#|6hMnl8l`{P<uXf%A1P-nSVXbbpcTx$u9g&%}#anP3Vj|z1*j)%5}Z-i@Ypz-kZj9u}ZU6IF97()+?gER&{1@~?Rjf3AWBTvS6&<pUimS|1=2E7YU=d=+*ozX}q!qeKIHBu28gnwAB@o*WBLaRFbVxc~h?t^b6BT7aMXifM^GTxJIDns|ehsk(X`m)fK@D$|BL07?-m$6#<3eZe=3i1`9Yv3bfyf6I&&_(dn7xh^lx*DFoL*EUDE{4w#YTOTD{PaBJ7YH@(2Qhwn9`d`TKO$o;bPjwq<ZvzWMR_A%#izzKALFBO&d2>~;Qpjbgz_}kpJKjA&%@JPU&efs-hrQsF-(Ncbj&?zP3TPcY8Yd6=uU?}g3qM8;Ts@#4WZ%iXXLef)CXx1Jmu<h%s1&5@Raj2$om<zB~R=76`|HR>6`HP`&1n*L_JYmk*B#nh505u4POs)U*Gq8J&~`2TB!wn06r46)c{%%zCOMi39SHM7qwdtS`OZiTCWQ&3%?IJSqnV^ACgfZ)O;6U&dGl*;~a8x4mmx8XZ!@uNqQ9iOBrWnd<8uQ{}ue#&~xxBF&C?#U&60~r*)Fh-B+wq@q7KJ1;76Z`sn|i|Dgf@ru)}7&ToDu`?7zTlhFM>`Z-k;lmDXwQzGr$;y-wPcd7'

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
