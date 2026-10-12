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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/77d56cc994f94d8280c38009688e7413/part_004.stl', 'relative_path': '77d56cc994f94d8280c38009688e7413/part_004.stl', 'source_sha256': 'fdcfda28d29b2a63b53a7772e14175e1e8852496f8657be541a43349e456b8cb', 'input_faces': 144, 'input_vertices': 121, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4999999403953552, -0.30938827991485596, -0.1931217610836029], [0.4999999701976776, 0.3962821960449219, -0.150943785905838]]}
GEOMETRY_BASE85 = 'c$}q}d2AF_9LJ}$SdLO_St`mkrQjA>irpTZvI9a3ER-z@NIANt-BJ!qX=~LWaYDTQG8`dFVz5AiCPu`>p#EW)L`y*sXbUULp$(ylCQ^bTr&`~8^ZiZVJTWo4$;<aM-@bkG-8b)=hJx`49?kxwYdeeIE<M*@(|AeJJX%Afwth`{q%Nzv=A}3-Mfm(fx}#{({Ls=ktwG!5t%%f>*Lo-G-l>%ny*}MrxuLecwye5zLv2Nb`vqm|>mtmrt17FBu<Oihf3{E08ROG8>;Li7k43P$yMH*$H0)_U72wzYwwA-fzXQL;_VtBd3IES8gs<(~*T#Lrf2hUnH?_(28}D^}&(++WaMrGWu;qR})i-W#y(HS%-xcM)=0DJKKcDJ{Z)6DH`g-#b(O%x?M}^)PDSUn4Hj&@RxBbRnuU-`XcO#CA@8unG`PTMik>AXR|I5LPa{C(kNA-<y9~_bWj?_)A{#1P}%dT%-e_8lu^x8La`>IdvJO1{Yt*+;#_|$&*dRX|4S2mus`{&c6vTyAAtljP(+qbUWz94d5PCV(#qxeo9_|`jH+Ff}RpYoVp?+f4jFnCTL52{bkSL=FH_}Z<?({g^t-`#me&foEKp70xg8+cmIulkgqeCypEXXN~<@8tif<h<y=yVF|bJmi~uzC0`EY5Z}t@U7cXS02@O#t-@LEjsHOKZ;Lz^v=SV@DHTLT>aKL%jG-s^ztX?M9$xjx60$6d~4s_s676|mv`Cz-I7*0zv@$d$KMlk<yU>mubqD*D)iv;m|R~!|GMz4kC(W9ml<0peB%$TO`h-JSXlVxy|>&s72nAT-`YDM>dLA3&OD-an#`#Ee0%O2klHt;c4Xg@?i-NWH*(zd$v0`dvEM7Mn_jX1j{A1RUbXX~->4mp^;<ydHzOVED(nA%^t>pi>Qhd~$Md50RiAP;vhfp;#+5<qCwv-L+63FzIt%RQO5+yev*Svk%cuM%8~*`mzEFPEr~HnO`9k?spYn&<{N>j)uQkkH@@ZaMv`(`1fnU>lLU~l5@{mvK3FT3J%A>ROP4pMmJ<8+wSobIoUq8k76TWR1?Pm9^tFmv<JR+agTfb7D)@SrTU(fk9t^cO9&da_f?F*t^tpCpMReV$0r$oPDpK|&iKJ8OZ|Fiv0d>{LxDeZ%@Z%O;6@UcHSc@*Cn&uqUI_oH)#w2#ZaHO^h1_IGMu^__Xm&Kvxi&LK2k$ft7%&6hAc&xq^h9rn7JPv@MBOLF_PKIrVcB<gopx7p*tK1Zp(iSa<bvHz;Q-uRXJICnYok)7W}y<4wgU&HuOd}`nE>Aa`br}JTY&pA`nyAV7fw?lr%g*hke`}UkaMb4dj?epi~eEVGLw9n4BqF(c{Bd+%0>z-q$<oX@#oGk9!-0T_;<U95Ga}T-R3O?Feb;n3#e`2LCdn>3clU@n9$v>p`e<fIx`|n-}a&!OhD*^uvg{(Y<!Z`??4-SHhp-aHU;APMi;AP+l3g^|(GVp3}6|@{&1+Ijag1IgQSAv&A7l4<87eeQN7lP+Or-SE#XF?}~XM(3f^T1QV6QEh(3E;8N$G~I38BiUZ0Uib&3?2p^1Wg4G0{2JZ+!vY*?hEb%O#=4;_k*T@xu${pfj!XSU=MgGbQE|fcqG&Z9tnP&6+biw>I3WOi*yvuUT7BB3my;61CIyiLnnjt!Be2q!BfC9pmV@8z;mGsz;nSN=u&V9Tmmfxmw?02a&Q=20WAYpfLB3RfLDQ6LYIJ7f}e%X2Xid~^FDk8{i=fpLkEHfgHxdof>XiC&;j6Na1!((a1uBL`Y<>JoCX~MP6H2zjs_10kAjW^j{^Jf8w>F}i@>v?0q|_F0i6goz>}ak;7Q<Is1NMJeK|kP${JRlLE*d>`W$#IxEfjut_E*}z5w0`ejbH$1N22O*E(<mxE{IzTo0~+t^?PA*FzV9*Mk>BXMq=k3!qPe3&7K$Pk^U^v!P?a+2Bm*qu@;N5a<KoA>c%40yq)e8`=xp8ypYS!13TXRzktJUY_`W`j=eK$K;h=|DaR9>E5>GZ>F(^oJ~9w?9H>YK)u9+-Nt8>_7^kV5F`'

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
