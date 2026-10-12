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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/c209c30d7a1843918ea5df1c61d594a5/part_000.stl', 'relative_path': 'c209c30d7a1843918ea5df1c61d594a5/part_000.stl', 'source_sha256': '3d5316587a11f213105f632c0be81523ce749cf6377434dcd02a40ef1e82eb16', 'input_faces': 212, 'input_vertices': 235, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.31513264775276184, -0.5000002384185791, -0.2824544310569763], [0.31511276960372925, 0.49999934434890747, 0.2813758850097656]]}
GEOMETRY_BASE85 = 'c$}r033L|K6~`y+n-w8a7Oi13LBbj$RKa|r1vH>(K~zx5LTDmLLP9|nb$}u?vPz(VR!BjFmPH^Wki?iTVKXFwBt#ZL2}`lsb8u^WdRjd8zW4s`F>_~fPEY%B?)m@UZ|-|D-}~;&o0$+7+q7Azr9R!QjY&(cFYjboBHCG@)|}*w*{Mm%nf+&`&kM2IOD;ZI*FE*jxVYy-tU1<#@Ttj}Ng3e}g@q5FHY_|cEPPs8#_WuQnN!j-rX~wMDq%)uGV#omg!E);M+}aNjtq<H6B+he*#G!xLx&L7qi=mFX&~jqWueyLCAp=3JZ$~u7}0+Cg<8oI%RY7HdpPo~gjZ{1JMY>>sbAhGDD~qdPZo&$;9EOR`5ljkV|>He@pw4$8@5g_5p8>Mr_=KIa$<{0o&3%F70)Xxbmdo%tCu`5V!WK6WbpHMtNadQi`*RJgp|v1G!Jg*TO)brKE<y55mAb_*iz)o5By#4H_^3UEBB_02fO(n&u#8L9?kjjn0$6Tn)Cez=6_cx^J%JN|H{Z3KW=YtF2~c{n*GB?zkJPgzCGw$$%8K`ZdIv#4=+>sVWIU0{p!ubQE&DebGOO;4;yw~ey^BO2TJ|8ed~4Eo^|IYslC$bB;VV0uP?9KneF1mM=$v1YmWTfwdt!R|Ne)|lE3}+PG5fOADiX(8a2~5-@}n_on4h0<CE{<$PYBj@y+*e<i|(<D=WrlemorC*KjsJ9<Jx7A$y(t-3qgUk_ThQyZGVOWs)!7xzv~E9I;~@+{zkWu72N~m8E`sP2O^6zCAhZi0}BCv+?aoH;*`vGgy$iDaNPXJRJ3AUwYX$-@}n_&Dd~2wsoE79WC(X%OYg`$M5|-U!LFW{PJ*|Uk%lY+w6SjT%W(1^Yfi^ou6A@aafMSu4A{k`#PpMzmA!Fb{*54U&rj|lPaIB3x>0G!EnAVd|Tyv{I@w<7r;I1g3jmb0=Q>g0QY>ank&Vsj;{sf?^t80<JUYTf1licamPAmzFp8koi78c=Q;E3$DdW){%omh{ML`E^Ci7$mTR1W_o(`}2P|@p)9{?)WAYcf^1sN#`7$}t#aE<MNj~>#t!tcW`xD8d7Rq_EE`Ya<DwFL;1|N!X@L<>LY94;C=0S5SzHE=|cjKE{=Q!3GH9t1y$Be(ZTwQ-G>j_u>KFnLgv3bt%?MV|AUvp`xE5FAeHE->EEOq6#8>x6i^DI|>J?1k<&8NxF!F=v3U+l{N2J@LaCDFy-U0A91+oaAl4-+xZ3)MVp9=LbBn&(A<66ZL<3e11R0y+QooU3Y_gd1v})4x)63~tARXSli5BK1Sb6O+nZyg7Ih<F_j0^)=9Ic&%%{)=72!=KSWh?NU2++~ykRYw)g&PusOy>h>4&eEAN>J6w_V6BzQHd%vNITbxIJzhCOO^g}M*4}2`+5B^)}@u!Pie5gOSy9AC)zW-dI>o~iD=P}-Yw5o@M-iKU#0C<v{+jUb^o#b7sb@4Nb+l*W7PN@9l-SS<>e+T$7#%C6uQg!;(doG>^zSYfxnR)6udEZdiegm@=w>e)uS>0E3nSR7IZ{T)kH@AWlRGrTsT;j@S+*(yp;#dEg^ZGaWto{vW^=~+<f5Tb*8_w$Aa900@v-<b&9gMU3H=NbK;jI1*XZ3G5tAE3X`g30YCZE;6;jI1*XZ3H!XZ3G5tA8^NtAE2;{Tt5e-*8s{n)CYCoY%kMtp3gMv-&stZKTe5{RhTWD$dql&H4JPIbVMbXX~#SpRK<ppRK<ppRK<ppRK<ppRK<ppRK<ppRK<ppRK=!v-Q_-w*G3)*IzTAZ2irx!#M1I&v16Xr#ZjhGo0P;nQ_?tp2=tTdxo?7J;T}kp5g3%&v16X7l@r8>wrHG8qS^vJsi(#n)ByD4`<`^=R`9;drtIlwqO37Xs1rDmfP8TFb~IjEyLM+Fb~)7&2}%A+^VcTCwWniJ*9rUpb?(^*ImBj<bV%ctM=RPpXXiUb6(I0&u(NKj2}O)Qe6kxbFPQuIX4(TtHy7BJY2u$%&w^On|}}2`Io!M=dM8X=nKy8>){2BaC~16*YkPm0rgzh`)}^~<h-B}p54eeV*EJQTkMfTFRe&#LuWQcYb(^6mf(1WEui>l^?!w(I^@55g*|BS|N9EN3mrpeipQWM9lk5tLLZ0kMj`tA4Eh-SBNSp@K81b;-;AO;#ZRF3!QVr1ulSvykHVj&_=Ms-^b-6fv~NJK!=J_Wzd*l)|AOMr6rV${!C#>G810Y2gg-}d5&bTrkMO-HdWfGJ+7o^d#Q=(d(Eji}kv9O^-{E_q-3z(e_eNWft9?(jdtwaXTT-;JL}4jy1us4!6iuK_;VtBaKwCQUT48%DY_rg>HMY0LHa%ubY;TEe!k?k2rKpG2!8cG`rML{e0$+!`tI#VBe+KO{$ko0cZ9T5`b!gXN4B^LF;!j7G6$@<xKbE2`wztJL;Ug%*DEdIV!*@q}1a!E=N1!b<5?=S|2OR-_H^mr=j?hu?Pf&=zVvUA|!i)SLBUk8?4&MpwPUtUuUy6q*9)Lase?LVyd^qxi??7=U#a+-l;M-%{kDzzK$5D)@cnTr>FQ7k%7y2}OJjGOs1n4yQ{S*Zh`=AHmr=rh6=st%}KwI}0ehNhr#Y@mc_`MVdDBg$W!6zc`05lJN3i`e8=&yYu+KI>&eg;Jf#VgQM_!5djiVvWN;ZxA(F!Te5e+6ybU-;=1zod8>nhak=kxx+!Jp`YOynN^(`040Z?C7t3GTO<=6+V+<0mVG%Yw#N>-l13r{T=)~<ZOh#13!ymE=3yjSMaMT)>Ev7{uVwBIjf=T;oqWIO0g2U41N#A4vJmS?eHs+vj@5Z{x=khD3(CqfZs;3h2oFUKfo_R&Nk>4_-84~DV~EbL;D%9QfN8+M2ZO%LFk9@lPM-q9D^Q(e-YbGK##!>r8q?q4HfMg=uhEm;7>z`!Jme&hCT>i4Sy0k1pXxaN6^9WAHi2Zqu?vxE1}Ww`dEd3p5g_HBhcgUVq2ACoGQn@svO5t<v8Xl$M>poeD^BsuL|P|zmQ_SB_5BJZgThxw1vLy@UNmRGzWe*#T<%k=mv*RM_cF`ho6bI&{gnnQv90YJ?Og*pM|#2KRNsgw1w`5f8COQ8?rV-a~*y;+Cq0a{9?3)ZiSDF4QUeEw6Xtkar<M71>f}_FnCY*ZLYKDaT?3q^v1<Dm-iM;=%2Vq%o3}k^&iw#IfV'

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
