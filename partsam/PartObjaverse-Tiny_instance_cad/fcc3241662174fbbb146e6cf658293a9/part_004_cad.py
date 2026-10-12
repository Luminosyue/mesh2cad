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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/fcc3241662174fbbb146e6cf658293a9/part_004.stl', 'relative_path': 'fcc3241662174fbbb146e6cf658293a9/part_004.stl', 'source_sha256': 'c5c0a2c0c4f2cc8a47c8946bdd4f91b52978ceb3083f7d24d762b57dbde26341', 'input_faces': 186, 'input_vertices': 111, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.35799503326416016, 0.049342505633831024, 0.4629926085472107], [0.3598945140838623, 0.05517325550317764, 0.46489202976226807]]}
GEOMETRY_BASE85 = 'c$}q}TWl0n7=TZ2&~hm)ZMj$q+X7umOKG9S0)?)Cg<dFIO6dhCyV9+cLV+!kC>l2*Atp*<q6snaq1b@bg&3lVAYeA)6Gk6JABau7p+vmIkO(O5nfcDhIXfmsH`&bheJsO2GkbO>_?uEvbA|mX6nU8gr8g%CA>Wfkt~eYDAL`!~8Y&+=@N|;Mvbub!?JF(q8~t5L;;=a4?F|j>3VT<0ytREb-ZGE3Z-4kuI5@a-f4Da!dwp>4P$=Gqb_WlH;=Z7=va-yxw4}`QoaaBjtSNfG|Ex}KzkOj;ZilbFb3<-p1wU9l@XV`L7kl5fy6@#%_UA{UR*(FC&b7ymU$pmg=|`)_KK@YKkJ)|s7pyLxx@~n&;8SfLU-?h=JlD2pUEH*LtS6xD-|Wu*Re!!YYW+Knr?l?*=!De+DW|nA4qdnVH&^t}(_<$`weGw3Ao}q6F}pfHs*iPLpVf}{<j?k;`A7BhY;?7sNcS&x&m7jygW1)2h~)fg&$I8mc0N^C=SPIzaPNoT)cfL>?Bl(8M(dHz5vvbhAJPBarkK^o!k4ukpa*iJdQbl<svVcn&Etx_e%tQZF|Ci$&G}U~&qLrsk#$`>zH{z<{rg%M)2sCBIB>_FXJGB9Tla}g`uZ}uIxeSQIjDahjIO>9swb>pqnrC5`}~yaoa(yAq9<Luy6&nEhmL9M!ufpBsC|8Bk7!-I_pW{ZKZ&~ci<h*n)}47=swbSc)i<JU$K|QKYxm2iU3=tOOrO8G+`7JF$IiO;fY9gkMeFqML&ja#btkUgbzQ$^cYeoIH`ZxF=X>sSW1XsQu2a>`b*j3#PMvP7Q?n<`Z>&?*&2?&a^SqhsG@-LjRZm!_&)#$Yy*0Y?ds}_q^**Ayc^^^TypK4aH|`^<oA(j3oAa3Wk=X6~uJ=vV&HJX=o$Gbx57+y$2>$7Me>c0c9*>Lb)}Nct4@P%>$LPc7@9X!e`XsCSzPqE}?~Lx;7gRs7>@Dp)Jg~d@J85>cAJx@<%+IUteEveReO$)#l?bQUz3rBE9?b4s->*}({X5?WqdTAP7-#j^2Vd&v$LP-a$r^9<$Zuch=b3IEui2gN$<g%0^X%82l3zTv`$$cO5b~W7e@gBPKJ<tzqkO5Y`y+CH)xUd0u37efACZgVGfauUXS1CI7r;~CNARU^0bGeoUWd!=WAJ8p9lQx|fH%XB<27&tybPa<FNcfpEO;(F1^2*NZ~<Ngd*G$`dbkQ+hf8k5+n85!Bisfz;El}Kz_tc1#2<y{;+b$EoQ2PVGhq+D1fB&~;cMX~@OoTwE8fbyk~hGua3j8f85`Lyhv(qca3MY!o&#s%`S4_T7B0C0uV7xuYv2laE$)Zcz^%CCdc2;w6<6cc%qV##z8Ic^PlRW}lkpkwL^vNWhiAYQcpY30ufbd3I@pi<;1;+ZUkv-;YJ3`A2G7JNz|-J~_;h#zJOh`!2w%j!l2^lv;5vLGyc%x7C9lF)F>ed=`DkU#D7`=a9*n;S;JtVV?uVbmcfcX|30(4aTyA&5J@9sT7v2Z=z`OB1a38!6AAtA3gLnY%h5PYtH~@$6PPiN1fp@^2@OHcl?tpvnZEzRdhX>(p@E*Ju4#ER?JH7=D;7xEl+>Nh<o8V4-1-ugOz$Mq>wahEI8Lox5;alNmIEZh7x5B;ne0(0<j!X99UglL?f|oF_<Wjf<UV$%!OW|640lW}y#w8cy#mw8xd|PSrm{EE<J|3QrOU}l#nOkxWoDG-Yd2kL~is!<4@IrhloC`0&GvKLkF`mJU#cb!nNw|R1@nkp&&c;*WWH<*O2dBb$xa2fEjd>-fz-jPQ+~1UxoSX7b|26sdD<TKe{-e_ToBHG0!+*0l{)6c}y!o5b<c#qHN)`v>+t;i;`~@4VHtq'

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
