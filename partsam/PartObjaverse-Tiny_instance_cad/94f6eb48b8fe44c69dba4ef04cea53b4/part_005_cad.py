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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/94f6eb48b8fe44c69dba4ef04cea53b4/part_005.stl', 'relative_path': '94f6eb48b8fe44c69dba4ef04cea53b4/part_005.stl', 'source_sha256': 'e8a7b8630f943e20d98121d5538a56f332ec7999372fe15f6e1dac63767c5026', 'input_faces': 124, 'input_vertices': 144, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1168455183506012, -0.11633352935314178, -0.49999961256980896], [0.11699600517749786, 0.15959812700748444, 0.49974676966667175]]}
GEOMETRY_BASE85 = 'c$}q}4OCRe6~_m~f*%-K5h0QI3<gArAArWDMmBy%Q34V{%?A%*i6|(tD$>OIlv=SQ;UpA~4eEK3eAs|kR1j1STZ~abgNZRp6T>5kAf{L?pi$G<nLBswyPNGfJ?(P-=l=J{?981z^Jd@Mn5f?FK1{xbvx50m8XL$h*8t|j)>^YxrzKl$V^(D5xG`_w@WNOay<lF<A~&{{y&RlkwIyc-KcNIqPMs7SssyL5%vzn5v?6h3R*F^dnMvt3E9bVQNtssue&qOwh)^XwBve_i{Ex4GJOyoAM{OOC`onMT7tvVSex}aEwWo6{;Q!VD<d=c7!c|qkSFCC>bIV6NDn(Q?MiXwd#T^t;Nw51@@>bwVc55~Cli369E!!>uSF1N3fpKaA&qDk9GlxaAZ}55#KKJ9j7HEI07C0Mm?$2hfe)ukMeMemh;UBFBt{r&%Z8KL+WB|A93@tZv<HQTH{RgvlnYn&)o@~GD&3&Z*Q%}i!5?bFfbFCpn^7;v7r2U!B8sPqkB!B(m^T3Uu>x65c{894QfKrm@Cq=;3(L-o`&gB5NdyFCT)juCE$9*G;)JMB89JuCDw96&mbC}G_-h2br&mQMlLF##FujFgWX#TAWfU^q<$<y8%3tTH-M&@Pz`bo*%H@-vW)z))J#sPHQ+in2Yaw~R_e%d;Kvpa<(f4#jKxUud4Sr?=IJaBvbqhwxcN2MG$_BFCk^v)#U`leB2Uh1`2*?vYDsk8msY?<el&;CT}cKtD#=g}Tgf3>Tl%GEk*-RFU8yEQT|<A)H*cg=mD<oQp3;Fd8Fbf4V24cDzcr;X&v+&-^#b-n1ls(`cTJ3C2x_qQbPSw#1VN3`T=<6bA@4s3vPf&K06>_{<BM;&HOg>}^rY_AvGSoxRJBC?uK_rm;~&JzcBKF93U4ZxkxD+hNzuk6+Jz@5(@2mi@=wf`NNPw`k%XXVgz*}f{{Ly@<V(?{lCdm8o`EAOWJ@Yr<8HNOJVPt)^oJuvmcI&*#Oew*Jl*T<e&0sUK)PPk53=iO?uPr|Jw=6sBt+l`RVr*mMRu`A7FT>aLZV&GvOWL=owk?k<=`plzbe?FKGTt8P{L&lw%kPrEKo|NAM&39Wwf7<LJ!1cq$a4sr;{T{e}Gq-b!Xul`0mgIxnd0YqA-`iH>iYxYSNF5AE|4#WhxSE_t^XVUyAL%Mj&s5;f{jgUyZI5(O2Yb$b;LiCQSB>4ke<<5e>UQ-CaK(2jJ>RZ)mq7c%i{$#%zg2;=u#5EETc1}7eB8tY^E#@l^2%TxlGpr!?6>smz*$iuxvte`&z1w<Q$_Mrg2NBMe76R|^=O&j=cJk2ySK^q@m{CQT=}dK&Q)#k*akD#n#zH*#08DOZ$ATE4LMH6wS1op+;U<wsgLDWwj4M91UaA8n_J|#8~g1gyr&qrvGeE$r2gIe<haSt?IHE-s+0YPuORhjT}`qMZYkt@iv6QS<{6Z+o8)=p@3NoWTXiz-^?R}oH`_@4^=rWgq5ccq$a)zaxssnPiX-cLr3AQoF@Vmutx2}OlSArbx!exi`M!c({tmcydk4wW^6lM&uJTmA9##qCdM_dOMT!ws>8frHZqatq`g~;rZcOqc>%zXuu5?+SOB-bSyCJ0h%D8;stadu=A3eF?G}P_O0@+XeRWdL2i+#ZL7c1yGesKu6l9xj7TbdhX{@qJRKgzj;DwuCp2dzU>32?2*O6Fy0yaik-t)=%B4ZROR{zrZ!`DhIuz@6`xv{Mhs_If(Whn)<U?ZcwUelU(FO8$O0?f>{oz<+Yzc&q@p<<eEMURr5(4YdDqF{zJXYp(^~<#mwsWBX3>!FS00l^)Xt-1$6laOZWr&+$BQoHGt?_%8>pE-WV8o{=P<Ym(e(KZTLxT)N-hdptRpEH=q4=Y4@29+O+lT=kl<Px6U`TO8M;=Y*EJ81nR3IxzB^n4d8w)R#X!rY4yl9R(CGM|Az@m=^KhJvxT{-;a*J<2fwk%EPz_{Z@?m7#E=zaWVRQ^si!k4!wx0(Z7oR_ZYXJf1Ili*F==?q9oy1#xRWT=p(o$aP>w_!2h|UceEFucf<a~7`-q?ppU@M3qONvE>{%#>G)p6Iq2u2pU3q}uJK%v7@tJ{G*>j&G>p%n7jYK)Y3QeNP3C%vYaB}Wu_)nxg%aMvHHPa6uE$WqhoXcZjS_wo#!2W$p%39o<+5_cqlAycn1Wu!Wb`5~K_7>HKE@>UBC6;`Ohhl@i|FU0kHz=``dIWaDB%-O!avWoitE>0%Q3D;zZ`uU#trDx&@aRIGWuocSD=K?;abP_8?H4NH=<vIJ`>|6^qJ^w7&Y`Z^lMSVzryt}R}hyk#$fcm=zUPa55_nG{b2M%xqiX*5Z41374#3F?~m~j^!?F$VGKa;h29$_ygyei*GjHzuHSNP=6Ve!{Oc&;3z*!;Vn5Gha?guvU^d1nCO-||FXeiP>sgEo&}VU_b7gP^ay^K19)W%+#zE+Zq8GIh*M+zqMq&&?AB1%ui4uMoMql*9&<|nqS3D61VDv>l0DV7<KIr?Q?~8FT`o8ErFb+aL2<PB|F%bQ5E<ap@0QCMCe~#WCy*EZr)7p9BdWv-yd*V^9m?*biKE40bPnrLIY2uJ1KWsXGl75YuKRJc>b^l8(CaMp7mG$C(;$l4oJ^Tx_#^ty'

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
