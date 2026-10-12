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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_001.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_001.stl', 'source_sha256': '472623f0af6fa691f88e92dbe79d817ff0b7cfcd6cb33561d9f1e5fbc40fd8cd', 'input_faces': 245, 'input_vertices': 175, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15656976401805878, -0.20435015857219696, 0.15822651982307434], [-0.15562456846237183, -0.20307011902332306, 0.1595349907875061]]}
GEOMETRY_BASE85 = 'c$}@7d2m(b8OFaX1cPjn1c87az$C~fiy&Zx6OaT931LZ4w%iB_gdj_ZC}HuaNR(ZXvQ+S3BBF>&)gn`uL!pb-R{f)OY_*=Lb=)bGMg<Kv_ddUao=!W{>GaOrd44?e@}BR!-}`>&a4E`9NK7^QbT=P$&iv@(_QpiNtxc*~US3^OIj4MC|3yny#F_RnKl%xDTVZiQ(M@q?xmlStw|v>0>Z}n~R(8d(tiD!O#p3Fk>as<pi>v3BNB!Kgh0DsD{blpZmXtUDx!1sJhV-=tU)k4MZT*j*R?SO@)V4bDO0zo4TD}%lQ#SU*sAjR>PLBCje5;u6{Vgx%oAVdNe6y!@%(v=qi22Uf^1YgP#Xmb*dGO7r2{GS!XH3kG{E_(8EtF?~u501DL*o?xc23Oq>gC%#jr?Kq-5v5H*;>E%Qm)oBQNC61-K#PGU0eP@`A$l*@~j#c^Zk!oYMmq7sSdXmC_ldS-1%4@`-JjX`-yL&KBcOISt8$_Onjr_Bd3#eUw>EKys`<(^FIDy#XFVU?<4ZfJD0@b?I}fC|9ax{l9cCV?Tf!wzOz*I^fKgoYm!3s3GUackZ*a3ia$c#BJ#b77pV^A<F)?LNum2P-L=2YQ2c(%<J2mTeFfLORdqHCRUfMp{>N>#@2d*spKPH#zfhl8^OeWEDc?Cno$t?A{$29Ty^8nNDc;}MBD7y_JN27YDc}3*;#j=@hU#wylYcSSeN%Z{OTIfVRrfV;isIAB|L68G-+f5?;{G*J>mS`l@tNG$>xrR0baJlO`n|-^`kfoJUy(fd{!Z1$zI&psJ328`ANLc*J7*KL{$F*7`H|z36^|dxi@jI#W!{kQ{zUuY&r=<|-{E&rog+u+&*Sp_62*H1<oiFDZ?-GmO3}Rd&m@HUA#zClW)8}av{4?rgYwu7tUq1*5~))jZ!dX1&^+3otIpm=^1MrbwpN~qL!Rf@-<GPsQzPGducPXmT%tTP@Q)~u-AQ?zBJvb4r@NKM&!9esx$bq;AtfPnUYSAcW8eq#K73-x59ZE1#C&}cA6k!9Lw(+s@Al&yDAxW)-jeU{P`{b?mESr_{9g5~_uf?H*%u$Gn|qvnUnSojqkeO?s?Me=K6IW0=e##LKD3Wc2Ipjt_|RPYIg_+b{NTCZe9C#7%sR`}xAx1LFXw!m;)8zMML!&q?{1<W&M3eABJsg__-maHPJLXc&+RVS$H*S})|H*L&KGY~o_X@^S?Uw-L-mO}L%x%#dG{Jre`^dr^I{#MPkPIbY)DajYO&%w$AzAQ-Z9nFH*w+Tm!X~~jq<;u>slq$=PxEacN6HVyX0HB>XXPfiuYHV@O+)-Jjs>s(I<8(b1~M0&VM_f`${8^M;|_@zH$PexeLxiC)tFa@AhHlwCTI!v2~ulRO|UY^?zP|Fn3m=_SZZu-y5H<`b?UkbsiwTm-@$aSDl?T@-IAh4p5&6{<bu&XU8<fPbEKd>YSyovgO-rmEYN?{QjBq$A36?{uAm4{|ouSK1PmGw?D~uf2%xR8g)J*|H5-Ek$KrAKbXf0`@V_%73y2tov!#h$$y@8E+u~r`77z?XH;jCPaftp=o7au*X^mkH9u1x6HlIC?$~$l%O=%<=V_#j=gu$X2k%#rW9o;9htC`Z`(+)FZx8RL^*=pJ`M1kA>FN{b;7zLM7V<C`!M?b+HHGTnb=3a)<?@5M@Y-=-)8%{Yi`!oDZUOn}bEiu2PF_=}AN<eAlhYLHL;pGIKZJPR2ZHm>?nZn=7y0%~#lQHi>Ul`_>(#Npd*ui3na-=Kvt3I(?+IR8`oHlT-B(&C<sYtjaegB|c%J$bxUZw~{Ue$$=lNMYFXTHPUZy_$L#fueTz>FebKX)vm^}Grimq#3=eqrg=lSKWVeTG3r~FmK_n*o6EI)WISP!Ugtupy$b64d#Gh6E{J{Rg|b4>ST_c<3@k5xsTdlS$3Y&NN{yf@G4y1{u^srvh`oekB~S*<+we)&$JCI4ud{LRF(kN)hLAwM{OJWKVlmYfaEsr#&ad%@XI|GVkR<BpOaynjaasy<G4`F^J6$UCR~va-Kce%=rL65W?clJDP3{E3L_@X}Yxzo@(NPno0jO#3QSAMX_Ba9jD#W6bX))xq2HrTUHMsb5N8<;nNBuGyz}_v=PocVrL6*Uwd+&l^L}3#&o<?*6nfbiYCUBejj8b24&Rb+AhsL;d4!R=hQ=F*J`(9d+o_7@7+=vyAtme<=P1*4a?5JSk^%-4Ep3B^A1E)9FyW{Q~}g)1muyUXyPQp9<H1lYHmksn9&S19V-d?o_A`y(HqFIjQwz^wM>ESE+8fUua)WW-0&9D&A*4mp@Uy(?I;opDDl9Q}_E+rPleRe7i7H`&g`a=T7_&uh4p)UT|VmQRr8aFV`+v{q4oZM8C-<)l`)I;3tx(8T|zM?|&kxy!yZTiDb~#|Bs(YOkDG~72hbgLF3^za69y3xE<UDy#($8_dvVDJ>XvG)o?F(Bzglp63$0w!ujxYbO}5io`>EE&x32xO>iyjpg)2gxDNd>TnBGMAAz^Q+xbSh9(^2+>JxB1+<+d08{kLLL-3>Ue)K7LKYRdv5{~L)@Bw%q>cacr`}szBE4mln3U5Ilg15jM&|UBbcs;rUUJtKBAB5MzYtaYbweTJ2z3?6IYV<C6HM{~{1+Rc_K^MWdz~$&1xE!91-UQEvOVEjM30#C;4;R7X&|&a6I0wBF&VfguSHL6S{^(_Je>e-h6wZP((DrZ!Y@uyo3+{%thP%P(Xfm7*cS2jjo!~Sy2~LAk&;&RI?tmu39pF^71)K_ZL@$Cn!ky7paA&wH+6L|lUyineFNb@gUErQ@CfWnega@L%;DK;9Iug!?$D;Z0Shx_K4j013=sdU>E=6nMQn(Uz;7WKYS_dzMSEAeCmGByLJG=(In{SkNqV;f88{nPrZuC)jH@pYk5AT5=Mi0PI-3LDmZ$|HjH^aB`jq+{iR`@pfc61ATJG>m-056AY(DiT)T#c@StKr4yT6i(M5WNFl2roca!wcXFbOl@i-;CY@-wa34aySCdKxe}<;2Y5r_(pgtS_DspC!^!w$#4Oh0~f&K(Gl=?I2Y{?=fb1WEO<0L3eA8=!PlY|d@Xzp+6}%29)hOBL*PMZCwLHi6`BTL1@}c$;J$Egv;*85?t`Ynec*m*N4Ot60PPG9fCr;p;lc1w^m2G8JRI!_4~MTqGvVuC8yyJS@E9~39s}p0W8pk_0$K=9fG45F@FaK&S_)5rr=gYbG<X)e6rKf_p)27scrLmIo(s=M?}q2YReYm-54sbM>TdWR_&#(Gd>_0KeHf1FW_TmKtod7%9~YmR@SpyB_4|(#eHjn^XY0TI&G0`te)u;tn_s{$`~##YzeV&p-24(BuOddL!u%7d)wi?'

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
