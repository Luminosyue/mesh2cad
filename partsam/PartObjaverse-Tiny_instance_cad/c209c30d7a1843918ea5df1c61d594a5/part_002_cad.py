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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/c209c30d7a1843918ea5df1c61d594a5/part_002.stl', 'relative_path': 'c209c30d7a1843918ea5df1c61d594a5/part_002.stl', 'source_sha256': '4ce4a787f186c1d481ce5fbde6b77ca859b5db7b0015baab8112f17b991fdf5e', 'input_faces': 152, 'input_vertices': 197, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.29662346839904785, -0.3500428795814514, -0.30798280239105225], [0.27601000666618347, 0.26294440031051636, 0.30800342559814453]]}
GEOMETRY_BASE85 = 'c$}q~32YTr6o#jiT|kNz5x1!e&uURw1O>Fu4bh4eSp;P1>xQ_{+F}I?@=$Td1+)}Fc?d<Tt+KV!BJ{NqBt#I|!~~NPW1^TC7bHeB@!Wg=GrT!>OpLzd&-w2+XU?7F&Yk6DXC=2yb<8i#Y3Mh;{`Ve^qtwMob;=4#X3fYeD7|WC@th>5yXNZ0ap~RTMrKb;a>|_YP<}yaUP)+(8yZ%4T`0p16&97uDv8XTR#cK-p!o2}L!|}8OYe^q7f}21e%BAqa0jGkxbxlr`0K2;;n=DDO%$S)d%sZ8$?5q-QxNaotvoZ4F9FZ)<IneaM_+!tyl7ug{%MZ<4#zbQ_nv-O^B#9KHYIT9jj4twwKVwhi*_E;yjS|x#QgZK?S{8s)#%GlS!=d4oIA!>Kit;GV<*1%*FVS9XYSSSXzDX>%|xAeMAwNP{ocP{%d;ANyw^0tH#F=0VxIFe`VE<WnMZF$znP|A=B<mdU(p+MzwvEZ+jaZQsusQfyQVg02Jv66(J{7Yir%jH>>m&4evYr#QF7<Ip|yd0%g~R4>NvA&4k+%9GTeFF@c1{TzU0myCO_8B@YdDX9^^~z%pF`C$bZ82$U3MWpS-Oh=)8DboEPTuyfByNg}FR0&Op&`3dT9OH_nqW&N*L<L*{ZEGIx2LV;s6YD@~o!mk#=lzu<iQTmM?7d2F@eJRT(H@nCU`2a97o#6Mf+?-%FM;y90z^LY%{O|K8S?%b1=b-JBbwnZP8ua<2J<dgo~n3=%isR#E3<$E0Y(F5%@m-DB^F@L)Efs6Um<{f?ca{jcr$&aNNp2KxUn0$*D`}1R5N921P`R*lMHtP12HD;b_`&)BU0Cy_-2lI7>%|UgX)by4_9$k2>IjBB!S>NNLzQ<ADY5Zk_?sre2=|5w%X-i&Hx89e3B43X`E1x;?!wpl{>VDtqvrEU)t}Q{_$sMv=^N*i?RktU%)8pQmd16N(FC6o!J{}c|{JhBITb%QcA9_XiyR&+aj(^o*UiWinZ2f`6{P6N0b_eA%=luANgNCC{82OTOe$KS53w8U{A<cRIk(}or=Ftfip9SSJ=X~c#qp6d7*z7OnE6Kh2>Z}IM<A0!E%s&>#{3AKfKg`3}9==aW?sVT<709cSHV4+>`&7Tstf1>oa=tDsj_bnWxGtE>>rQf6UtV_>=j*Pfb9T@;l$^&2b2$zr_r~q2pGF0ZL&?4RWrN1+D6Tt;<2nlOAK~Y??ktY{oLg2@>f^!JJLUn4N6b9n&RD6roHr!rdBd&$wOaQp<}r(7Uh=q@$1INg_|EbVb-&_1Wpi_1U@q@dHb?%%d78`nl*Nnv`SLzxapZ^hEHK+C?#mX(eK|brl$r0vbArWj-)AnL6D*GWoU+3@%I6d3%hWo({l8ZDp2sBj=0o>v&7;gQUs)XUmE_)hRoT<jUsK_Kt`ppwCne|SI?3@|7jutl9-n*C{~jT@_Z}fRzeh;U?-6BRn|?=}^uI?4&c`j<WOx*u=V!_Jcv>9C)2hSuCv~mY<3c>oGndcvUcPvqXD*-Tnak(-@R4r*e)0a|aq<4bT)w|Bm+vpk<@-y{+~MXu<J<jap2vHo#qnP0aq%8%aefcoz2u9a{qnfjFXnQ;n9KcQF89m*T=a|Y56tEF2QOcIe_$@ZKY01#`-4|set$S7>ht%9W1>EPe*m}UnNO<Cagg6_EROFm;MR8=i<|t`%ic3}#C&UUHQ#3YzM8c>l2#k*K$}kL<fJ-<k%UiX3aTH+;7?{V2L8KGX4m%rzn{!z(l$ImdKhsA{OzP$NW&3thJT23Kj}fl>F{@uZX=CAycPaz(t1)V;)n1bkZQqd!IgiRR7H9RaSi-BEL)5C4ty2bA0uv0@axc4aU1*+b?nvYM9hcJfxiav0{A?%S0TpW&qq!kVm|ymq`OID5J$m}LVF%!d4j(OZ51Db=XGWy&V#><6e6V~4uDUG?}K<bd^fbaAco+(BBvYT0C+XFZzSD>7>1unnn0R`SPH+0^fc)i#Ao3PNUKQ^#HH{TVp%`L2>fca-$pD<@E4-3;zjVeSobx=rSSbxFBdTazlF4wR1YcNh}ZzH;z#h4NRvsgAifEI1*tcd_r@~i%Sdxck0Q>2&nAtAAB{Za)wk+1NbM0j!mDYa6P9<vGUeNmZXmTq90osx)CTP~VC<98PR9D|hoU_cwUjR*Jwmz{aXfqxX)M@SaQ5TS9*11^#b_6!F8d<1i%>)Pr${ZNClQ<B<D@3ACUEu((O!sL<)6ShPa(FzzeSotdKFUsKE(6jRlE}ZJ<=x9yNDa$H<R8cZA7ewuOrnUuLijru&f%(tFcV^*GbDs6^L)Z_a&V}%0TQ1ua-^2dMZv$@O{zli(KW;B&CpC#Eaq6NSBbhBldt-%Pz%wDxQ_#)6h;suJY=49VrR%didu^pOBtM+yTFWw34(8u@e4VQZLfgh*!biMY@wT5-|%tN_w2M0C7J2omgi+;sW@QST~CJIQ$^eK+<5uYvEray+~S&_yT-(R#KbP<bV20?DQ|H4ubCwGP$Pzu^@5HL3CifhlK2`c4{7=3%HHGNK(}3bp8f55fc~'

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
