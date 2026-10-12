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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d1a5633cfa0740d59bce4d3ea051329d/part_011.stl', 'relative_path': 'd1a5633cfa0740d59bce4d3ea051329d/part_011.stl', 'source_sha256': '73555101fe47b038a42ed8c7e7a98754c371aa000478b0f8b69e96e614bebb2c', 'input_faces': 248, 'input_vertices': 138, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.20739977061748505, -0.3695532977581024, -0.20530658960342407], [0.20739972591400146, -0.08609616756439209, 0.49890124797821045]]}
GEOMETRY_BASE85 = 'c$}q~32YSC8OO&qmkAhB8;2u-B^VZiA>oWm0j~=I%3`xMS7NR;W&zV+8(-mOxC2cEv@}sG(YgWBfZGxhuu?9s4A_Py0)-r{ni{96Q6ZvH4@Ipvg3f#IH}<^oB1P>=pZ>r7&ztwY_vV|~H`;(du0xWcJ_8Nkp8UGv?uH?vn~`Kxgi6W^@<XK~3yass7(JygKDPcSdtO%H`52?Z*yvpzD$OtPPVjgqu1NQ$dAuu%O3F&|3YQj@EDs5PTHXt#A<Hjal~)|Hz7HKWCOyqFCN<5o+4Dbsx>_j&6JNeoV`-(a@utwGtnNo^qWIyM(XVG%YQD1lsyrT=^s!LS-Si_hQGE08;$xzH)6jzrvftX*r5`L>_gYO9-yC%KsAyklZmV;S>v?bAg_>x-_wYs8|B1>gT0Ykoov(@Jrxsn1`Cq(w**UJSlmA>z6h9bTd|u|$l6X;DhdUEh9xlH!xvoyM4}aBsUK=-Qk<6o=pV@px=0E0xbIx%qz57)jZhvlX**^U5+h=6Hc_(Ea=7W2;gzx)u82+!NZ+!Ki#%O-{{(0Fx{IB;<Yks6fwQv60oAUhnzu!>p&&l?|=DW&Y(Y4y?8=vJ!-&c1@w)aJT*XZ<(g4$}QAN+H+-v0i}x17G+-njn*mFK5jrSGY$mhFwmyNyoYEcmk8=^G8TRoeCX$*Zz1n^u{+U*Nqa=R5!83FmcbsyQU<GCZSL_xGn<mE+!<aa^mPyKmP^ZHm|Y;Mpk+vVPteaLhTbxoNt(uUvlc_zjs)c&h)XbKJ@YlVtvGKb%%C^D(aNJK`MI_~9&>e>=bCLz$0JI&Yu!*VbQC>vpx#>DzT>M9yk{IIyi&9&f2qe%UzXuf1|j)z3dQ->xfP<S%-A`te0RRDR&cru<$soP4fmey}K2`ex({&2P)|9lf79{VvIIT7DJPHzFUYI`@~G&OFV?XUfk^uE@~*M(KMp<}1J8l&X)&ZO!-PHeXir`dIpA&MWKX`1!q5eMH`O`HA(a|0d1%1?RAC*B|14qVA)>N78Rv>2Gk3>-Nn^v*w2vW?s?mN0)C#elPt>|L42ZeAWGBuaE5;tN)>%11-N*>z3``ouOUd8!msV@>`CnesYHIk?Y5OZTI8$TgSz>>&=LSqxxp#u9{a_)qXwyX3e+rx9i+j^11YVbNXCTb^e;_|DBEpGPL?p&l%sjkn&sWwnjad&Xyn0=XEZsZ|7tCcAbYKcT`<n*mXd^z8^fq|5Wqa>g~GAPpo&=kL}xaWzWm)`yzkP{I>dOc!<w^eX;zY^M0|fW2@hKfBjMO?fb}#+*Ip)b>9&=U)S@kozL?vIK?mb5$@-w+qa*e<}U}xeTw_}?Dp;Fb1-4}ap$<<RX#bcd1{pAn=7m3dRM-9@Pu<*-{gVncckHv=6fc+D(6*syH@(X^6$%aFshQ(@8E(%RZ?qHqWiI#mz;jnUyoKf^Y`^mk@*`F-q8G}<e#eF$G|7jH~#dN){p0B9pBXIndiLi+xM64n?KKzzWw|DFyDA^=9bg9fA`((TlWLBul&Uw<=20q`hRd+_wD@&zUS0?r=9g?MC#Oi{np?!x_?>K+uNzSe}A{ypH$z&KgmAow94Pwr#Y{?y?<-xvw!ng`#|lwvp;O-vp@7%`%LHcviF~E-`;<EtbMF=Tzh}(_U-*`*xDy+<FbEl=d*wIS^IG3xc2_MozMO}Z0+;4aoPX7eS7~OwB94Mae2RR`}X^VVZEnl_00Q=+n4Vz0qt$=v3EPq^>nj_up-`iTU(LmcvTao_}Ci#Rjpv`*LqbOJ@)^8RZF#U7-Yp_Lhv&5QFs}=o)EkheFWYL??OAmyWpK@2Y4sE1?>uNf!CouVWCgL>)?Ds@FGI+P%8#ok!QsKv;ZCecSkqFLU+L3;m+t@xHBAsz68g>2D;s7`v~rYZh||(-3Y<`(bcffAlx5Lv0}FsCjD)PH=!HgP4H?o1h0mJ=n^;xr=UaN6u3X?apdD6ccBT6xg;<@p<NvF?ZSEpjdiR~EbAvU&as|xthdm3$NCHIj`lFxu9x5e=s=_GS_>YGdf~xv9=a6HgA35*Z~?p--3V`ncc9zg9q?Xs54;zC3Ed3~-42WUVhi4G*hJUCCcFX7hd00>bP*ham!L!8CGZgRNq7kCL3_d;I05YnC%|3M4saJZ7VQYf!g1&$a2y<uJ_^UfJ<vgL4|pJ&3J-+6=wjFlFGZKZOX20{dU!d!5#0)Jgtwu);BD|8bSJ!%Ybkh+6?3ilCOQHBt`#{P&*7NhNmfke_+*X={+1OJt(b?-hv&fy(C1)#j5+WmM?d1640HjUZN+RWvd{qhtQFHZK8<79920GxMn}QJtQcX%baVzRj*q5|;BkB($vMN}5quZN$IwRbSiV0++cbD2-^b9#kIsUpS}}$8Q#dD$W1`JW^gFQ7Z#y`X@AjOZC9;@T7IT_T*lX}Kxep^oljmr19q!0G4fVrzepAtz@Jw>C=ak8Oggya31&>5~!9pL0N5b~?8Nsz3fiGCpov6QO2*Kmg39zWQiST$h9reNK@Iv%Ccp;pN&WGpIS1vjM7CINsg`Y=r;2d%l`~o_g5F9|CfdlX;Lhv|rJUpH`*fl707Mc#HGatK-gswps!fW6%G#Ab#r!q(0WrW~DbT&Mj>r;q64j00`3BieIFE|nIgFXTGfs4^hIFtDlqif(|xEw8m%gCdgHf!lyXg|kT{m4aVk|Vbyau?bc7X1~`=UV!$K+EBB+Ej2(U(V}`U&vVE{KwEz2UqaD6n+scf`yjA;+${LUq3hrO@@;hJBf4qa(-Wq3I3iHE3H_Cu7CsnnAoJahy4}Q_A$k#N&92SeWw0e;ym*=R$r|zDFJ^+v0t-(q+{h`#EUGA{{pmYr)U'

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
