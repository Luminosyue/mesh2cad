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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/58685e436e6242c188b95fcc2ba7c1d3/part_000.stl', 'relative_path': '58685e436e6242c188b95fcc2ba7c1d3/part_000.stl', 'source_sha256': 'f47e40994b89c44b46f57afaec4cec4c50dc31141e51b715d39b3c8a30553b2a', 'input_faces': 218, 'input_vertices': 143, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.41326701641082764, -0.2066982388496399, -0.05329706519842148], [0.500009298324585, 0.25725847482681274, 0.05329715460538864]]}
GEOMETRY_BASE85 = 'c$}q~e{7Z28OKk1QIMflEmQ=@MUet6@~a?YNG~YZ(oriE7|_;R+gn;%DE&cMX(=x#<wucbGE3rgyNV!|OwF=H6Swu9Fm;llS;jUEKbmaW`iEPVxkO`^ZSOhn=iI*M+`DAiZt~>&x!*qbdCz;!dCt9WT2d4ml_~t!RPpSue=>XMW+7yZ6Pcnd*4$cG6>GVF$IkXNk)eF~(t4tJ{hE?ZX`)SZWLL*ps+zNxgtM2{EY8jiXV)|~w>DSqc)YQ>Iwt*9l?^R1&u^)%+!^!U&zP6DAUC{VW^Q<I_<wwj^@iYl-uy|v9Lv7JUrLR9-qbyi!WW~OyYmBn<kPl~q=vsR^AmoE{I13;N+<04K<34_mmFRe@S|hOlppz3nlq5Xchl3IU>$KS!_VIq?G5G+Ud4Yd+8fM|uQ~Y(l{flgUoc+`fA+r0fAe3@2mSc&T;IQv@uE?G?CST_c(#7_k}=MyrSGczEt6jk`jNku{#@msa13AkVciA!K5FI1zbrp5--m0>`jPmachtOD<B5#@(a%(!x2*BMnW6l_G3Nb7vQN4yf4enr|0weP%l`ZiE^WUOTz7Xv&goRX-Y2%N_eqk!Ip=iHciJ*9sqtQ3bao(x@BVJlStGyVl=8*ww*G-s{@k{HBY#=VhpLWScy1t-f4=aXk>5Gq-?w&s{J}Y9eX*y^_pR}3-?7H8`$B9q=hN<^BtK-%r}o`V{(L&OzMi_j@RRz>@)P}qpVVLYN&SVN)L(i$+MjZ<&!}(rovvf|oxZN!cY6GG-{B|qoxZN!clx?^-|0Gb-)Z0OJ6*@_JDqR$oxU%-?>_Cis`CFb*`Md%_N#f;zB}ufKc8>+_8I;={r+|TUid<=PV|#W%6DJx?F;&Y6MEEjo&J6`9`}}iUQN~Swy*nF`}Tge{lxzKp!iy<acbWlr}ph}Mjm-W`S!VC`}*9_zTKy`ulqD|?uBc{JRJY{)IbVfJoE9XV18mAdd>XAJbat{!B_lo{`7*nU*}IhR{JO659Rsub27az=!eA_H4kp>_m8X3HT}TPx6Z>PpYt%`Tj!hY>+{Xs{J!s7=Vy}7`RQC9Qht2?IMpxiwI$yj2>NB6>b@ewhrSc^Bdve-_y3&!9`*Nq;<~Yp=ZDUu^2K{YXYvESUPp1k%-6pAF8TepT@S8fbZ}vOAeI07h4Em%UdOnVpE#e%cRyNc)N#LTQtN2@`g_y%_4j5{9nstu^!0Tk!)AT^dnCyZne`KOsP9}Vyl(8D*tAy%Qu(#hUN!RdzOwW6zS`>Ni{;hVgZn4^`moBkeeuI#zy9b}W8I?{3sisEe*99wsbIcd_qdg>{ix25e9zo(6JGPrbIVWs9=80%?_tY#CcpN4(AU=uXPNaA{ugHbgdZ~NCwyK1Z*Lpx;;uZQ&fz4#;KXSoU$2Xuj~^%Bt^SR%E^hBO)nB$Be`cHNFDK`Z#&x3=Z>WB;eMiry<-7WREk9EEM%?fjr(@UG_hr||kJ|P1zSZ^b5QD}(9N+7I?^}Lc*SCFL-}2q8-WT&rjHkq*59`mq<vn}JxXF7;tf>q<B1%)fw5EPUtjqha9ueoyTm1h%A};mDaK9H{CnV>hV_>N_!nyD)bQC-bo`K!~&wyv5qv4rw4tf)u1J6ds!n5Hy=vUx5@LY5pJQtpa-VD!!=cBj4^Wg>Pt?&Xk56yt{;DzXI@IrVIdON%begM4#mbw_0x(t2*eh^&=KL|gJmcS3gk9zS<bQ4+vZ-O@yk{?4?!jHkL&}Hx{I3HaM=fht^GhwOYVW~^tr@c7h#c?kVpbjDVD0&3$@}isE1MqR8n|e|Y!u!4G@nSC_`AJx66CrsQA-Ro^{1n;)OFafZ1s_D8hFiR7_hKI*`4D`FaqWkDh(pvkLY>3tG58ochtYOe>K?eki!v{oz4#VdLr9LIWpEV!h8N4x0<;V+fY+f7@H%)Sx)a_AuSa*l>*3XC1-u%5h>%>2w!+2m6JBgXJJD8H&Rd7@_elrdQM4643Oi^8T)~(eLh=E0rx@99lDp6bxPdwC3e0;KA-S87e2|d58?AwN!!a}pM_G?pV4Wo2iB3e9!^>H-iG<`y=sI{3d^frgz8ju`u7{_<Q_<D%RQO)>A^2W6n~*%6kX(lr!^Ny+U0{vt&`!9Mb(LHs<ZoFawxEx|Ti|*xD!nN8VvQFo&_c8vE`&?b?Qki)0d0ggz-!TZxSs2-B_vNKB;SQb;Je@ngybwjay426OMM)cS_QYEyU;4QiadR$Np3=m;3DQrpMjG1qV;0r%#^$zZ4@JCm*joub}@3+Np3;Q;d0ia1>Fj_!0m+OJ%r?1v=Xjl{b~d2D)~Ni8oB~r!5U8^B;SLU!uP;obORiQzlyGf*RrmX)4T`?|0OjYPD5pn%6^x<t-mjJvu;vjV&uCf#v1D0t|laBp#m0MD+|3Zz#-lrW*(0ak~`2^xC5>W%wruPc{&<`L)_bR^iH^>C@noR^q>AUGV*fN#039QVt>;7xg7lDbnk~);>UAI(G55HlaQ`9??idhiGKqV)_Hg'

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
