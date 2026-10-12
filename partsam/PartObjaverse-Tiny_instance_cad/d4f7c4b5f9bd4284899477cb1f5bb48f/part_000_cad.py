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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d4f7c4b5f9bd4284899477cb1f5bb48f/part_000.stl', 'relative_path': 'd4f7c4b5f9bd4284899477cb1f5bb48f/part_000.stl', 'source_sha256': '2a68b7d921d0834e0a6a1763e2f8d6212f69229c829c216f18e40376f74be9f0', 'input_faces': 118, 'input_vertices': 105, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.048178501427173615, -0.10449540615081787, -0.12314577400684357], [0.04392911493778229, 0.09351441264152527, 0.4999995827674866]]}
GEOMETRY_BASE85 = 'c$}q}e@vBC7{_0J253k|kb?M1;YB5W2?{E3Nx=k_n}kAI-V5BTCMsPRtJHcojX~6~`6GYLUdtTb)~q!{`$KQ7t<9}PYt1l+cg;<g*8Hy@CUwra-}8Fj2ijV_?AiBozW2G$eeSvEea{)L+NkJcEqu+;e)@Uyjm88`<1tZ7*1Ej@&P^@ej@+&7FGgrd!snONy(=45xSArgE^WJ`)!WhHcP!8yi+m-H9NppD=I``-wyxjiZ}oD&+SAtIWq!v-PrH|mvkUTzbM(2ha`c`0f4q1X&dY&;3%r*}w?7d2$B!cwiXTc0`{tkBSGjL|Unu-w(vpwVeCpGD<L;VMqTcWJd^dap`TDn)PYQp^j*r#))Hg}K^VanfYJKVJ@MV4DVnB@b8N1Ke`X|0g@{J!ZnYR9kFYAZSe|}tyvzHI5^{H=?eDg^EVYR;W-SDmcJq<@i-P|wE+WIHHN%D<dr}x?Vhwp?h>pLrp#n@SR<(zFj5Z@&EroV2FT3`AGeCzjJ{9KQi=Y;n6Mg2nEe?jp>@nPSnKf71W58n8!myd%lbze~PwO_)%)?=(z^WCQoz9anY_Ixt{->~P0{J(uTUcS)*{{@o&THK)co;1HN>}&0$pZ?onzuf+P4fuvD{C$H91KlFOxaU)K{;4nLU;5fN<$db>OWzy{`*Qx>UpYJ?e_qg5pZX@rcV0_<SLo<pc7NC**1tY_$L1UOT<z|F&DSrE^oHvnvgd#Ka<AIIRUf{!J_j4!;{Lc+XY0opXxlE{_uc60>gPHGw}h_^o$pgWR}19qs2FFSsW0b2`gES9Pv==X*Y--qIO|;cbe&6|u5;<rbuN9n&ZSS+x%IhZolBptb1R>$b1R>$bE_Y+&aHg1&Yg!+`o*|w`kU(Sr5!mSe0OL69`*MM9{xo5^tnWR>%M?bpG(rG&!y1jzPE&SZ`-f-6WnrB_`%&*_o@BpTPGY8{gUS}^{sshK79^Lf6Q~Zr|+0}{aD@+wI8GRj_}<_Pan3;Pw$+!#p`6>p}sXg@aeuIeY)@HUuTK+<h+u4+;)ErZ3(ZlE7wi6A7kiM;g8v8iEr&w@W<@4#Fza9FIAlo{;kya)PD5g{bB#+uP1E%44)A`Jy%fQ>IXhOS4f|pE8HV7Cq-Z6Ttt17<kNGJ^y#_C2<;R;J*P?Ec20BIPNlv#5)<QMHH}9+JC*u8%8`_t{E|BUk#tkhzdMo^l>FZ#>9ec{AB$!d&#>U*H3-g)&}MKWcpY;1_(=rkRnT?dRp8YK&J768YoX2HwO|j_2ljxy(2Za(cmuQ*yaC(-b%R^L>!DAB*Mpm&Pl21j_0W~zdhiP96W|r#rO<icrQl-d9B?ssHq-&04W0>21<wShKpzCBfG0yIfhU6#p%cJ~-~{M>-~@0iGzuIGj)X>lBf%OpM!R=$j)umAqrq{|`@wPGiO>hY6TwN)hrmhTWat!dGWcQWEHKw>@O&2eEJ|3+Wl_W;7r{9XS^~}k7eMpD%TTL^MHP!`)SC+~g4TeGz$MW6;5yWDv8ZLS9QCTe)le6>8e9Wi2F_to$l@^;i&&Jim<F8=PG^z9Vj;8)oDQ7^U8Has#$~7_IRoPi)R&x&aXM;ncCvU}<B!L%J_6QRWU{D$R)Tft45(A#N{lN}OL8X0nW!&W$5=-V&P!M<W|0Mb6r9FlDvJfsQg9kH3%W$%QjAMcOY&5Vr=q^(G>p?wgR`qPA~HGZpZ>LR?=r;Arv9UYzSF+_sP8<$YFV3+t2Rb#L6Pk5d8Whsj?(@Hg+Bm='

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
