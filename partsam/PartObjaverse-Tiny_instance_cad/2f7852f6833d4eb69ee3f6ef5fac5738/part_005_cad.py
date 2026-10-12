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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2f7852f6833d4eb69ee3f6ef5fac5738/part_005.stl', 'relative_path': '2f7852f6833d4eb69ee3f6ef5fac5738/part_005.stl', 'source_sha256': '51b03856460ff2fe80c975b93d875d68cdc9d431e2516efb27d2001eabbdb9ae', 'input_faces': 78, 'input_vertices': 71, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.22977003455162048, -0.11690536141395569, -0.05318529158830643], [0.04111727327108383, 0.4551449418067932, 0.15310515463352203]]}
GEOMETRY_BASE85 = 'c$}q{3s6*57{|}DEaC&gXDBFFNkCapQ4kd4u9(hbDbbKwW3nTQVkWi_zU8W9rfE6m=uD}okSIP7s{x-EEejusW<E-D#~eqCoXnYO=y}fn`><VxW}3P)|M~y#kMDlx+{3x|ZpK)ve-}YVZ;`$r(HYZ52&E39izsrr3-hM93gTzZnrjgu;Oc1hwd1m$%$R5qMPhz*j;mmbJ9?NFotm2*ZP%i6^WBAR=gi6Z?i`omqn$GfT#^?|bIx+f^O&K7?AqXdc5R{dUypWj3TBVIGe^~2o=-ifTz4+7Op|Ubzk5oZ8{geI1W$7BS6obO02l734x@g$XAkOAYN>u!3Am?m_72ofe}njv@2URdty@w5;&kfsP1z3R=BpETDsEn%M*Po_mAEeR*gJ~r6C#OMSu4;da0cdM^#AoF`2E6Ns1NV31moWAOZ@ae1O02P8^O!w)}!v~xqX=Dvqjb57bby=x*^qYvtT#+r$rE7F?%iQYui;}KAV2|6g;<L1Nz_lc|H1+PbU7%j4jHwrWL3+M<f%Ux3o-oc4kcl`uyPe1UzfOe)K7}?FHXbNj%X0I_5iRdpY`NB@nk)t%HBP{XNWcU*ZY6--YEE_fiqfKQ8|mczg-nXVBDAs(+yleDj<u;MH@fekE~z5%JRFbHK%${lU$)uYHO6jj`dr#A4#&{xa~=VZ@D$pG@$N9>0pZ8;*U-J-6$QqJMqJC9KQkz1VO1E#l%fabsK+xOQ#+5!6pArg=7W9IrgPdmgwEwhH44bLlAbUp#?$$5mf}FPNQ)ams(B{TCaC{vu|j8}nVai1zoXNc7jcp09;B-N5r;KJhl)@A%Zi@SDu@iJJ$Ai#wx<*EL+F{p|oZzMWT#{?|`j#Cd3+L#Ve9*AEcayAjut%RfY))x{SuKg-&KxGr(j2ed!WHelRcC2P=U(3bbn$Nt&pICt2w&yD1Uy%;w&9R1DWnI?EQ;=)N>oFrbl<}A3$^~P%Ao<2kIyqTFPmr=K}$%l)xhp}#^E4>caxs$++zL&o6?$gZm`o>ndx%efFtKHvl+=ow~agA&m*Ki~fcU;CgXqH!YdvksD9dI%K-m;_K^-F8cqptC0jd#5f@jJNZkAyuweePbw`U}rA-G}dQ0?)oueZ;5F0J`7i^?blfj?n*i+pTTh^AS7WqW#umc%=_NN9$>X@On0no0~=ZFeqWCcfE1if_<*9f3Cut>!H1`;rhVej$yt}Z!B%?|Eq6%x3sl=BF>B{Olxi5=H#qOYvs8xHfz|AEuSN!F>VviTR!jEBg$~z;(cOf2H`#D^Zv>3`O5BCe!5MJzkGtF+RCqNuG9My>rZ9P-ufptZ^*y<#3ujmPi&N&LztS6RJ2qAXXS~UV>m~#R30J~D%De}D|<NSuAIYIDo1dC)oU<I<s|k9&Pkk8*uy!ea301|IhDO9=Ty!kSSt5o59Qp8b9eSWoV#<5WFO8slJlcd{iXWy8YJ`iQ1&R!QM@)P50V-vrS?fY`vCTVoa5PJxjvTv7Ry}aN2D~V9xRo+u~dGTrD6LC5yx(4*Enn3%g$1{pOh};V5U5sa~%6f_H@o8IX}iyc{EGqQS1)RYO7lX9m@SUE4OeCky5|++DqA_0;C?2>df9rN<Cs7g?gw+DhIK5;@pYrgV+N&2XPK$1@OH5Ia}FnoUNSwST>%kg|qsF+<`rq-NxC*V+Zp+1@nCcGjH#8Z|zx~c@081w_|nY>oUe#{JL2G>8JePhk*t4{$bzpO5fL$_m#P_*MpZ;##mbb{geE}%hK!BEX7}GV~42'

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
