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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1f98b0e3d4446c1ba4ff9ba2660aff7/part_006.stl', 'relative_path': 'b1f98b0e3d4446c1ba4ff9ba2660aff7/part_006.stl', 'source_sha256': '6394c862c5267b9892de4e0b49fee279ba9964fcc5dc1f386141b28086f00edb', 'input_faces': 214, 'input_vertices': 171, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3235628008842468, 0.11052864789962769, -0.3278346061706543], [0.30082088708877563, 0.2067469209432602, 0.09517957270145416]]}
GEOMETRY_BASE85 = 'c$}q~dvI0N6^D18Bq4zS0ZWl`BGw3mNFY=UG@MFBYy^WCHGp^n35vA|CLzefdQl$XSy4>WK=o=!B-lDm3)+sQxmFCZe*lv7F}9t#ov~A=+UeB#SFLT&KIhvf=d9e$blN+!=l9(oE9<Pi);as$xl~oAr57mgRj5i<&V9BmUn#wERe@@)Z)(}Jp}x7KVe_^WmGAocW%QX9)yu1DQdFzjQB+soyrHS6+$vhMaY0eBRkX3Osimp5;r_;^x_a#|t$nz;-tn6stleDiyuZHm#?oSI-i%`FG3$SP<v1n8?XyFDx|ZXWKUu8b|9Z=-i-Z0zR-e=FqaUR927Mb}-M;Be(2p+6{HcB)6L}KWd#<ncpF17OU+DSqPY?bu=*RvwE$+VGQr;Ex<M?*#iq}K_OGjKkns-xA=(_lknU~In>i_ZNpSkfVSHBSSBlxkKkDd(e3qL-#>$POQ{px)`3gubS{g&&CdZNY`^+Z3MaNey)?ib$@`?c5id+}}IenyNh`l+htyzTZu%*D>y>-zCOiuoG9GCW_qJFh>O$2!sM)wz9sUvTcmw|}2-eKqjW%SrvUpZp-`$F{!b&dWNo^i(Ln@gEvE6ZFlz)SG|l3HoL((aX(eL;0I)-2NvHi~RUX<hN3nxc!V@2-k1?#F}vZk+U7=gZ)XoQ<}67#+UmwzTB4|FX}hGtkZt~gUhZjo@?J1&$aR8b8Y;%cpi<P5YMCWBjWiozI<Mc9~1Y#e_e6^`*n)@*1xW}Z+&0fw`$zrMK`WH;?BiNIrDB`z*k4p+<hf}^Zb=$e(bt|%RxW>w~xL4R5uO={RF<%`PWOKJb$nC`Y=CxDCpbx@y>G>L-{|O?)D)zXH6(x{nPUk?@tcLr=|5LjZgP{^@nhLY}DHqlGT&IPl$RFd1ddoD)y_!c)l(68{0hn=kCA%Hr&rReq8i3@k*=f+sws!?N67I&CB?5UeY)7vP~W_FXPL38DGxJ_;Ox;elagUkC>MqFXrXPi+LGe&daY~%**%1y!`xPUVeTtFTYMPFF(JSmpu@@?B)^kGJfKz@VtyaVqPYXoELsv&dcPH^TL<&ikLiNUdEU6^5ez4{CF`h<I8y&U(U<-#k~CdVqSiJF)zPPF)u&Am{+1R_uXXkGJf>V7T1rIfB#C*mvc0}oTKm0dfl7jinhVfb;W#*FX!vWC(6Cgm(*E9q5NX*#vgI69w*PbN#5s6+peLYKjOT_A93EAczNEMczNC$zbn5#*>y*p!}uf4VUwruqYJ@4`0?_5Hu3U&#*h56(Tis;em(NsHv5(5wz;l6xAWS){7d`ZboYBz`%uu2?)=dE-c|8w$dB({*q_X|-*{jkS)N$tZ1=j6^S^TIx3W5t-fza2_mA(3`@zp6=H>gM|HdED&qx1!#jWF&y72c6d{v#{)~R;TXW>Wp(P!gt{ltqu))2~X8~=A7UkduxKi0eZjjYNV3i=WJ_`1G}p*$7Wx_z)qR)^xF_=!_fLh;sHsr|{~BlxN}9B*fwzmTk+D1JiJ6FD%~?WZO78#TVzZ}fYG?)_kie#Y=)qMz33mhgT1a>Zb>z8PQk$2Rez55|}KHNM=J-D7+4;(0NCL_9CXkBR5S_?CEHj2{g?FIAymG2)-SG1!))lwR4YKy9oI{)Ca^g&9r$6UL^p|LP}<xus?Q?@t($of@un))e%M@Dz9|dL29!o`x2|)8In%dRXgpxDYO2X`X;y15bd*q82<B&PBff=fc_O)o?bPfqov&fYZ>=!D(<hIvGxfv(PDU7CaiA3Xg`zpwr+n@OZQkE~FRZS(>k6X`X~mfG5G@(6R71I1kN*^WafvHarSWMKj=3SfOcZ_@y}oO@~w9Of(D5gmci*a1NZ0j)C*xiRgHEJiVC6wPsR_))|4?W>CA<S%JOGVy{|f2lhUj-e|oc(5oBhrPk6wZ%gUD)_H+h%%eW7WomeKWz;;Ax{J|FxEL-$bKnwq4w?_of#;$V;fY*JbIe)KJL@@?<`d|5;S+EtdK~VAJJ9dI9dJAPZMYpihCT})gP%s9fuDw-LXW~)zXjjrtec&6H~LlhZunkwDSR({4|)rH4_u8dfve$F=vUxX@Je(syb`_x{W5$9yc}H!FNZ79o8U_LHuOgLHuzR_K71>@j6UeT*yx?G4OgI5a0R>wT>&qG%hB86a(DsyHFyF1C3G3QjM_ABbk;YWRfq0?>)`e1qwsn-g0{jDcpcgduY=d3o8h(aYV;fMYPg1abbY(f2jN}tljuY6lkgMhCin^Xar6QBad;<M5ATGxp&Q_B@K&@I-U_#%_roplBj|nbBX9${25x}Aj@H06^hEO^XYF;?L1!I6_n>=Wt*78U@Jr5m5$!@x!Cml4mgZh`FWd|7Ll43G;KR;(4Bd_%g15t4(1Y+6xGAuoCYI(#XFZJWM-RaJ;oayScn^Eq&C=Wx*nba8^9#y5>$J9`FRJ0QQF8~{rH0Q^&7J5;HGKAJHs`bEZnPKfhEJpW;L~s$dKhklj|BRAgrzyEyk|tKenzV*Q&J1k{?mWO4ZouLLoD<kbMi04Uw?yt+3)1?zYJGZX6Vm7=R-Qxy{Y%>Z&B*s_SQ*X'

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
