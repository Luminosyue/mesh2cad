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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a45db53fa2fc4e94955e59aed66aa0c3/part_006.stl', 'relative_path': 'a45db53fa2fc4e94955e59aed66aa0c3/part_006.stl', 'source_sha256': 'c1ac79db0a6533824d1e0c3899f2700c03a6e5ad6699bcda249d6e215db87ea4', 'input_faces': 192, 'input_vertices': 149, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16676513850688934, -0.4481455981731415, -0.2848559021949768], [0.16679911315441132, 0.49500712752342224, 0.19462409615516663]]}
GEOMETRY_BASE85 = 'c$}q~dsJ0b9>))$;*%`j3Em@Wh@vJ^q9FIE`3g)bG0D<{0*aa--~$ajNSKswlE_gz+5;TlFS_D`<BQBkPFiYW)0tY<FpW8lj{m5wIs3Q2=eF;OS!>qJUF*BPAHH|reSUlI^VnyR7$4B6t;9cFr6n869$OeBNlY!Jw$l8x?A(lLX*qr8Waaruttn?8+e@EI8k?BxC(V}@hoz?FOv?@%EQiIWM~6koVd<IKx!EamretQPrm=iv%IuspE6<scl9gut-Lrqxpa^+Dc!ZoU|Bs*MRtf6riKlBUSALSOFgN_mJ<QEkZpzgMtLm8RF4qY+^A1BOH|EA%rFNSS?qInV_Y~z?kE*Z9Z?8Pga_NQsl*`3eD3?m>w~M({y7m$sf7Le!S#C_~$LlHczee8|dJfkJx!(K6Wy-5E_KUf8v)~K*{`OYtUrX!5`}yGn9ar~Mczp7Km0wan4`YwAT+ZxGxmo)jjaPj>$s^{*;Zho}wEvtT=30wH%C%mvQhO;coYz@CfO36G$$MgM43DNdm1XVTWx2Yd2cPG~*Qie8)~0eX*OqOjew3@J2WTG4y74+^?z%zkV|q|OcCI8BP_9+aUoPgx>_wDIO($#-bA81}G+ynr^r6_l@`tUIOR-HSin-eDP0EcP_sV?wFTX_fE1&2e(ckZP<?CBi!TX6Ce^AT~99QnS^thO7`!`Xp$PtxpAva4e^ZDuX^8vBFj^j!(2j=<Yo4(-f1Kc$}^&C=ZK8<hvD#TnV9>~`>_<TP7ew&Nuqh90ZXG&Ftm}@N;&^k(MhAyM;Tg9BD{@NE_q;_W__tQEa=|H(+cBkB^>r1&2(ui{P#;&V0kL7WvsK1Z@dV=!0AHJsZrm&dKfAh1QluLIXr}NfWG>rPu?hc{cbf5i-+FuAdN9`I1o)GJi`bSh#`=VRN#d?%LKg!iV-lSa49dLvCIn`-5)iG%Oaq+n3>YIny_xgrHpMH#I;`g!KyqIgy{Fq(%_0{D?%GK|)46(hQzn@=Ux8_i8>Ic50d8u#lC+aUGjrU{M|Brvtb*E0aN9$?c;q@pRH&SjK*v<2E$G)L)N|!g#_v?Q=Cf1|fp24rvgu6$nU%UQ``88Be|L`L|^^g1P81*+RgmO7<(=}=rw1%HgNk7y2=z->SmMiD~LjCHIcdDtL#PwIGzQ}jaQ~OnU)#A96^zTp6@3zdNTp#YH`ptX4?4jdLI(SGNubDNHx4(LU?$he9`!sJ#^B8_#`8>)aj!VB2ev;~){@o|^_vpGm(|DF&Uq|D<bFzy1!Fbg@8|gl8`WNpL>(q~CeM<AzD}SHZzfv)ja-}|$x36>Ybvdoq(s4IE*dw-=j?O+!dGP(+;&G+$BQ!2GfAmhuFO8-1Us;}4OUK{!!48^_I|X%=f9Rt1)@HS*+)VCE*O78)?*-~_Oy}*?KKMJDPxa7QUdO=tZPb3-Sbn{XdPwsofBLYJjvKk_TgqGhO4qd>Q~7~74@R5yXWT+=)Q3_o2c}Z4B+R8;zarDP^ynIzAM-2MR<XV2$)x#FuLp0T`MMdx=Pi3T&5u6y<LP3qhurna<-Y~<dCTi`#;3i!gs;oodY{}ruA1nnZ74TVJ=9+9)%~Yq?E8PsrTJ0X#?bxGn}^Kd^IY!wT+G#(Wwc)AmbzM>_GhbUy|l8D8ZkHPU34BAjh558C^MCf?gr*TNg27>-N3xb6}h^*fq7QTwo~q0FFSXxm$v=ZHg^N(gL>4p-QB?XBR6S7`<>sNZ`~>>cb=c-{9h?|p661>5j))toagd84|cg5xL%~9%02D|t}peZ|6Z}Z_j=sZWUn|6_Vuf;9CJ{t$G+a>8P!!{Ki>Ps#veUmt|jlI`pv=jJ!1df`&iuqdY=65KBoObxfx&Pb3atJ{{1kuciuleosZD*9rs(UR_5o0<9Y4P9nWh!cRsK6BcYT#_fdB4+(+5Db01~r&V7!zy<?wa=gxhX_qdLImz_KJMRxAok9o)C*e`kOaqQE)^*HuX-rTW|@{ZTBk23dl=k+-Dv3Bm<#~SbV#Bm+_<g#A8y>nlU+_`^NRz&deI`-{$?%e;|xpP0SE$z$OJKhWI-1**N=g#*IW8ss$ALsiEa_9Swlo`pNhmQ9nIW3C!?|7e*<6?RJj`uG$Dvr;;<9$utk<9B6-|rHA-deL-l=Rb@S%<LH%zA50PZ3^OS;#)NH~h+)5%u4_vJQ&;e_vULSv3r{G}O{_@Zs>m;Njp{cz<v#I1(NXjs!<QjKd(t-Qc~z-N4=9{lMM9eIUktA;wYgr@&F*r{Qtnr@;#R8L$E#VQG@3=PiwgCxXX=$H7N{N8q>PAjV_i!@$EZk7FUm3Bp__z+V6-fM0|dPlmq=o(#@_PX{x94V(d<0iO+?0Zxa{0yCcpW}XU82fqTJ1fGO>c?Dve1Rn<;hcPF?6Tk@=TM~RSI0-xjo&nB4-BaM{;B*|DabruZEH#H1x3uJEDZo+-OTm^pT6z>>?1C7}5aSR_tu1x1)EQ#j7GnGu#JCN_xIMfzxHbA~4>4{B?+9)O?gS48KMwB#4+eJuH-SG2ZUVMHj052=a3HuVTn2XqhgxcC=@Cmo@KA6l+62Kv!1jCvL5v&0JA*r89U4K5o52IX0a&+Y@K)evV1IaHaAVZ!4-Wzd;TVhyEWKfA34AG-c{X?nShKXuQi-K?@HOCd;9__YxCp;1hG&D{gy+Ju!MWfZ_)>5Vcm@0o@Cxud5aU(w0`Mwup`|?dLU;kV0OMQ;F<u1Mz>C0(;YDEP`QXLi`4HoI5aR_9<JaLu;3CZ3>k#AR@Dgw-d@Z~LycYZxd>QyH@Y@jM)$n!T)!>!zVz9kVj7M4;Woe?NH25@#aWZ@qI2k+!VjKf8j)so}M}r4Kj0ZuCN5dzAM}uF27*7@In+h?`gc#3-7-zw!fwRDKAjT>1WN-@jW%wBI%iws3u^S!(c7q2%jC;eQ!M(vxzz2e#0QZ0x_k<4u_XIx)F&+XR4ITo17XA|WS?~miv1%zX-p{{nz<>Ie!*3srJxqN50pa|m@3v3;WtG*JcN3Tx-<aK}t(%iSUo3XVm;Mdp%CVp'

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
