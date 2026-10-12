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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b3e8b99913442308aa989e3f87680b3/part_009.stl', 'relative_path': '1b3e8b99913442308aa989e3f87680b3/part_009.stl', 'source_sha256': '87790e8582d5362377c81305ff751c3c1c89089a6cec252670de00f63c310774', 'input_faces': 120, 'input_vertices': 98, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.37612414360046387, -0.35407131910324097, -0.40469643473625183], [0.26100456714630127, 0.14771205186843872, 0.32302215695381165]]}
GEOMETRY_BASE85 = 'c$}qJ3s6<p6}^Z8f`~ql62#`J<r_dmRG>zlRzL+TDvBgpcoD29Mg(h7iC$Yx{X}C_+QdoV8Jj2we&W-J_<1o#3dRpc1J2m;YCD~bZ7oStQ>)S5v-YCJPCL_S-^`x1&N}<<yU#xRo_irX!@YNaCcmNDd%5+y4)@hGW&N}OZADSp^5XeL<*_f8u5{A|Kv%zR+&OJlR(777wnAGSURYE<zbrgi4<EN6F+5riU$C@nd716S{H0}uMM_Vzm6R8mdig?IX^}aONJ@;>M@2^KFX{j5&s*iN*wS&<1m~mF3kqGmKXjy+XnZlRU5&My#v$OrkRwXhR%d;x#s!^!xCZ@$++*;si4xu6{gFcJj1jHSCpX@J->G}MF%ErL56qt;`nE@H3iTo07oq#;(DhCCKS8{omL5@POjvat{*R*fDzty`IpS**Q=uEdwYa~rsk0fnEgrfn(GJ~y`wrHnmED)TJ2stAV`pf|LEQHT$3#yOf8%9WJ#g6)(H%jD;Wyv^0<dcOHSyclgt))<Yyciiz<P|Z^!L@+o_FRr#?2S5B9BiCKg7Cx^V{IxxeU6|QFT&{tx<E%Ltl|Ddc42XCo4((^S53>K0!^VF~0NHbHK0PxZJZ2dhOz?(BJC3)H6?Oe$2bj*Tj5`IKCUOPWy%3692?N=thY@>SL^kI10b8{?K*S$GOGQ41Kz@1^(-^C7+t$Gr*L`GXMN~ti!o#(KYC`=b#sCbe@y`Y85@lA^w?P<Guwyua^8uH$u1XGo*ggr;7jSbkT=4B95zngXqij=ALzM&3;AJl~#YDr>@;97QJs2bS-8b`ao|UCi<l7=ws(!_TawStXWr}kKF-X8+I0X+Pl_Cojun>w|B?ibLbNE^Cc3evRd-&+9dw3Rh&mYduN_iW7nEc(N8s?Ka33_4#card;&dU33TnT<pb>F79Yvy&o<Hbu55%pe3#U5ZI<X2#}TJs&zDjkd#u!5-@g`lwLTENI#~3^YV@IVNh<nI%W;ElymCtV*l3YFbFQ4lcxbs3<Di?rkmsxUG_KoUyASIf{G8;!<G^Y0zbNsK+GKx?vEqNjQj7J@94-D2!<wK+#G^m;IE(Dd?25zC`;K`B@ltX{uhT^TmG|2Ut$PiLlUOh3SKxX(*8A2G(H-*+$@M-bao<<(;T+U@e|!Kq=kY4^;g1rp!@o2g`Dyp^-o(DQ+?9O}*@1Ox4;D8d&+1nt&aE-;B7Wt8qv)&gF7~<Q9jX6smt)_X=E^x+--W!5#4bFiu7!c(?=^Ba=G(So-<=UW2drOJ$$Ec@`dHhyh`xR2PQ*$64CjK;xK{Qn!t*uwZ~YVE7%P{``Dy%SBlKRCb?B3p@5_3ve(Mm&*B|@r+VZ=b@;q*N3Hr#T=zs0;A~_$m)s@g=JkW>w{uG=?THMcm2;E~6-V@H-fpYE#S-0Z)^sZy5f7~(2zr$LE{2D$--|ADUBp*k^8^9N)q0X*t?@65}{RI1=Wkzqte(iF|zHI*6UOW$(9e560SKB213sE@#>~m}7T*|p7^_jK?x^W`~{(4cp-1qGh`;d3{`{hm^>l|O(Q@0Kt%06$0ZUk+R_;V5@PQ7m(@bdepk1=CktJJ+v-Ydyj(CwEJ<h*I!iM}yB=i|L)pIRezZqGy=tpV|J4m7p3Anvo3jnbzMInSM)QisoKpu5t>%k#ajQ0kWZy1Z{XA4;6Cr=<=-=b-B=y|91I$Z+Y;_Lt>7=NP^n>rQ<g?`LD`99*ycc#-VyRWB#}Pv1iSS$DpP^T8Qt!+Y7dy!j(w@dK>SSus=2JO5&tpOGr@D#l%sKKM#>ztK{Um6POoyFEeHUD6Nlor2$&$#rM$OJDE$QqGy01mvZ;9h398E)Cx?#__v#@?1^9Icmf&lsHL$l>9OssE5(74RMS!4^F0JKk>Dfbg^il?qQb7w7%xo-U3^XPdz27UpM~yPrc%V|LRk3WPIHJ`K{+2Xy(x0v;d+nd4y?$O$#LUCl8=c5Ya*&L>@y7CyyadA&w_cA)i5<MLvT(kN7-!9{D_C0r?!$o-^&c#BB1prsZ=!pL2?T&omq7ZJe9SSOuIf;GE(kOnZj)c!sr5{5z&i<ora=jo`hrIiJlr#h*59xM?B8q2wXtLx|rZA3`2Uj3$pHk0XvGk0T#Nj3*yOZY4fTZY576rjn<TXAq~5XOK@LP9;~ENv<%9T>T~EWm+%O!c2=bEy}b3n)(w+(?V&A52Gor(-imA<fqV$*pJ+eyf<+Gd2e!Wn&Q4R#Vy28atnEPZz>!|3?&a`e&cA0f19Rw5>Y4Dxz;3_;$w)h<YUMaXt6!^E0+5i%i4ACui|R|RWGT&`KD?9#HWZM<O+w7KSdr)j3kd_%wU@0gNRY&QC!a;q9^$va`ztl<WB5G?oQr^=tbU#d?3-E+@HA)q$%!43?>iez5R&p<nD~?#~eI(&%Q(-q6fJT`8P~UHf^$LiNtjBMDo!z#V43Ho0vmPC(j|DNmD$RIGH?`d^%0>NyKDwg=5LHGu(Owxc{erCH(Ves0ZSSe=Pj#l~2BwdR}?g9RA}am7USYLpHIOw#>vS>S@vb4pQ86=l'

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
