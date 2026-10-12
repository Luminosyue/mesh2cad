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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_015.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_015.stl', 'source_sha256': '2a87b2b58dfb354f09bb605c008fd32da5e020299ff05ea8861b04fe5015a9c5', 'input_faces': 106, 'input_vertices': 136, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2483750879764557, -0.27011609077453613, 0.21710391342639923], [-0.07601921260356903, -0.08159428089857101, 0.27295544743537903]]}
GEOMETRY_BASE85 = 'c$}q}4Qy3K7RRSR<x?ro7LY35f>Ob5O9c^u#j7Y%YO!dGd{lZ%TWS$Yd96q-;8j^5E+$6et}#TfSPf>QZm=k&LT@Skp!72_vI(pEl68w8>taz9Nioix`OkIcMHAz`=H&d}Z|0tvbMD-kcblC#ct|{xpCs1v_3lgd<%|g%#p2nf;&5eYVR1!jS$S0qiz6;R%I{f{o0YvHhHYZi$wkE#h2i8mR`R^Hvy)S-<h2{ZmEnT2{0-rvV!;;{tgk5MyyBsP@?!q|hV&V;Qmh$MQ>?Al@BEAqQ)z7PZV<lgUme0*{aqcmaqpjhiMSit=L^qz{`-sEKXj&t_{g2aBa`P)95!(Jq~I*Eia47ws)5?A)!oFGEs$}#cFJ*8{M}=Sd*O2@$&YTAapGR;qW%LpM=4IX?60^D9?Yj?F>x>N#t-yy-CZfNzkRNgyc)MAL_G4vGU7hQ^-J^VyK}0(ULRL+3tWwBpZyQz<HaAS)5o<hd`tN__A_;Q9K|j0AkLfj6K5HJf8VIvfi>;)J?X>ujXHpP;6WXBy>f!`{3`uDJ&ylOZ5#Cqzxtk$7q|-^%x8OVE5*4m|DYbnxlkf`&D>t{NvQMCm6Crv)Zk9lxfY5)?czawT*YnhVB9IWk{?c{INtv6h_kdT;(q8<57nto_P3t>zM10Y{kvA5rx)5Ld1rz#A3uHzarQ!nIsdY0#O;hvjCm@~z<-|S)5j^V2|Ydfx{Bs%o@~xW;*mzHSAXuJxysjiF_E}`ZK7HK#F{3Gd*;U;eg0P3^Th3U(#^aIiik&=bB+71xCgHCio`b_qxmm-!^kU|tGpt2{FS)%%{M)IUeR3T<-C}2Og<NVMqX^(M~yU(smF}G?0L1s?QhQ+oGo};_J1qKd@jIU@Zh<q+Cn^1T78J-HDPlv)#1P*8K-iWj5Dd6xc5~^^1UmJIz;oJ4mbDG{usGupIHZRA6(VJcAq8gHQC1V?tYgf<2=8{$k&M(Puwc3q5V?rSJsF)8E4>=LwX$)cfeI0SjN}1FS~ymb6Br~pZlrg&U0p+J&!o+A0_j`K5zFqa(}N$t<&qqGGmE5DIay~byM61S9SA8-zWF+lc`4CqIs|n?C3i}{SHhr_FI2U330pn^)9_W_PuGuSzF|=ULVE%R>_0sI&ZS<Zy)bA*5Rpl>0EJ#U*4_P!T;>F59B%@VbskpnNHka-O#1iA(}_jxXW|tTyam&>elO^xC8E@4(>a#@_ZWa)*H`J<9W)*?J76UHFw%yh<owNj_7qz+yM{P$@-PV+1{O9MqV{jBwyd&X{?7(6WtFxtJ~<$66+=J2pi|G;ug571G{)uuGgh;@?2Hta;i_<%lk*Cu};8U@Sr{=yNNr)GmaY1*PbHcY)gXiJ4bQ9I>GpzV-F0G{Rb~Mf9J$rlF#k*ah*oKIR_;#y(rIll`pst9^_m5AaQr#&+U4?ZsStoPJgx$->rO`_G|0->y5_z!5MgPA9uV=+zu_4^H=9i6c6g=?U3g|N3E=n8n<ILaj&VNU9W@Rw@{AT@@1Poe-@J_d3s*EQHLn5>fnz}l;_j=$7S8rxKGr}bHbb3YOIImYU1|ixlMW<6t}>G=j+pa;%?J^BfdS<mhtzEJfY|1UXvpGhu&z@=dZW}9?bvFVUmBj?wC=xEGFahztFDNKbi;i-})i_j`0T)nvMG##e=-|`0{tp$45`-d9l5Rh&!>77Nh>)Hn@u8zO|pYx99FwW1VMSCFA$cI<Du%%6@p4z90FgIqqZq#ND&aZN_>7_fP+?)wsX4b;Kimp%y*9|Kp>w|G=4+AWpXN_SNx9L;2=d#)J*$Z(nN*v{x?y#Yg#He)TGy`P*K-rvKlsUgF(LOl2heWzdD(9^h64zY@Bb+bXoLLR%rOWw>5^219S-wo#NBegpJoZslk%N1M=Bal3}wc=)TKQ@Gv0Efsz$^bT%+;<g3;3Fxij9-`evo6y&Cn=I}#{Pob+p=}Dh1zpAMDQ*wJS3s9?t3-Px+JsK$b_=(g;BSQ%^V-QR4F4o_KDYJUa^W55W!wtTUVyfI<o*ZbFMJyGB5wC{n-9MjTCCYjv}dAC=sUU1<F*j~cId}&kILZJLQm&5m)kV>8PGR!n~C<BXcKxiYB2}?Cg^*(-OFtW{8H$N+>*IXfKP%><TeTIlh8I1b9)@~6aEosk;`4kNBFy;#p5}STL?Y@`butN(LNS!LW}h-*7k$&E1<97Hin6Rt4Kc@TKp#^4()Mh6M8#px(U7vIvcgP4}J-B5ysAg&w(Do#Ad>eDfpq#gSZVt`!KW#y@1=z+-&Gs_`VKftbxyiUWxp2;Fm*-+*cug;a5Y8`fo(-g?|)U+*7f(GT{FRU5N2Y;MYMf#Wh**8PLVJ=3)2}Xc2QE;tGEU^fuJ@Y548XVs7P_pYYYt*_kne;s^iQzs!FAxT46$KhUDDG`D;G%56MWu=!_a#?sz6i2sR6rHhrvegee$PT2'

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
