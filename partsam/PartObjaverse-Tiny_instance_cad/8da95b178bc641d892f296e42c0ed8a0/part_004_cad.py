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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_004.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_004.stl', 'source_sha256': '82919537edb1f80d9f2c634180aa1604851d986c74cc5a667400ffffebbb9679', 'input_faces': 288, 'input_vertices': 191, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.46064823865890503, -0.08603677153587341, 0.11418110132217407], [-0.4374975562095642, 0.07046964764595032, 0.24307364225387573]]}
GEOMETRY_BASE85 = 'c$}r0dr%eE9mfx%@(8|K;uG;wANW8k;sX`Kje=3}0V+lm6yy<56aoYzYFt}QY7$>)Of(TL)*9dO5shhrUTKCRHMX5}+E|krooP+e=_CKtPNy?X_w0VoX7@m6IxRE5`F{3$&prFw?>(?*uV!Y1c8wPHPn?LZ`{Spj-x5Mrl!z9!#Z@(Bg~iq5HdJm35xp&6{wO`LFnd8}PKc-#o8ya$s|%~*r}^SjN|NIfeDNg}RW(%w8&+3T6%|W=c0qY{vFTTr7E~6S$0HM`CMNijMkV;R`u@kCNVA3D%*~(QkiAR@yDZfo)9_KM%l9u&yJYD<ueP{-fgeoS+3NO<LopYu*W(7>^vr|r_r<lj{rtvTr>uEWy9eEVpaEY@y5*TaX6!L*{(~7eJpCwN>pwUMf5RcqJR&LXwa(6KB;sr56~P+A@_pXx63w<RwCfW0M@^N-LeEW%wtPd&&4hKSo%C;HiQ|?(yZ_HT{*6cH<gx#N@3v>2NA2gW<8*tx5gcXbF!!(Tx<6m#``W^6e{D{S+ZW3J&4X5te|O_W>-@FrgKj_YDgMnnZEoKPPdQ_0uesMf<HKxUyx+IoGhTg;dkUI8{qs2*n_l*gKQ*zwv-!nI+t=q8l_yKA>(crcMfh6(;;ma-t^D<T8u0aeKKH%o`5Z?Kwfo%O{i<~x=|{bOQ^Xa^&+qqBw=dq<vBR48FUM|s{H8Ch`3-%1(=YZ|zBa#DH*3G;r+xLY$B#Y#rnP=vxO2zjH-uR0&4?KMbB{kZ;k0#K`uLp%?^yF_^9Lubzi9bd|Hk~tOV<4J?DZ*P{{ES@4nOX9#l1e2AIuwPtwZBdR*Ty=l)vZ8R=4lJS8uPwf2|6-eWCoBpS5}BdAPz}pU(`t?)C$}xBXz~=yuO|wLbqbt=ZEj>(l>1gLnL&AMNjKe(@*U*XI|dk%iVgdjGljTK^&{(y(&Y@)14owS2^`?3di@Q)Hd%Jb(NS`QvxUAHPHX_#N_B^XU2GcgSCj*Yj6>>iMhjdj6^(J%8ov`72+~U-^3e%GdK(zMlWh19t!MJ-zwk=U*FU<s1wwX>t2Ld?WBht7o1*yRDr4zg-h_`+j_}>Ta9czdvq?oqvyU*WJFr7m35$-M*85Lt3-vyyPGJ!(s3E-0t<A&cD+3_4&o}kRnU9{>6OT59WFM7cHB%rCK?7^AR7}zF*5ntP1z!Z=9{O``7P}_#N(#_#N(#%Gd9Y_#N(#_#N(#YP^1bRO9vgqv~J3KdSNi{ZaL)-yfB)-yfB)-yfB)-yfB)-yfB)-5-sRBD?>dH@x}d-!Hv)+3vrv#WP;{Bk#7leczC5JLgYc2ztiH;ukfyx&6Sx0d~%L8?SrLyTJDSyF|O&ck+MlK(l9lwa?70@{a%2_WI7|7oXU^KEF8o^;*l<`WFFwt$)$}yE<!~Yx#)V_*y>V;NBhX{DU_Z+5OjU_2jSoz>!8P=iuRr7PoKU`x|bzddB~9gq3q}#)&q!e}C8)r>*m!d2q{fUiEi-Usk)@7sDUccQ#%GiYl%1Yx9eT@f)q{q93C%%<fa$cPT%h_Fbcgws^*C`!UBKF~fS^F@6#mbo)N#UrM~?_Wj-aoVEIzlHTm`yV<_~tJmAzzBs>kUuWZuv$o%1ytp>r`h2y1%o~R7YyF6*=d8bnLH1paukAA(Kfpdy%SYdTe&c)hpHBa4?fqvk)8FP9ukA}6e=z&fervq*Yx`Bl*Y>N<c@x;L>hoy(SZDkWdmn4)eQNt#<?H)fXC7^T8~oeX_c~jL%GcMSGhTl#P`<Vfm9MWu<?HLv@wIiRe0?1{=hfDsGhSPVj<2ml$Jf@O<Ll2m%GcJR<Ll2sj;}ojss6Qf=#1B&kCd;iL&w*jo0P9VH>vY#>(CjmKToOg+B$T`>(5#E9iFq)JnnUv>G_tb%dgv(ik>E#6(OQUNrCGtD(eLy9PRuos<Mgy)mKy#l9T`6uc)fc9=4nHEG4-THQ-9P3jH2j1=pb8hil+kbO&4uKacK&pNH$v7vVa13;Ghg1%3hj0W5VJyaBC1x4{+gdUPwi9$trThNW(T*TH4zMz{=qhLT*2J_k#!hKu1s^jWwNE}$gmqm^(ax#v@o*HDs+&>FZ1E<tPIT5>O;B$uLfa4Ec&l3b2%fwz!vxhwZ_O7bd7@@ljKUJd7=>)||jCAtn?3Fn|?a2dJhP?DcUi{Yo?Y_t&0hL@lP@DezSlAMX=!<q16bPc>1UWyjMOW|c`3A_wmj+Vm9;T7mwcm<q`mc!*_ol8kxNJ(CVu7(%E3(!1x0i1!Zgfrl|Xbzl1zH=$bPf?Q7(QG)IeA6k(v(PMf7W^b7*^g$zet0Ij7@i5Ip-bU3cs9BWo(<1Im&0@5dFTpw9y}k-g>%VzJ|+1HN^&Z?2u_7(pbOv`@N_f-&LH3El;o+D<SFP=@Dz9wnhsBblh9dk5}b%W2`9qiQ9nE$o`BATC%_ZYG&qf{CsL9pqjTWNa56d%PKKwU^WkZ53i<?`0)K~+JQPiZhr)5_3^)!Rf=-8rz=P4L@KmxMOi3O@NgjYsf(O9;&?GpCtou=tAEzWoqvPRdxGy>Z?hE%vC&K;Vf#_s-ARL1x!!d9yIt`A6eP{}tLe@S?axZi!+zakaN$!cp!Et2G9?Ie<bTAwRN1}t^NH~m=+zlN74<O%el;lwKaX1tXp(G1bZS@4)1?>xWfxDvp;r?XZm6F_@k{p4?z!C6cXe=B{zK>Cod!W7G9&k9?8}3b};b;^bMRwt67#v1M;b<rvN-p83fCbkdj&_B+a-HF51RTLNgwu04$KN)qk6H3xa^ExSEwiqmN8mTix@6X6_;rr2nRS%+9pyceKQyb!tRJI|@GE8=H|qq)jm*)=`z7z@^^@=`9PcvgN4$TZS?A0;1J`r>zF7@seSikwQ)azt)*kq6j^8xvs#%B8cj3L9|1`XtV|nct%{l~M=J-{5dl`P4<8zF?2-kBg^E*$5k`Hh!^{k8cb9{x*;sPc4HFOj#bp$Lwhta$~n%9od^GMDqH6E7PkKuh|c#q`kX8q8tW=irg^t-Usad0#GAtkv99S2Jt3pc@yXaank&wUp<9F{r^Ze;vXbPRlf4Bnw6A2cg7Bcw}o=zsbz4&VG3)-Rd+KRoE~^gedF-+98E%XtXR%;+Y6|IA;`F4lv^1D`zlH$?aw3I'

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
