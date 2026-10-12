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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/474fd643f4204ee59ff73fe9b1916239/part_001.stl', 'relative_path': '474fd643f4204ee59ff73fe9b1916239/part_001.stl', 'source_sha256': 'a1b91dc78821328fcbe651cdc80fcb604387b8a6a3a6428756595560d60f92a9', 'input_faces': 113, 'input_vertices': 140, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0868525356054306, -0.00872012972831726, -0.46173906326293945], [0.07593744248151779, 0.21573856472969055, -0.050669193267822266]]}
GEOMETRY_BASE85 = 'c$}qJ3s6+o8NT>PL=hh`zGGLc0tOATh>F;~@c|f&tQ09?luHE^Q6ON5iiGPE!Xw01GchH)0U<s>V|>+DbG4ud8hl1aB(6pqlQbDyGdg2*+H=1DCv|V>OsCzMZ@%w*_rL%7@7c5GoV)gj_8odD^ck!K1gY~KT@^*bL+PbtCuJ^4nU|C`GA(17o6;S={Iv4#r_X%VKFdwXR&u-(ld|SzdIwv)Lz2gO`&qn`(=(T3CZxruXC@{|KQv)cR+8|u79?aOiMG$EKz~1r)z{CGYxy5Poka=8!|?|`leO4;YBtH?ai`G^TE8FM=~k*_<D6#$+9xjV1*^TYWxO7Iw;tD*-ue{2t|UlyJpUE)=y!hHgX_UpPRMvm{|BGTwszth^7oBADSho7YZLCbUV*Q!A8=gyj-g@jwKZEPzH8*4(Qohf&%$3E3SYTj2jA!&a}ND_`%}E~J^EEIH#N$(^RN%a+rBf9r|bDMh%b2e6Yw$5TEu7FL7hgY)ZOs6<x_mzFyuEHEW7D>4<o<6#}B@`wljR=Q4c(qBQ=8J$5?madSN8;SpG5(`IW{O;p+#>kD%XE#dt2&_KzA|pMC-H>b<oTpL~z}qZS&^*$o&UJvSP@{^;6gsHgG|crN3}_G-kRo_!2{as%?~J!0Xjb!9Zpm7C!!gYWIc^}>KZq2K&C>i6hA_)2|go%EeAJUEZ`TMH@v;!xyw4k|{xJ~o>C{sr*0I3MIU+{<^sFHb|A&iCC=zgk-aUpZEF3iI&cTIARN9uD6q=uYF%QjT~d?e2D5UpE?gjN_qHXU}Eu6>a0Eh>u!&68YCnqxca;crGKoH;uzSck)B)kw-a{PW6BHyKTthHJ8To_*NR9`*YzNIq#t!t#}vJe`y@W_q>e!ny-QJSAH5!er-n@|9BqH%||}Qec{cRw_0=x%@cJRd}Z7>RL|t))UTH}`LAEV{B*2p!uS~Bec>CAQ&EpHHW&HT%_pl6?^{QH`9PW{mm=Y-x6jq1o*j=bA@26qmGDD1)BMaCO?Bo~!&h!tQI9&c8$ECSQu51sV*cpbGnBvoimj-p%s7oYwM5F_5>kQdyK)ZUd7E}%Ju$j;{|Ns6m#LoX4-s!%Uhjav%7O1u_owes$<5!4{-Zu@#Qe#A@C7~BqD?eT&tg0+d7c;G|5(2PzDE_!lkg|k;14(qU$sufcxpqwgs-HOZJ_zNhT`ALr})wm%46+@`LFf6aFw1bo&3G~(XaDb9{C*-D9_bn@EzAjT!CM+zZ4vP2)?47rTSxiO5jiV{1epQenJb{Rh{AMGv0u&FYiNsU2rk#AL>i>IJZ;33rDU7Fa80(p8hV4e`8A?;_q1DD?c5)O!F-KP54?Zt$WHA%A-D<kGP4=)yThTev6CmS5gD^Dsl1EC$o@8IdkKhOZ@#T^s81jUUu<+7>spNEvTV7JFm*OwN=l>Gex$x>W}d#wYBlQdaTC=TN~q}daZ_U9?w?aJpTHb(;IDVd|%q5$PaM;lOyoeTlD=J)r;Yq=YtwwMDeD1)#{t)mGj$!6dzNLcx^h(+g9H^Z}o=RTj=|6o&QSk_;SRXelL#OD=QGch<;zn%xwI=ocBGqqF>YRQHu?%LfiEF)$V^!{!1$lfKzTFkE31A$9PWDI-s}9*oOX0>xS{Df_z_pT5qFiopHq9fNx%xoRMMM;hWYmy*UfMUO9h1`fZ+Y%Ehnv;2?P5YFbZf4s54>UDrvqw%ZQWZ(3LN4+p_FufyumN#vW>ZLQy4_~vz9&Gy=fI%;@dSQAUnb;}pN^4fXqBYGh1BTlzS_~v~_FUg_!38ggtZ=b_+8Oep@oAxi&-wnTK^L}U97(%|5kA4+LFRH&JqnhTu>wfCAy+i)C`gOQ(z$Bat)o*W*e|{9@KTG?vB~7iN`R~c+u8-*ZwXKG4?4f<%;m-U1+D){+{B<GnShmtR!PpzI3-_DO6-r4Q`KEJ-F{T>6`P`zGeNFxnI_GHBJpRRzyWt<EbCJ<dM(37>P2`);QA7G*y-=<<uS6a8zu`RLcs!KW7t?vnc`u9N&F8l{Ipmwpd&YBl<VP>SI%h;(#W~vuDkT4I7o5Y@FScR)wTkuBujxFg&)NvzeEw7ww>`*fI<KljJmCM^`F7$c_~!GlBjYQI&v;UReuhm!J;oFd+P_WbYRl5C@C_@U!vmV=yn1^l`KEKbWB3W0e|>9dy&cHs{GvX45pRAkxEBTA{2pQCB~iTTy~A0aLH^V4DR!5)yFWJEym_Xh*x3Z!#oJwS!c(ty(v+W8Zu`|PCGfv{wHsyqe_!pEiW*i6tYBWiT5>$=xdOQYvCNBE$Fh!RUcq{hz)J$71b!p1NMNQwfPlZiaE8=<n7vs`9?Dws0M?R6vhKrrICB8&Xn{EbG0aO?$FTk_b0X_RZf7v0p2a+e^&HMCwR{imF7Uj-FPUZAUEo=P=a{>(P7-)aAe(tD>pX!1fn@^gm}R@Cz%v4V%zat+5a^=FzY2&uvGx>@)2J(R2iExlYXnva<S@&2kwBrqN@kt)WPvb&P=?gg1b)pN&K$-%jPD6&NIiui^{<$1tgXz!%r@4+tX1a8tR*Hq6(jXHhSXyiQjcaxJ&9Rmt#Zyu%%Q9$Ph~xcbreHtJ45PM8B=)-rt<yMxZgmoWgPQZhSWjKfvkgAhcJ(49m4u$=83E&N3fRs3hOAYZwC7__}VM1Bbn{2BUw*p*!h`;2n-YW1@mCm{g`_(r0&f;n6=~=SX%^q1o{iSC@_NCl6{}LCV3#UFKfwOtQQKrE|9>S&iXaxIEK_3b2@9u^I0bgqzcSqNSz{(Dexw@CBMNsm30bp8tW{9w*_VkEN7N&`Ee6y$K0N^J;JSBulE1xZ@zzhba|7@pMK^$UAK^@@BC8a`gudKM|70ygy_5-2JDVpb(DVs6wvW%'

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
