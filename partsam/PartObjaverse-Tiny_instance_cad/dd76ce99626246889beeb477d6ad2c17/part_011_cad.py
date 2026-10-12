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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/dd76ce99626246889beeb477d6ad2c17/part_011.stl', 'relative_path': 'dd76ce99626246889beeb477d6ad2c17/part_011.stl', 'source_sha256': '6982fd576d8b02d26c2acc6b96bbbca8363693d486717d2851ef2b41bbb28560', 'input_faces': 186, 'input_vertices': 159, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.04376954957842827, -0.11477698385715485, -0.20210765302181244], [0.09908286482095718, -0.020191073417663574, -0.1398530751466751]]}
GEOMETRY_BASE85 = 'c$}q~3se?m8pnrFF%r|n3n@BSiWy$O3m_1KBr2#OiXes#A_!@MT&zTJyr-#HcuNC6?_y*kAfT0_f~ZToYl)^=j+$DXZfiHB-Q&*tJpZre+p~Mlo?Sf8dH>IEo_XH;JMVXlj&g40F7cn2RCRyKZ)uN8lCXA?yR;xBD<?fUC41n!%vYSG4#dTuy)2p#J3e}<le9p}^PZKGot))8LiP?$4e<7ny;C!?a<Y=<&B(}_l_GdV(%kG6lV_(TWu};ZKi^@2KJt*KeB^xjfBbVbo1p%Zw(o>!%ZX#vqSRV7){9ad-n3Vg%8ao`MQIBRKO;){#0cWjM|Bi$xLu%lEqVa+QM)QBJ~)fw)rx{WqSUj0IzsWzlZh+AU+gBnC%2sV)^90~wDb^hDW;g~y*Ps6jk>YKm9beAFR#4C?Yt7ci|Rk@OZoNT?i4Te4k0cbA4hrgk|^S~%uzPVbKR@T+D@&gKXIw^DavDW?a%Se6+7ttAA%^4RvydaP*+((@%0NU=sEf&-;I2W@}vD~%LLAob$vU%zxfK~SN3{wz0IA8t6g@~SjS&Us^3O=^B=9Yj=!?Mkokvu9piWU64x@5c^*#==Jt4}y-EH#e}_EA*zv^m>baCh>YG(Z{#-xe%J5j?Huw0`R0a&$O8lE1Jnz{PdA`1NC9W?tsK4^9Ri~_6d3S@uIIBBvZXsTw@;F5Q#O?PwzM1lTcGGb@XRlx$DN!Ev_Bx8!%bp{yoT;VtX55=e^(qC2Hc@|nY@~H!d$)w+{Z?+W)@xsH^4&z{>HR2Pu?5xheBIkfe%WKx9_@Qq&a>$<alO@DUT^JNxW6xMBrX*ObG`3Ha(q)b^IoC6uFBicIIHE`W>a2mU9ENe)u2Jdr3bmS*6~*c&6!TTDx}6b{%Y=>Y4kkYsm40~YGG|3%HPTBsCC@b2SHzbK<&I*WgRzd(9YOU(cYXPG@dH@tNvp`oZ#ArF1)YNU)!QlD#hQOQDN<uvak2PP})bC#nfJ(dFP0?*|?wh=>XbKT1?AX;-{O5t3SrQPu$}fUWdMI4p9E(k;LUA1vCz7{y^f|6JNbYaovBWc=?+k;;MX%xH9|CJTHwah}$xqnES8gc`vmwAN|2`8i&K7+^?>Oh#MRGaJ?M@>#SVq+l||qzJli^`4YDW^{NkUQ@r%iEpGqC*O^~8c$_`kl~Vrm^~Web*1ujpfVeFrjN*+x*pJ|b|1D~#)Hd5O{_=dvW2?M#lJcbwC9bM{DUXKrBNdJzuD!6E^62XlxWAw6;P^9fwBGdXJ@~xZxR2|tK7Ne*dy&_Jb0z2L^4&4(I#ixIOI+Vme$2WK?Oc)PaQv9IygrME93*}viR#s+-mkZE-SrlqV{@JPyz-4DF5hvZc(vh&lUA;EEu?t8;8)`6?$?PMITvcI>tE5zh)d(v*I3uT^nESIx3~~jKDkkE<@&bGw2zd`gS>tkFLJ$IqWQb<RU-Fy*{951Dycncb!X0B*7I%Rsat5@X|p{kk8#0|xO8F;ai#UooM&|)aeZ<l<(G;Ix!%;t9PfAcsCA!ep3^vf)mo1Cc<GdtYl*IW4$qrI>&m#8#JuP}?`xMbS|`S9X`E-x@uSxLu0)g&S0ZjyS?kp+-{$x|o$!6+bHL7}9aS9vm)5+0rHdT@Qv#1e^{hGv-anGK)UlkuJ7HfOrgjD#*hz7@*Xi8Qdp;m8Eea=YR7|6DMve0<=kbZ)b7se56mNW*%zVvS`rg`3{n|kB?n{|xCDV7?DE*wztB`u;=S%53W?NWK+;+(62=V4JI@gUo&6Hmr>_J>x^?=%=Uq~QsD<4c;X*2VE>%Laqh7z}*Z}xp^jEdp>m!{DDMc*=x>#dx@ymcwvQ`BY7lwZ4=O<ca-p3g(<M`O$qjz8DL=LYtpKELjWb=>r@{ghwZ@(J@_zoc_pX}&|_qa3_R+!k`L*1C@*j~}>SnMZ1^`^Yw{TLq27&V78pyD^OC>-Hex^7H9@Z;2bp-`SoMh%1w>Ra@7a?i*jh>!g(T(Xb|7S6@yiF8Lnd`_7k-@cbUh;5@kJ*w>-0eKxnJVm{v!Z(pN+NoQVR-Ytyor*cVe8V6(VY0kg?Yg#Ar{dai$-7hfDUqb6adn1+Vl~%e{65snI-J{ja`wb3!bqL?5;^R5bjSkFxe%s=(p0{>o?&?DGqU^4vJbFnk^CDNeU#s1UdEM^$nEAQQw9e&$mpFdfRpy&7mlAI;pS5!B@JPNF_b8(F=o1E3QT+4Q_}<+soAPKmBboo0NBvUDeRzLuo5Fm7*FlQ^d_AwjS+j|24ZoC8eD_AmV;lG~$2U3iec7u&fA`nqF?acd@7=g37=>4=tov8}tcxSZ`qWyAdEVb>dzAb8HP7$8S9u(2dN3cbhJTk_R=B@^>dSom=QKXr%qGgCy6z^f<t?Uu=}YSPzTMKm@qd3|m%})xH8Bs3<@FQzIOUhGcC03TzaQl{{(6(gzt0Hf8`e@DW9k?lw<RIWzX+r8mv6k!@lS7M9__~MxzotMYxG*?yKd4rYbO`;`SbB<=AHa#zVyZ%YNyeBnfao@2guK>!uk0P^Me`h(ECGP<nMk*rG|KLF6A-4yTScE8$nzf?Yp0NZXC~JVjA(^zf+g`^LN}mgY#Sq<L~mM?fjkk+iK3^?ZNG@isJEq{6mh9nt7P=+kdaknN&->Z3A&F=50q_6mf{!(dH3eZv~0OwMBk(50?r&8%{(!{7P>*e>gATVM!A9u=y)JHOcZ5T|n_?FaP~d^z@<s-B0v@;s5VX^f%2myk*)}(@LQ2tk|^e;Kg9CoA#P%o5WHR+rqRh(4t%i6M7>|=xyM_UypJd^a?y%4ZXqQuS3jglxs{|0$=FG&`Y3Kz+Vad3iJkxFUke56?ktI;ub=0u=p$S-f}z>Y^`a9@R!411-1eDRdDe<AHH3S@+H`E<kS$84=u_(n9y0Ue7u(je~xK6@P%Fkodc~|eDQoXO7ZRtXi-kLJQMn5yfY7ak;TtJtmxln^t%vR^uGvtE&5ahE#^?n`x~aEn)ZTexuzvTr(&$d+$6z-Rxw86*-W%S)SqnHAkzk#_B_f&=w+rAn6}ikha~=MW11^UXN&)^#dks}LAxPFJZ}YG=trOhYYSiK)~2~YyWpA7k0M^gJ#Jceu<qbOd!VlFDBYlYp%m{u0bhm*-4oUeF&#~7k9?irdw{irZihOAc1N7h9iRn!48A+Y$QAFUnKsL`kuafyP^Lf!K|cc%I^48$(_Vy5fgcVNJQ61K6qwMNrp3b-ItG3=EFOG5o(Yx#E!bS>477hFm?+0Wk422o-lp|2tt(9E&M5mrcZTkQvLAF8=x#8fJyG_D_JsB^tv7t3pM)>;0Qf?CK@0XYe4%?l3-%QJr_uf%U|pdF8*kbe(<VTRa*}D$@TbDYgU8~TVAJ5+^;FEqRK!lfJWPY0gt?r8@>$IDXy{1PKN@-x{7A%!Z|yUP4FwA^Z5aG#;fKNm4}=cHyMhgY9|-La?T;A2eBq07Ftk7PaA;8m;T?Zy!2+Z|*1XX6eKAVnH5CRu63>I7gYnF+N5Bt*7Viv&wm(<EM?puSjDU`Uo``ZBv?!m0o(LTW6FLFqWa!D5>jYRV<~0GOnCBSy@yL?^7KJ)u(EljtiHM6q`=jvO5B&_rc>7_T0-%F2&V#|CqnsXccm7ZRHS))wCJu0i|0wy_Hyy8Q);IT=xqiRAMMt%!Z^A?7KXI6Nh?7$KCyd)6-~'

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
