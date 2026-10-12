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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ec56d0baa8f492da805fcf2ea98de4b/part_001.stl', 'relative_path': '8ec56d0baa8f492da805fcf2ea98de4b/part_001.stl', 'source_sha256': '65140c30e0f35c3f687307103f3e981dfaaa995eebf287d5e8da9cf17a5a687a', 'input_faces': 68, 'input_vertices': 64, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.07000307738780975, -0.14398451149463654, -0.2589462697505951], [0.13397365808486938, -0.11902584135532379, -0.19372662901878357]]}
GEOMETRY_BASE85 = 'c$}q{4NO&K7{|{AM3jpn-=A{8_>#-_*X7e=S<wi(O1UvHE`!T3Qwan^YCDyVnPn=4_CdRv#wbk@6C#D9V_1L+S?We@x4CR#MK#w-QM&K{c}!`wwL0wG|HqH#KIeJQx!iM2`HoIr5*?wEYeLdy)mf6n(o0@ay`^UTs&Y$h+}i2}o#YNLj@#K>_*j9dSSQs>jgb|W+VYynOgS>U(imxwBP-X{tgk6sTe_~M!Xo?wWlz>x?7p_DtlDD#Jt{55ASXu~<Y(podd#+upmksESY%J@b7xQXiP3URBO<jq6XdhX;B8Tb@HRup5#i<UQcsEBrHO~(rJs%PQepu0IiClw#5KZOz1N~%&c2uW_$}=e-aPV|hPtg;bl$41<gYz}dUbUI`70NWqR;UG^fx!}r2ffc@XBZjyrkPs_5Q!W+wvBokMh>b@K&Sihr(;s-l$i`n&9Q0czAW7l<Ff?s`q{y-u%-_%&E2q(tc<5z)L&)XwJi)@aC`^@YcPjseZhH>OT%RhCYujN4@o<HB|rFR2Q!2oB61>sw>Io>ATV2Fo`*}O-0maG9F%T>*>SX_YIwc4_Zw19q-WfFB*ndjwJWM-)cd<b}NpqkCH)tLlfQKm!jd-sWtGnL%;T-zegVWsO8U4eeQ$QzvU4+?@iC+xSrh?slMbYyml}c-dY$-_a)>qynOn8c)7g=^-^owS?u?l$KlNvd}zOmJK>eVet4xPi|*IgIcM;?;`dI#Z+sekY*nS`ZyPv3{s)QXyt0(eYZ!+&@7;%bWx;RgV>3>{+s*~jockPbUTxm8UhHd^h34rBAIAMru9M&S2Ks34A3RI<`389>cbfCSe%jZG+&;Xowim+7mm=uAf%)*-5;wXp8^Ykt9cA$HsSjxW&qoLG_k`W#>qb#;Za+%?oQsD3UyV`y?sq@M-*@?uzwC>8_2#$eZ=EwAUY=;B{SJ9yU)od>)f<xVKD4cP0e$3)MtIw)L8@0g;8o9Tc%`YE=1HB4KIVdD)F){R)o=Uq6V$tukY7?s|L>Mbc*VJ#`tR|l>+CWNFY7C5&ga{ye(oiBt+9^!bbUefCZ8efYv=3m+W2{zr|3H7QR=PmQcNQCan++<scWM?#xv++&1}K-v>xlHeOb2A=gi7A@a7#u<i}Q{kNK5my8f*fs84Jt)&E`rFC|@~`GY!8uYF$&uXO$hZ{6|`%`+Z^Io056RKMIt*R9|X?W^1KB=$A3pZX`Zz^e^D@Jj!S)PHw3d0ja9;v9NExV=hVA3=RKkI;GR_6+rzraiqjR;}1{*in+inq_}_RhHfL=n_&KxAX5GU8_?5-J{F+zaL$x_8GG5D~&UoS!6DA8ncme5wnpwgO}iR&K%}+<`m9MW|7IvDa^5)(af>T;hbU2;mjeN!OS7d0i1r!0n9#}Ud%qs9-QvX9?W{qIm~+I8N38La?WOUWY%%IFpHeYtYelqXGwPs!4A9xJ8`-)J25+R&Se%kkJ*{ojnkXijoFjapV^bymvcU|FLNO00%nmib0BjNFTtUl_b`VtM{q7=j$n@BOk$2=HgKjg8<^ub)0jmXnd6ufI5U_Nm=k#kj^|8gj%SYHOks{;j<hdRzRtnR@t?k`-Z@lplc#-g{p%~Ie@xu{%3gb~KR+}~`7`h>*TMetls((UyGr^4f765R'

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
