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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/68834dab6d6c46bb8fb7ca4d5c218b67/part_006.stl', 'relative_path': '68834dab6d6c46bb8fb7ca4d5c218b67/part_006.stl', 'source_sha256': 'b56d8bf6c304e6773ffd6edf4e7e0eba98cd8db9da1e93b38bfa0dc9f17ebb8c', 'input_faces': 100, 'input_vertices': 97, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[2.3558735847473145e-05, -0.45629191398620605, -0.17063398659229279], [0.3437333405017853, 0.45629990100860596, 0.494384229183197]]}
GEOMETRY_BASE85 = 'c$}q|4Nz3q8HNu(HdSN%Lx>W>Qc*CVsAwV><tkwX2?#0y49X%bl{P2>u~Md!+esQzYiv8lrqM}U4TZ)iM4%g_n!QTY;tvr}3@T(Bt26mQliJvjR_)&Rd(%Rvo#~`IbLM^SyWjcFch5QZ?A^3vA74KupAc2qdA8u!LzObyy~<B*u$Pt><=e}qtu3kWQlsFTpRaXWYDP+0wwKzVD#HrwW%;FHv6iq$3+IGITEYs~m6n(0t<7CmT3|PQYu;03c8_1SCa=WqxekwcB+?Q+CDQUE%QyWDLlKQ%&Nt;sbdSr_FLHX~2Kd^C!{NKXs2c1aX*_58#_iWX80Z_WEclN89lZm6b+`ADd2O>Uu6GU0<F)3p={qtm92@BC-p%lBi5-LD4eyiijkt7UP`vLfsc%`~?=b!^I%~~q?au2MS5LT4^0dEl0R6o-BaeI0Yw)#m#r25y-YNCWABp_N`6KXkpMLn-(pcnIUET1NSE|&rELZBkG3g+DS2*TDeHo5<aD09kzU4zD^Ze&J>31`!8TtQs>9XnDZvI8azcb`8zHjq?-}LqVEu7Cn@r|v>Z~ME3`FH!)zk_})N$26;u7q!l+<g@NZtd)bZfLB<{f=sZuN_*~iTUb#4)df&_rZ7cj+c6_mY|<8CbI?O^xU|F`mgO0f9!tv#-Xi}=Xx9RXnyVR)mK|CLVx(DI^-J{@Gjy{`d`4l`eYp9-TsyE^}qEa-fdka>k_aDzReYj`?cKoT=GwdJBB=8wIE(EzkV3&6*ToY{QhU*YiU1u7xe~j62JR{i^$vAdk*Un;&lSr?S${{^f{0F5AB1mIX`Yk|I6bqpnurGKfpiMfO*!tE4na#_*M9Zb9e{pxV#wgD$>=8?+-S^xAZ(Ad8W=i3IE)dZp0sLItxFl1-`p8AHHg7gRe#JJcWE8Es^n-=Tu|-n6NYWzAp4E@*H=zqyCtPGXwXJwlW>}qhc4q*FTMrIx_ugur9IrXJp?7$-X`QW63kOPW-m(STB9m&yYu-7t)6Qbyke4op>Md+Pnzy`!*xLUR3oazSr8}>wP6MZtk8Y<kLP9zx8w%=BHBjv7y}*zy3DzJ5GFx{I-QpzK3yI8xZe!rp*OEem8v8mnid|SacNg@mL>x{qgow81H)xGQWF5WWJq4u`Z5+iC8DCY6E;dW%OypfBy>N9aX=AucFeipR|GiS=Z`2k|#an4C-Gq0`W%m1k|ghZ%4ev9*=lc69V5j&?4()edP%1ud&Mfb!~;}30d2)4!_Nl>wsP->apj`xNo#e{`cno2K5)dLBB)dqn^gNMqV-YrDgAR@h4Qjjrt2;l=!{g9T+#hq80lf`S*DK^*2++@6PIw`DogXdiE9JT6N@O|2e+fgFKdf#p0Jw*@62h2!!w6w@duMT8!&n{Wj`R`*%zJupeNZRB8pz3)}uy_{PQkGH&?`yYPMOHOceR+D61>XX1I*YVR_BpL}nfhI7MFJGK+oPxZfyczZ7DF=_+F@2Eums$eAjVEFp#3PbkKU$HK#E<)mez8lY<p8MIe$X92T_=`Ja{EfHXLB6;0B;Ic_)=NvDC+FQ;FN^=njt2B!@v78+;E4DIt=ln=t6!A!rT#PVTbAv?{Ve^doP+hZW!$`A)Tt#UV7+V&3viyPt#{;iEb|o3N39`|eumV)zT^eOH$E?ZPU|-8?<H5{d~d7~-?i8!^I0tO;JgZ7-`05=buNm)x>=kz#ozo4_Pu(}y%FO&Z%Lj_Gv)U-zTFt)Z%>kQE8ll7_JuPP=dS*0iaf7nui-qmG;M^h>K{G?UHP#S`I>4Zz9>$9$Da1b{5uZzh+iCp`*CD%d<p%UKM{Ye>@$^p3+rQPzAOIv8S?v+QC00q8}wEet6e)geTe5t_Ozj%x4Oc-0k3qXX@0)e|NKf<H0ytQrJFH*`v3V(H*BV-hDfs>Hj}4NCzGd;Cs8frN#tN^06CcKPaQ?}Cy(S*nd(IyMfO$Zq$%|+Hj{_3nLM8AM;=dph#E$Ih`fM0m%M<yoccJ~)MWB<@>1#|@>22=YCL%fIf*)toJ3woeU!YA97lbG97m3!&LYQ<A7(RoDm9!ul{}FeLY_#zpE{0wKY0xGKJpl{H`Rwc*3(9N+5^-H<Oj&1)bEf($up=C<Qe2S)Y;?}o|fooS!^a-sZnGrc^Wl{JdGSk9Zn7;-|K1LrrtvxPQHgcgw5m;)FAQ*@`KbU@`L1PY9cwBoI+heP9Z<(X_?fOY$oSYSCDhbHfk2xMqWjIg1m~HLtRGBA!k$5$l2r!>SA&RIi30#Ih~wJolj0BCs5~*6UZ8y$+6Vg<eAh+>TGf(c``MEoR;k6?dS8~{zCujqnn4xpg+|A-gEFVJ+Nn&=klM2c3Scf^BnR#1m0@BM;GAq`Ujr^iU<'

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
